from graphql import parse

from main import BUILD_DIR
from saleor_deprecations import (
    diff_schemas,
    generate_report,
    get_deprecated_types,
    get_schema_json,
)


def main():
    new_schema_ast = parse(open("./schema-new.graphql").read())
    deprecated_types = get_deprecated_types(new_schema_ast)
    new_schema = get_schema_json(new_schema_ast, deprecated_types)

    # last_schema = schemas.load_last_entry()
    old_schema_ast = parse(open("./schema-old.graphql").read())
    deprecated_types = get_deprecated_types(old_schema_ast)
    old_schema = get_schema_json(old_schema_ast, deprecated_types)

    print(diff_schemas(old_schema, new_schema))
    generate_report(new_schema, deprecated_types, BUILD_DIR / "index.html")


if __name__ == "__main__":
    main()
