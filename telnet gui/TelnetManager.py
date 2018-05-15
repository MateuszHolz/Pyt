import encodings.idna
import telnetlib
import traceback

class TelnetManager(object):
    def __init__(self):
        self.connection = None

    def isConnected(self):
        return self.connection is not None
    
    def get(self):
        return self.connection

    def isUnknownCommandResult(self, receivedLines):
        return receivedLines and len(receivedLines) == 2 and receivedLines[0] == "Unknown command\n"

    def sendCommand(self, command):
        print("TelnetManager::sendCommand({0})".format(command))
        self.connection.write(command.encode("ascii"))
        return self.fetchDataUntilNewLine()

    def connect(self, host, port):
        self.connection = telnetlib.Telnet(host, port)

    def disconnect(self):
        if self.isConnected():
            self.connection.close()
            self.connection = None

    def fetchDataUntilNewLine(self):
        receivedLine = "_"
        data = []
        endOfContentStr = b'\n'
        isAvailableData = lambda data: data and data != b'' and data != endOfContentStr

        while isAvailableData(receivedLine):
            receivedLine = self.connection.read_until(endOfContentStr, 1)
            data.append(receivedLine.rstrip().decode("utf-8") + "\n")

        return data

