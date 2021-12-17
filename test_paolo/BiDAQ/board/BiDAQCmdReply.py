SUCCESS = 0
WARNING = -1
ERROR = -2

_StatusToStr = {
    ERROR: 'ERROR',
    WARNING: 'WARNING',
    SUCCESS: 'SUCCESS',
}


class BiDAQCmdReply:

    def __init__(self, status=ERROR, value=None):

        self.Status = status
        self.Value = value

        self.SUCCESS = SUCCESS
        self.WARNING = WARNING
        self.ERROR = ERROR

    def __repr__(self):
        return "BiDAQCmdReply - Status = {}, Value = {}".format(_StatusToStr[self.Status], self.Value)

    def SetSuccess(self):
        self.Status = SUCCESS

    def SetWarning(self):
        self.Status = WARNING

    def SetError(self):
        self.Status = ERROR
