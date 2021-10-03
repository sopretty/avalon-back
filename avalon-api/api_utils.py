class HTTPError(Exception):
    """Class HTTPError related to exception"""

    def __init__(self, message, status_code=500, payload=None):
        self.message = message
        self.status_code = status_code
        self.payload = payload
        Exception.__init__(self, message, status_code)
