from datetime import datetime
from os.path import abspath, dirname
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .deprecated_types import (
    DeprecatedEnumType,
    DeprecatedEnumValueType,
    DeprecatedInputType,
    DeprecatedInputFieldType,
    DeprecatedObjectType,
    DeprecatedObjectFieldType,
    DeprecatedObjectFieldArgumentType,
    DeprecatedScalarType,
    DeprecatedUnionType,
)

env = Environment(
    loader=FileSystemLoader(
        Path(dirname(abspath(__file__))) / "TEMPLATES",
    ),
    autoescape=select_autoescape(),
)


def generate_report(schema, deprecated_types, file_path):
    data = {
        "gen_time": datetime.now(),
        "deprecated_types": get_deprecated_types_data(schema, deprecated_types),
        "parse": parse_markdown,
    }

    template = env.get_template("index.html")
    with open(file_path, "w+") as fp:
        fp.write(template.render(**data))


def get_deprecated_types_data(schema, deprecated_types):
    for graphql_type in deprecated_types:
        if isinstance(graphql_type, DeprecatedObjectType):
            yield {
                "id": graphql_type.object,
                "type": "object",
                "template": "object.html",
                "name": "Type %s" % graphql_type.object,
                "object": graphql_type.object,
                "version": graphql_type.version,
                "message": graphql_type.message,
            }

        if isinstance(graphql_type, DeprecatedObjectFieldType):
            yield {
                "id": f"{graphql_type.object}-{graphql_type.field}",
                "type": "object-field",
                "template": "object-field.html",
                "object": graphql_type.object,
                "field": graphql_type.field,
                "schema": schema[graphql_type.object]["fields"][graphql_type.field],
                "version": graphql_type.version,
                "message": graphql_type.message,
            }

        if isinstance(graphql_type, DeprecatedObjectFieldArgumentType):
            yield {
                "id": f"{graphql_type.object}-{graphql_type.field}-{graphql_type.argument}",
                "type": "object-field-argument",
                "template": "object-field-argument.html",
                "object": graphql_type.object,
                "field": graphql_type.field,
                "argument": graphql_type.argument,
                "field_schema": schema[graphql_type.object]["fields"][graphql_type.field],
                "schema": schema[graphql_type.object]["fields"][graphql_type.field]["arguments"][graphql_type.argument],
                "version": graphql_type.version,
                "message": graphql_type.message,
            }


def parse_markdown(value):
    return value