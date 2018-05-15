
class NaiveCompletionEngine:
    def getStringIntersection(self, s1, s2):
        s2len = len(s2)
        result = []

        for i, s in enumerate(s1):
            if i < s2len and s1[i] == s2[i]:
                result.append(s)
            else:
                break

        return "".join(result)

    def getIntersectionOfCompletions(self, completions):
        intersection = completions[0]

        for i, command in enumerate(completions):
            if i > 0:
                intersection = self.getStringIntersection(intersection, command)

        return intersection

    """ Returns list of commands with given prefix + shortest substring of all commands.
    """
    def extract(self, listOfAvailableCommands, prefix, ignoreCase=False):
        completions = []
        intersection = ""
        prefix = prefix.strip()

        if prefix == "" or len(listOfAvailableCommands) == 0:
            return completions

        prefixLen = len(prefix)
        stringsAreEqual = lambda s1, s2: s1.lower() == s2.lower() if ignoreCase else s1 == s2
        matchesToCommand = lambda command: prefixLen <= len(command) and stringsAreEqual(prefix, command[:prefixLen])

        for command in listOfAvailableCommands:
            if matchesToCommand(command):
                completions.append(command)

        if len(completions) > 0:
            intersection = self.getIntersectionOfCompletions(completions).strip()

        return (completions, intersection)
