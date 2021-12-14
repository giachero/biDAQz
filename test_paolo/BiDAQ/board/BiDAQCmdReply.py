SUCCESS = 0
WARNING = -1
ERROR = -2

class BiDAQCmdReply:

    def __init__(self, status=ERROR, value=None):

        self.Status = status
        self.Value = value

        self.SUCCESS = SUCCESS
        self.WARNING = WARNING
        self.ERROR = ERROR

    def SetSuccess(self):
        self.Status = SUCCESS

    def SetWarning(self):
        self.Status = WARNING

    def SetError(self):
        self.Status = ERROR
