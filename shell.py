class Shell:
    shells = []
    curIndex = -1
    def __init__(self, id):
        self.id = id
    @classmethod
    def openShell(cls, id):
        Shell.shells.append(Shell(id))
        Shell.curIndex += 1
    @classmethod
    def closeShell(cls):
        if (Shell.curIndex > -1):
            Shell.shells = Shell.shells[:-1]
            Shell.curIndex -= 1
    @classmethod
    def curShell(cls):
        if Shell.curIndex > -1:
            return Shell.shells[Shell.curIndex]
        else:
            return None