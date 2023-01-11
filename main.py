import os
from os.path import abspath, dirname
from pathlib import Path

from graphql import parse

from saleor_deprecations import (
    JsonStore,
    diff_schemas,
    download_schema,
    get_deprecated_types,
    get_schema_json,
)

BUILD_DIR = Path(dirname(abspath(__file__))) / "build"
DATA_DIR = BUILD_DIR / "data"

REMOTE_DATA_URL = os.environ.get("REMOTE_DATA_URL")
REMOTE_SCHEMA_URL = os.environ.get("REMOTE_SCHEMA_URL")


def main():
    if not BUILD_DIR.is_dir():
        BUILD_DIR.mkdir()
    if not DATA_DIR.is_dir():
        DATA_DIR.mkdir()

    print(REMOTE_DATA_URL, REMOTE_SCHEMA_URL)
    if not all((REMOTE_DATA_URL, REMOTE_SCHEMA_URL)):
        return

    schemas = JsonStore(
        prefix="sch",
        index_name="schemas",
        remote_url=REMOTE_DATA_URL,
        data_dir=DATA_DIR,
    )
    changes = JsonStore(
        prefix="ch",
        index_name="changes",
        remote_url=REMOTE_URL,
        data_dir=DATA_DIR,
    )

    current_schema_ast = parse(download_schema(REMOTE_SCHEMA_URL))
    deprecated_types = get_deprecated_types(current_schema_ast)
    current_schema = get_schema_json(current_schema_ast, deprecated_types)

    old_schema = schemas.load_last_entry()

    if not old_schema:
        # Initial write
        schemas.insert(current_schema)
        schemas.save_index()
    else:
        diff = diff_schemas(old_schema, current_schema)
        if diff:
            changes.insert(diff)
            changes.save_index()


if __name__ == "__main__":
    main()
