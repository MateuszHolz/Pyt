from parsimonious.grammar import Grammar
from TScriptFilters import *

import parsimonious

class TScriptEnvironment(object):
    def getVar(self, name):
        return None

    def execFunction(self, command, args, line):
        return ""
    
    def echoInstruction(self, instruction):
        return ""
    
class TScriptInstruction(object):
    sym_filter = "|"

    filters = []
    filtersMap = {
        FilterGeneric.name:     FilterGeneric,
        FilterGrep.name:        FilterGrep,
        FilterHead.name:        FilterHead,
        FilterTail.name:        FilterTail,
        FilterWc.name:          FilterWc,
        FilterSort.name:        FilterSort,
        FilterEdit.name:        FilterEdit,
    }

    def __init__(self, strippedLine, lineArgs=None):
        self.line = strippedLine
        self.lineArgs = list(lineArgs)
        self.command = None
        self.filters = None
        self.extractCommandAndFilters()

    def __str__(self):
        return "[Instruction: '{0}'; {1} filters]".format(str(self.command), len(self.filters))

    def isFilterName(name):
        return name in TScriptInstruction.filtersMap.keys()
    
    def buildFilter(self, args):
        if not args:
            raise(Exception("Expected one of filter names: {0}.".format(", ".join(self.filtersMap.keys()))))

        filterName = args[0]

        if not TScriptInstruction.isFilterName(filterName):
            raise(Exception("Unknown filter '{0}'.".format(filterName)))

        return TScriptInstruction.filtersMap[filterName](args)

    # Extracts line into command and list of filters (cmd, f1, f2, f3, ...).
    def extractCommandAndFilters(self):
        parts = self.lineArgs

        if not parts:
            raise(Exception("Instruction '{0}' is empty.".format(self.line)))

        self.filters = []
        self.command = parts[0].strip()
        self.args = list(parts)

        if len(parts) == 1:
            # Command doesn't contain any filters:
            return

        for part in parts[1:]:
            part = part.strip()
            filterArgs = part.split()
            filterObj = self.buildFilter(filterArgs)
            self.filters.append(filterObj)
    
    def applyFilters(self, listOfLines, environment):
        if self.filters is None:
            return listOfLines

        for filterObj in self.filters:
            listOfLines = filterObj.applyForLines(listOfLines, environment)

        return listOfLines
    
    def exec(self, environment):
        output = [environment.echoInstruction(self)]
        output = output + environment.execFunction(self.command, self.args, self.line)
        filteredOutput = self.applyFilters(output, environment)
        return filteredOutput

class TScriptFunction(object):
    def __init__(self, name):
        self.name = name
        self.instructions = []
        self.functions = []
    
    def __iter__(self):
        return iter(self.instructions)

    def getFunctions(self):
        return self.functions
    
    def getFunctionByName(self, name):
        for function in self.functions:
            if function.name == name:
                return function
        return None
    
    def getNumberOfFunctions(self):
        return len(self.functions)

    def getNumberOfInstructions(self):
        return len(self.instructions)

    def getInstructions(self):
        return self.instructions

    def addInstruction(self, strippedLine, listOfArgs):
        self.instructions.append(TScriptInstruction(strippedLine, listOfArgs))

    def addFunction(self, function):
        self.functions.append(function)

    def isFunctionName(self, literal):
        return literal in [f.name for f in self.functions]
    
    def execInstruction(self, environment, instruction):
        output = ""
        print("Executing instruction: '{0}'...".format(instruction.command))

        if self.isFunctionName(instruction):
            function = self.getFunctionByName(instruction.name)
            output = function.exec(environment)
        else:
            output = instruction.exec(environment)

        return output
    
    def exec(self, environment):
        output = []
        print("Executing function: '{0}'...".format(self.name))

        for instruction in self.instructions:
            output = output + self.execInstruction(environment, instruction)

        return output

    def print(self):
        functions = ", ".join([str(function.name) for function in self.functions])
        header = "Function [{0}]: {1} instruction(s); {2} available function(s): {3}".format(
                self.name, len(self.instructions), len(self.functions), functions)
        decoration = len(header) * "-"

        print(decoration)
        print(header)
        for instruction in self.instructions:
            print(instruction)
    
    def appendScript(self, filename):
        function = TScriptScopeBuilder.build(filename)
        self.functions = self.functions + function.getFunctions()
        self.instructions = self.instructions + function.getInstructions()

