import re
from collections import OrderedDict

class TelnetGuiConfig:
    filePath = ".telnetGuiConfig"

    globalSectionFormat = "Global"
    cmdWidgetSectionFormat = "CommandWidget{0}"
    cmdPatternFormat = "commandPattern{0}"
    tabSectionFormat = "Tab{0}"
    keyValueFormat = "{0} = {1}\n"
    sectionFormat = "[{0}]\n"

    keyValueSeparator = "="
    sectionPattern = re.compile(r'^\[(\w+)\]$')
    keyValuePattern = re.compile(r'^([^{0} ]+)\s*{0}\s*(.*)$'.format(keyValueSeparator))

    rootFrame = None
    content = None

    def __init__(self, rootFrame):
        self.rootFrame = rootFrame
    
    def getFormattedSectionName(self, name):
        return self.sectionFormat.format(name)

    def hasSimpleFormatString(self, string, printfFormat):
        keyPrefix = printfFormat.replace("{0}", "")
        return string.startswith(keyPrefix) and len(string) > len(keyPrefix)
    
    def isCmdWidgetSectionName(self, string):
        return self.hasSimpleFormatString(string, self.cmdWidgetSectionFormat)

    def isTabSectionName(self, string): 
        return self.hasSimpleFormatString(string, self.tabSectionFormat)
    
    def isCmdPatternKey(self, string):
        return self.hasSimpleFormatString(string, self.cmdPatternFormat)
    
    def save(self):
        try:
            with open(self.filePath, "w") as f:
                config = self.getConfig()
                f.write("# vim: set syntax=cfg:\n")
                f.write(config)
            print("[{0}]: Saved {1} lines to config file.\n".format(self.filePath, config.count("\n")))
        except Exception as exception:
            print(exception)
    
    def read(self):
        result = OrderedDict()
        currentSection = None
        contentOfConfig = ""

        try:
            with open(self.filePath, "r") as f:
                contentOfConfig = f.readlines()
            print("[{0}]: Read {1} lines from config file.\n".format(self.filePath, len(contentOfConfig)))
        except FileNotFoundError:
            return
        except Exception as exception:
            print(exception)
            return

        for line in contentOfConfig:
            line = line.strip()

            sectionMatch = self.sectionPattern.search(line)
            settingMatch = self.keyValuePattern.search(line)
            
            if sectionMatch:
                # Found section:
                currentSection = sectionMatch.group(1)

                if currentSection:
                    result[currentSection] = OrderedDict()
            elif settingMatch and currentSection:
                # Found $key = value pair:
                (key, value) = settingMatch.groups()

                if key and value:
                    result[currentSection][key] = value

        return result

    def build(self):
        self.content = self.read()

    def getSetting(self, section, key):
        if self.content and (section in self.content) and (key in self.content[section]):
            return self.content[section][key]
        else:
            return None

    def getGlobalSetting(self, key):
        return self.getSetting(self.globalSectionFormat, key)

    def getTabSetting(self, tabIndex, key):
        return self.getSetting(self.tabSectionFormat.format(tabIndex), key)

    def getSection(self, section):
        return self.content[section]

    def getContent(self):
        return self.content

    def getListOfCommandPatterns(self):
        globalSection = self.getSection(self.globalSectionFormat)
        return [ globalSection[key] for key, value in globalSection.items() if self.isCmdPatternKey(key) ]

    def getGlobalConfig(self):
        patterns = self.getListOfCommandPatterns()
        globalConfig = self.getFormattedSectionName(self.globalSectionFormat)

        for key, (desc, variable, defVal) in self.rootFrame.boolOptions.items():
            globalConfig = globalConfig + self.keyValueFormat.format(key, variable.get())

        for key, (labelFrame, entry) in self.rootFrame.configPanelEntries.items():
            globalConfig = globalConfig + self.keyValueFormat.format(key, entry.get())

        return globalConfig

    def getCmdWidgetSections(self):
        return OrderedDict([(k, v) for (k, v) in self.content.items() if self.isCmdWidgetSectionName(k)])
    
    def getCmdWidgetsConfig(self):
        cmdWidgetSections = self.getCmdWidgetSections()
        result = ""

        for (key, section) in cmdWidgetSections.items():
            result = result + self.getFormattedSectionName(key).format(key)

            for (k, v) in section.items():
                result = result + self.keyValueFormat.format(k, v)

        return result

    def getConfig(self):
        connectionFrames = self.rootFrame.connectionFrames

        result = self.getGlobalConfig() + "\n"
        result = result + self.getCmdWidgetsConfig() + "\n"
        
        for i, connectionFrame in enumerate(connectionFrames):
            tabSection = self.tabSectionFormat.format(i)
            tabConfig = connectionFrame.getConfig()
            result = "{0}\n{1}{2}".format(result, self.getFormattedSectionName(tabSection), tabConfig)
        
        return result
