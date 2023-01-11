class DeprecationsError(Exception):
    pass


class SchemaDownloadError(DeprecationsError):
    pass


class SchemaDownloadHTTPStatusCodeError(SchemaDownloadError):
    msg: str

    def __init__(self, status_code: int):
        self.msg = f"Server returned {status_code} (expected 200)"


class SchemaDownloadContentTypeMissingError(SchemaDownloadError):
    msg = "Server returned response without content type header"


class SchemaDownloadCharsetMissingError(SchemaDownloadError):
    msg = "Server returned response with content type header missing charset"


class SchemaDownloadCharsetInvalidError(SchemaDownloadError):
    msg: str

    def __init__(self, charset: str):
        self.msg = (
            "Server returned response with unsupported charset "
            f"'{charset}' (expected utf-8)"
        )


class SchemaDownloadContentTypeError(SchemaDownloadError):
    msg: str

    def __init__(self, content_type: str):
        self.msg = (
            f"Server returned invalid content type '{content_type}'"
            " (expected text/plain)"
        )


class SchemaDownloadEmptyError(SchemaDownloadError):
    msg = "Server returned empty response"