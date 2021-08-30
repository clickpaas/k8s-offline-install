#!/bin/python


class Error:
    Success = "ok"
    Failed = "failed"
    NotFound = "no_found"

    def __init__(self, code, msg, data):
        self.__code = code
        self.__msg = msg
        self.__data = data

    def set_code(self, code):
        self.__code = code

    def set_msg(self, msg):
        self.__msg = msg

    def set_data(self, data):
        self.__data = data

    def get_code(self):
        return self.__code

    def get_msg(self):
        return self.__msg

    def get_data(self):
        return self.__data

    def wrap_error(self, err):
        assert isinstance(err, Error), "except got Error type, but got {}".format(type(err))
        if self.__code == self.Success and err.__code == self.Success:
            return
        if self.__code == self.Success:
            self.__code = err.__code
            self.__msg = err.__msg
            return
        self.__msg += ", {}".format(err.__msg)
        return self

    @staticmethod
    def new(code, msg, data):
        e = Error(code, msg, data)
        return e

    @staticmethod
    def default_ok():
        e = Error(Error.Success, "", "")
        return e
