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
REMOTE_URL = "https://raw.githubusercontent.com/mirumee/saleor-graphql-deprecations/gh-pages/data/"
REMOTE_SCHEMA_URL = (
    "https://raw.githubusercontent.com/saleor/saleor/main/saleor/graphql/schema.graphql"
)


def main():
    if not BUILD_DIR.is_dir():
        BUILD_DIR.mkdir()
    if not DATA_DIR.is_dir():
        DATA_DIR.mkdir()

    schemas = JsonStore(
        prefix="sch",
        index_name="schemas",
        remote_url=REMOTE_URL,
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
        print(diff)


if __name__ == "__main__":
    main()
