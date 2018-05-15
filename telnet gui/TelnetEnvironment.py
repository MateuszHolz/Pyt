from collections import OrderedDict
from TScript import *
from time import sleep

from os import listdir
from os.path import isfile, join, abspath
import re

# FIXME: Decouple connectionFrame from environment

def getListOfFiles(directory):
    path = abspath(directory)
    return [f for f in listdir(path) if isfile(join(path, f))]

def includeFileToScope(scope, filename):
    starIndex = filename.find("*")
    directoryToInclude = ""
    filesToInclude = []
    listOfExceptions = []

    if starIndex > 1:
        directoryToInclude = filename[:starIndex - 1]
        filesToInclude = getListOfFiles(directoryToInclude)
    else:
        filesToInclude = [filename]

    print("Files to include: {0}".format(filesToInclude))

    for scriptFile in filesToInclude:
        print(scriptFile)
        scriptPath = join(directoryToInclude, scriptFile)
        print("Trying to include script '{0}...".format(scriptPath))

        try:
            scope.appendScript(scriptPath)
        except Exception as e:
            listOfExceptions.append("In file: {0}\n".format(scriptPath))
            listOfExceptions.append("{0}\n".format(str(e)))

    return listOfExceptions

class TelnetEnvironment(TScriptEnvironment):
    def getCommandNotFoundMsg(self, name):
        return "Unknown function '{0}'.\n".format(name)

    def __init__(self, telnetManager, connectionFrame):
        self.telnet = telnetManager
        self.connectionFrame = connectionFrame
        self.lastCommandSuccess = True
        self.echo = False
        self.echoAllCommands = False
        self.builtinFunctions = OrderedDict([
            ("help",        self.f_help),
            ("print",       self.f_print),
            ("echo",        self.f_echo),
            ("set",         self.f_set),
            ("delay",       self.f_delay),
            ("include",     self.f_include),
        ])
    
    def getUniqueTitle(self):
        safeSymbol = "_"
        correctedTitle = self.connectionFrame.getTitle()
        correctedTitle = re.sub(r"\W", safeSymbol, correctedTitle)
        correctedTitle = re.sub(r"{0}+".format(safeSymbol), lambda obj: safeSymbol, correctedTitle)
        correctedTitle = correctedTitle.strip(safeSymbol)

        return "tab_{0}_{1}".format(self.connectionFrame.getIndex(), correctedTitle)

    def getVar(self, key):
        config = self.connectionFrame.rootFrame.getConfig()
        return config.getGlobalSetting(key)

    def isBuiltinCommand(self, command):
        return command in self.builtinFunctions.keys()
    
    def getCommandForBuiltinFunction(self, function):
        for k, v in self.builtinFunctions.items():
            if v == function:
                return k
        return ""

    def getGlobalScope(self):
        return self.connectionFrame.rootFrame.globalScope

    def getHelpContent(self):
        itemFormat = "\t- {0}\n"
        content = []

        content.append("Filters:\n")
        for filterName in TScriptInstruction.filtersMap.keys():
            content.append(itemFormat.format(filterName))

        content.append("Commands:\n")
        for command in self.builtinFunctions.keys():
            content.append(itemFormat.format(command))

        content.append("Examples:\n")
        content.append(itemFormat.format("> command1 | filter1 arg | filter2 | filter3"))

        return content

    def f_set(self, name, args):
        globalScope = self.getGlobalScope()
        output = ["Functions in global scope:\n"]

        for function in globalScope.getFunctions():
            output.append("{0}\n".format(function.name))

        return output

    def f_echo(self, name, args):
        options = ("on", "off")

        if len(args) < 2 or (args[-1] not in options):
            return [
                "Echo: {0}\n".format(options[0] if self.echo else options[1]),
                "Usage: echo [-a] {0}|{1}\n".format(*options),
                "-a: Echo print commands.\n"
            ]

        if len(args) > 2 and args[1] == "-a":
            self.echoAllCommands = True

        self.echo = (args[-1] == options[0])

        return [""]

    def f_print(self, name, args):
        if len(args) != 2:
            return ["Usage: print '<msg>'\n"]

        arg = args[1].strip("'")

        return ["{0}\n".format(arg)]

    def f_help(self, name, args):
        return self.getHelpContent()

    def f_delay(self, name, args):
        if len(args) != 2:
            return ["Usage: delay '<numberOfSeconds>'\n"]

        try:
            sleep(int(args[1]))
        except Exception as e:
            return [str(e)]

        return [""]

    # FIXME: Move include instruction to base environment?
    def f_include(self, name, args):
        listOfExceptions = [""]

        if len(args) != 2:
            return ["Usage: include '<TScriptFile>'\n"]

        listOfExceptions = includeFileToScope(self.getGlobalScope(), args[1].strip("'"))

        return listOfExceptions
    
    def splitCommandIntoArgv(self, command):
        commandArg = '[;|$A-Za-z0-9_\-.]+'
        quotedString = "'[^']+'"

        return re.findall("{0}|{1}".format(commandArg, quotedString), command)
    
    def echoInstruction(self, instruction):
        argv = self.splitCommandIntoArgv(instruction.command)

        if self.echo:
            isPrint = self.getCommandForBuiltinFunction(self.f_print) == argv[0]
            if not (isPrint and not self.echoAllCommands):
                return "# {0}\n".format(instruction.line)
        return ""

    def execFunction(self, name, args, line):
        print("TelnetEnvironment::execFunction(name='{0}', args='{1}', line='{2}');\n".format(name, args, line))
        self.lastCommandSuccess = True
        argv = self.splitCommandIntoArgv(name)

        if self.connectionFrame.bookmarks.isAlias(argv[0]):
            aliasCommand = self.connectionFrame.bookmarks.getAliasCommand(argv[0])
            return self.execFunction(aliasCommand, [], aliasCommand)
        
        # Check built-in functions:
        if self.isBuiltinCommand(argv[0]):
            return self.builtinFunctions[argv[0]](name, argv)
        
        # Check functions in global scope:
        globalScope = self.getGlobalScope()
        if globalScope.isFunctionName(name):
            return globalScope.getFunctionByName(name).exec(self)

        # Check telnet commands:
        if self.telnet.isConnected():
            result = self.telnet.sendCommand("{0}\r\n".format(name))
            result = [] if result == ["\n"] else result
            self.lastCommandSuccess = not self.telnet.isUnknownCommandResult(result)
            return result
        else:
            self.lastCommandSuccess = False
            return [self.getCommandNotFoundMsg(name)]
