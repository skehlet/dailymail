class StatusCodeError(Exception):
    """Exception raised when the status code is not 200"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        self.status_code = kwargs.get("status_code")