""" General parser class of TScript.  """
class TScriptEvaluator(parsimonious.NodeVisitor):
    grammarDefinition = r"""
    program             = trash ( commandStripped / instructions ) trash
    instructions        = ( comment / commandLine / function )*
    comment             = spaceOrNewline* t_commentSymbol ~"[^\n]*" newline

    function            = t_function space commandArg space t_begin ( comment / functionCommand )* t_end
    functionCommand     = spaceOrNewline+ commandLine

    commandLine         = space* command
    command             = ( commandStripped / "" ) space* newline
    commandStripped     = commandArg ( space* ( pipe / commandArg / literal ) )*
    commandArg          = ~"[$/A-Za-z0-9_\-.:]+"

    pipe                = "|"
    literal             = ~"'[^']*'"
    trash               = spaceOrNewline*
    spaceOrNewline      = ( space / newline )
    space               = ~"[ \t]"
    newline             = "\n"

    t_commentSymbol     = "#"
    t_function          = "function"
    t_begin             = "{"
    t_end               = "}"
    """

    # Static instance of grammar:
    grammar = Grammar(grammarDefinition)

    def __init__(self, strict=True):
        self._strict = strict
        self.lastLineArgs = []
        self.lastFilterArgs = []

    def onCommandFound(self, strippedCommand, lineArgs):
        pass

    def onFunctionStartFound(self, functionName):
        pass

    def onFunctionEndFound(self):
        pass
    
    def generic_visit(self, node, children):
        if children:
            return children[-1]

    def visit_pipe(self, node, children):
        self.lastLineArgs.append(" ".join(self.lastFilterArgs))
        self.lastFilterArgs = []

    def visit_commandStripped(self, node, children):
        strippedCommand = node.text.strip()

        if strippedCommand:
            self.lastLineArgs.append(" ".join(self.lastFilterArgs))
            self.onCommandFound(strippedCommand, self.lastLineArgs)
            self.lastFilterArgs = []
            self.lastLineArgs = []

    def visit_commandArg(self, node, children):
        self.lastCommandArg = str(node.text)
        self.lastFilterArgs.append(self.lastCommandArg)

    def visit_literal(self, node, children):
        self.lastFilterArgs.append(str(node.text))

    def visit_t_begin(self, node, children):
        self.lastFilterArgs = []
        self.lastLineArgs = []
        self.onFunctionStartFound(self.lastCommandArg)

    def visit_t_end(self, node, children):
        self.onFunctionEndFound()

""" TScript parser class used to parse content from file. """
class TScriptScopeBuilder(TScriptEvaluator):
    def __init__(self):
        TScriptEvaluator.__init__(self)
        self.globalScope = TScriptFunction("main")
        self.currentScope = self.globalScope
        self.functionsStack = []

    def onCommandFound(self, strippedCommand, lineArgs):
        self.currentScope.addInstruction(strippedCommand, lineArgs)

    def onFunctionStartFound(self, functionName):
        self.pushFunction(functionName)

    def onFunctionEndFound(self):
        if self.currentScope != self.globalScope:
            self.popCurrentFunction()
        else:
            raise(Exception("Cannot pop main function from stack."))

    def getGlobalScope(self):
        return self.globalScope

    def pushFunction(self, functionName):
        self.functionsStack.append(functionName)
        newFunction = TScriptFunction(functionName)
        # Note: nested functions are not allowed, functions are added to global scope:
        self.globalScope.addFunction(newFunction)
        self.currentScope = newFunction

    def popCurrentFunction(self):
        if self.functionsStack:
            self.functionsStack.remove(self.functionsStack[-1])
            self.currentScope = self.globalScope
        else:
            raise(Exception("Cannot pop function from empty stack."))

    def printData(self):
        self.globalScope.print()
        for function in self.globalScope.functions:
            function.print()

    def build(filename):
        content = ""

        with open(filename) as f:
            content = f.read()

        parser = TScriptScopeBuilder()
        parser.parse(content)
        parser.printData()

        return parser.getGlobalScope()

""" TScript parser class used to parse single instruction. """
class TScriptCommandParser(TScriptEvaluator):
    def __init__(self):
        TScriptEvaluator.__init__(self)
        self.lastInstruction = None

    def onCommandFound(self, strippedCommand, lineArgs):
        self.lastInstruction = TScriptInstruction(strippedCommand, lineArgs)

    def build(line):
        parser = TScriptCommandParser()
        parser.parse(line)

        return parser.lastInstruction
