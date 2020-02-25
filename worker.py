from PyQt5.QtCore import QRunnable

class Worker(QRunnable):
    '''
    Runnable "worker" used to execute functions on a seperate thread than
    the PyQt event loop
    '''
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            self.func(*self.args, **self.kwargs)
        except Exception as e:
            print(e)
