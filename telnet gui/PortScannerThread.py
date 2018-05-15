import time
import telnetlib
from threading import Thread

class PortScannerThread(Thread):
    def __init__(self, connectionFrame):
        Thread.__init__(self)
        self.connectionFrame = connectionFrame

    def printDebugMessage(self, message):
        frame = self.connectionFrame
        print("{0}: Thread[{1}]; Connection[{2}] {3}".format(
            time.strftime('%d.%m.%y %H:%M:%S'),
            self.name,
            frame.rootFrame.getIndexOfConnectionFrame(frame), message))
    
    def printDebugTerminateMessage(self):
        self.printDebugMessage("Terminated.")

    def printDebugPingMessage(self):
        frame = self.connectionFrame
        (host, port) = frame.getConnectionAttributes()
        self.printDebugMessage("Pinging {0}:{1}...".format(host, port))

    def run(self):
        frame = self.connectionFrame
        (host, port) = frame.getConnectionAttributes()
        index = frame.rootFrame.getIndexOfConnectionFrame(frame)

        frame.rootFrame.refreshTabTitle(index)
        self.printDebugMessage("PortScannerThread::run()")

        while True:
            for i in range(frame.telnetScanPortTimeout):
                if frame.telnet.get() is None:
                    self.printDebugTerminateMessage()
                    break
                time.sleep(1)

            if frame.telnet.get() is None:
                break

            try:
                connection = telnetlib.Telnet(host, port)
                result = connection.read_until(b'\n', 1)
                connection.close()

                self.printDebugPingMessage()

                if result is None or result == "":
                    break
            except Exception as e:
                frame.writeTelnetMsgToConsole(e)
                break

        frame.telnet.disconnect()
        frame.rootFrame.refreshTabTitle(index)
        frame.writeTelnetMsgToConsole("Connection terminated.")
        self.printDebugMessage("PortScannerThread::~run()")
