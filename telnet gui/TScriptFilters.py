import _thread
import re
import os

class Filter(object):
    name = ""
    pattern = ""

    def getWrongSyntaxMsg(self, args):
        return "Wrong syntax of filter '{0}' for args='{1}'.".format(self.name, args)

    def getUsageMsg(self):
        return ""

    def getExceptionMsg(self, args):
        return "{0}\n{1}".format(self.getWrongSyntaxMsg(args), self.getUsageMsg())

    def __call__(self, line):
        return self.function(line)

    def function(self, inputLine):
        return False

    def __repr__(self):
        return "Filter[{0}; pattern='{1}']".format(self.name, self.pattern)

    def applyForLines(self, data, env):
        return data

class FilterGeneric(Filter):
    name = "filter"
    
    def __init__(self, args):
        self.processArgs(args)

    def function(self, inputLine):
        return self.pattern in inputLine
    
    def getUsageMsg(self):
        return "Usage: {0} <pattern>".format(FilterGeneric.name)

    def processArgs(self, args):
        if len(args) != 2:
            raise(Exception(self.getExceptionMsg(args)))

        self.pattern = args[-1]

        if (self.pattern[0], self.pattern[-1]) == ("'", "'"):
            self.pattern = self.pattern.strip("'")

    def applyForLines(self, listOfLines, env):
        return list(filter(self.function, listOfLines))

class FilterGrep(Filter):
    sym_quote = "'"
    name = "grep"
    
    def __init__(self, args):
        self.clipInputToMatchedText = False
        self.invertMatch = False
        self.processArgs(args)

    def function(self, inputLine):
        finalResult = False

        if self.clipInputToMatchedText:
            return list(map(lambda line: line + "\n", re.findall(self.pattern, inputLine)))
        else:
            matchObject = re.search(self.pattern, inputLine)
            finalResult = matchObject is not None

        return finalResult if not self.invertMatch else finalResult

    def getUsageMsg(self):
        options = [
            "Options:",
            " -o: Print only matched part of text.",
            " -v: Invert match (select non-matching lines)."
        ]
        usage = "Usage: {0} [-o] '<pattern>'".format(FilterGrep.name)

        return "{0}\n{1}".format(usage, "\n".join(options))

    def processArgs(self, args):
        if len(args) < 2:
            raise(Exception(self.getExceptionMsg(args)))

        if "-o" in args:
            self.clipInputToMatchedText = True
        if "-v" in args:
            self.invertMatch = True

        pattern = args[-1]
        if (len(pattern) >= 2) and (pattern[0] == self.sym_quote) and (pattern[0] == pattern[-1]):
            self.pattern = pattern.strip(self.sym_quote)
        else:
            self.pattern = pattern

    def applyForLines(self, listOfLines, env):
        if self.clipInputToMatchedText:
            result = []
            for line in listOfLines:
                filterResult = self.function(line)
                if filterResult:
                    result = result + filterResult
            return result
        else:
            return list(filter(self.function, listOfLines))

class FilterHead(Filter):
    name = "head"

    def __init__(self, args):
        self.numberOfLines = 5
        self.processArgs(args)

    def processArgs(self, args):
        if len(args) == 0:
            raise(Exception(self.getExceptionMsg(args)))

        if "-n" in args:
            argIndex = args.index("-n")

            if argIndex + 1 == len(args):
                raise(Exception(self.getExceptionMsg(args)))

            self.numberOfLines = int(args[argIndex + 1])

    def getUsageMsgBase(filterClass):
        options = [
            "Options:",
            " -n <number>: Print {0} <number> lines of text.".format("first" if filterClass is FilterHead else "last"),
        ]
        usage = "Usage: {0} [-n]".format(filterClass.name)

        return "{0}\n{1}".format(usage, "\n".join(options))
    
    def getUsageMsg(self):
        return FilterHead.getUsageMsgBase(FilterHead)

    def applyForLines(self, listOfLines, env):
        return listOfLines[0:self.numberOfLines] if len(listOfLines) > self.numberOfLines else listOfLines

class FilterTail(FilterHead):
    name = "tail"

    def getUsageMsg(self):
        return FilterHead.getUsageMsgBase(FilterTail)

    def applyForLines(self, listOfLines, env):
        return listOfLines[-self.numberOfLines:] if len(listOfLines) > self.numberOfLines else listOfLines

class FilterWc(Filter):
    name = "wc"

    def __init__(self, args):
        self.countLinesEnabled = False
        self.countCharsEnabled = False
        self.processArgs(args)

    def processArgs(self, args):
        if len(args) == 0:
            raise(Exception(self.getExceptionMsg(args)))

        if "-l" in args:
            self.countLinesEnabled = True
        if "-m" in args:
            self.countCharsEnabled = True

    def getUsageMsg(self):
        options = [
            "Options:",
            " -l: Return number of lines.",
            " -m: Return number of characters.",
        ]
        usage = "Usage: {0} [-n]".format(FilterWc.name)

        return "{0}\n{1}".format(usage, "\n".join(options))

    def buildResultList(self, number):
        return ["{0}\n".format(number)]

    def countWords(self, lines):
        numberOfWords = 0
        for line in lines:
            numberOfWords = numberOfWords + len(re.findall("\w+", line))
        return self.buildResultList(numberOfWords)

    def countChars(self, lines):
        numberOfChars = sum([len(line) for line in listOfLines])
        return self.buildResultList(numberOfChars)

    def countLines(self, lines):
        return self.buildResultList(len(lines))

    def applyForLines(self, listOfLines, env):
        if self.countLinesEnabled:
            return self.countLines(listOfLines)
        elif self.countCharsEnabled:
            return self.countChars(listOfLines)
        else:
            return self.countWords(listOfLines)

class FilterSort(Filter):
    name = "sort"

    def __init__(self, args):
        self.processArgs(args)

    def processArgs(self, args):
        if len(args) != 1:
            raise(Exception(self.getExceptionMsg(args)))

    def getUsageMsg(self):
        return "Usage: {0}".format(FilterSort.name)

    def applyForLines(self, listOfLines, env):
        linesCopy = list(listOfLines)
        linesCopy.sort()
        return linesCopy

class FilterEdit(Filter):
    name = "edit"

    def __init__(self, args):
        self.processArgs(args)

    def processArgs(self, args):
        if len(args) != 1:
            raise(Exception(self.getExceptionMsg(args)))

    def getUsageMsg(self):
        return "Usage: {0}".format(FilterSort.name)

    def showOutputInEditor(self, lines, env):
        editor = env.getVar("editor")
        tmpFile = "telnetGuiOutput_{0}.log".format(env.getUniqueTitle())
        editorCommand = "{0} {1}".format(editor, tmpFile)
        prefix = "FilterView:applyForLines();"

        print("{0} Saving output to tmp file '{1}'...".format(prefix, tmpFile))

        with open(tmpFile, "w") as f:
            f.write("".join(lines))

        print("{0} Running '{1}'...".format(prefix, editorCommand))
        os.system(editorCommand)

    def applyForLines(self, listOfLines, env):
        try:
            _thread.start_new_thread(lambda: self.showOutputInEditor(listOfLines, env), tuple())
        except Exception as e:
            return ["{0}\n".format(str(e))]

        return [""]
