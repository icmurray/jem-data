class JemException(Exception):
    '''Top-level Jem-Data specific exception'''
    pass

class JemExceptionResponse(JemException):
    def __init__(self, response):
        super(JemExceptionResponse, self).__init__(str(response))
        self.response = response

def _wrap_exception_response(response):
    '''Wrap a given pymodbus ExceptionResponse as a throwable exception.'''
    return JemExceptionResponse(response)
