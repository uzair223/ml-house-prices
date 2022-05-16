class HTTPException(Exception):
    def __init__(self, code, description, *args, **detail):
        super().__init__(*args)
        self.code = code
        self.description = description
        self.detail = detail

class BadRequest(HTTPException):
    def __init__(self, description="BAD REQUEST", *args, **detail):
        super().__init__(400, description, *args, **detail)
