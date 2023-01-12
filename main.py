import os
from os.path import abspath, dirname
from pathlib import Path

from graphql import parse

from saleor_deprecations import (
    DataStore,
    diff_schemas,
    download_schema,
    generate_report,
    get_deprecated_types,
    get_schema_json,
)

BUILD_DIR = Path(dirname(abspath(__file__))) / "build"
DATA_DIR = BUILD_DIR / "data"

REMOTE_DATA_URL = os.environ.get("REMOTE_DATA_URL")
REMOTE_SCHEMA_URL = os.environ.get("REMOTE_SCHEMA_URL")

PREVIOUS_SCHEMA = "schema-previous"
CHANGES = "schema-changes"


def main():
    if not BUILD_DIR.is_dir():
        BUILD_DIR.mkdir()
    if not DATA_DIR.is_dir():
        DATA_DIR.mkdir()

    if not all((REMOTE_DATA_URL, REMOTE_SCHEMA_URL)):
        return

    data_store = DataStore(remote_url=REMOTE_DATA_URL, local_path=DATA_DIR)

    current_schema_ast = parse(download_schema(REMOTE_SCHEMA_URL))
    deprecated_types = get_deprecated_types(current_schema_ast)
    current_schema = get_schema_json(current_schema_ast, deprecated_types)

    previous_schema = data_store.get_remote(PREVIOUS_SCHEMA)
    if previous_schema:
        diff = diff_schemas(previous_schema, current_schema)
        if diff:
            data_store.set_local(CHANGES, diff)

    data_store.set_local(PREVIOUS_SCHEMA, current_schema)
    generate_report(current_schema, deprecated_types, BUILD_DIR / "index.html")


if __name__ == "__main__":
    main()
