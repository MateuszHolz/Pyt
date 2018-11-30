import threading

class ButtonUnlocker():
    def __init__(self, count, btns):
        self.count = count
        self.semph = threading.Semaphore()
        self.buttons = btns
        for i in self.buttons:
            i.Disable()

    def finishThread(self):
        self.semph.acquire()
        try:
            self.count -= 1
            if self.count == 0:
                for i in self.buttons:
                    i.Enable()
        finally:
            self.semph.release()
