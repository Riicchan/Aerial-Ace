import traceback
import sys
import datetime

class Logger:

    def __init__(self) -> None:
        pass

    @staticmethod
    def logMessage(msg:str) -> None:
        print("{} [Message] : {}".format(datetime.datetime.now(), msg))


    @staticmethod
    def logWarning(msg:str) -> None:
        print("{} [Warning] : {}".format(datetime.datetime.now(), msg))

    @staticmethod
    def logError(error, msg:str=None) -> None:
        print("{} [Error] : ".format(datetime.datetime.now()))
        print(msg)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)