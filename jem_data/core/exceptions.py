class JemException(Exception):
    '''Top-level Jem-Data specific exception'''
    pass

class ModbusExceptionResponse(JemException):
    def __init__(self, response):
        super(ModbusExceptionResponse, self).__init__(str(response))
        self.response = response

class ModbusEmptyResponse(JemException):
    def __init__(self):
        super(ModbusEmptyResponse, self).__init__("No response from server")

class ValidationException(JemException):
    pass

class PersistenceException(JemException):
    pass

def wrap_exception_response(response):
    '''Wrap a given pymodbus ExceptionResponse as a throwable exception.'''
    return ModbusExceptionResponse(response)
