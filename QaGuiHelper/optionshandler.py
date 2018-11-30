import json
import os

class OptionsHandler():
    def __init__(self):
        self.optionsPath = os.path.join(os.getenv('APPDATA'), 'adbgui')
        self.optionsFilePath = os.path.join(self.optionsPath, 'options.json')
        self.optionsCats = ('Screenshots folder', 'Builds folder', 'Jenkins credentials', 'Remove SS from device')
        self.optionsTypes = ('folder', 'folder', 'input', 'checkbox')
        self.__optionsCategories = [(i, j) for i, j in zip(self.optionsCats, self.optionsTypes)]
        self.__options = self.getOptionsIfAlreadyExist()

    def getOptionsIfAlreadyExist(self):
        if os.path.exists(self.optionsPath):
            try:
                with open(self.optionsFilePath, 'r') as f:
                    try:
                        return json.loads(f.read())
                    except json.decoder.JSONDecodeError:
                        return {}
            except FileNotFoundError:
                return {}
        else:
            os.mkdir(self.optionsPath)
            return {}

    def setOption(self, option, value):
        self.__options[option] = value

    def getOption(self, option, type):
        if option not in self.optionsCats:
            assert(False)
        try:
            return self.__options[option]
        except KeyError:
            if type == tuple:
                return ('', '')
            elif type == str:
                return ''
            elif type == bool:
                return False
            else:
                assert(False)

    def saveOptionsToFile(self):
        with open(self.optionsFilePath, 'w+') as f:
            json.dump(self.__options, f)

    def getOptionsCategories(self):
        return self.__optionsCategories