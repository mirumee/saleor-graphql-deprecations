import requests

from . import exceptions


HEADER_CONTENT_TYPE = "Content-Type"
REQUIRED_CONTENT_TYPE = "text/plain"
REQUIRED_CHARSET = "utf-8"


def download_schema(schema_url: str) -> str:
    r = requests.get(schema_url)
    if r.status_code != 200:
        raise exceptions.SchemaDownloadHTTPStatusCodeError(r.status_code)
    if HEADER_CONTENT_TYPE not in r.headers:
        raise exceptions.SchemaDownloadContentTypeMissingError()

    type_header = r.headers[HEADER_CONTENT_TYPE].lower()
    if "charset=" not in type_header or ";" not in type_header:
        raise exceptions.SchemaDownloadCharsetMissingError()

    content_type, charset = [p.strip() for p in type_header.lower().split(";")]
    charset = charset.replace("charset=", "")

    if content_type != REQUIRED_CONTENT_TYPE:
        raise exceptions.SchemaDownloadContentTypeError(content_type)
    if charset != REQUIRED_CHARSET:
        raise exceptions.SchemaDownloadCharsetInvalidError(charset)

    if not r.content:
        raise exceptions.SchemaDownloadEmptyError()

    return r.content.decode(REQUIRED_CHARSET)
