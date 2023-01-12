import re
from datetime import datetime
from os.path import abspath, dirname
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, pass_eval_context, select_autoescape
from markupsafe import Markup, escape

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


def generate_report(schema, deprecated_types, file_path):
    env = Environment(
        loader=FileSystemLoader(
            Path(dirname(abspath(__file__))) / "templates",
        ),
        autoescape=select_autoescape(),
    )
    env.filters["parse"] = parse_markdown

    data = {
        "gen_time": datetime.now(),
        "deprecated_types": list(
            get_deprecated_types_data(schema, deprecated_types)
        ),
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
                "interface": graphql_type.interface,
                "object": graphql_type.object,
                "version": graphql_type.version,
                "message": graphql_type.message,
            }

        if isinstance(graphql_type, DeprecatedObjectFieldType):
            yield {
                "id": f"{graphql_type.object}-{graphql_type.field}",
                "type": "object-field",
                "template": "object-field.html",
                "interface": graphql_type.interface,
                "object": graphql_type.object,
                "field": graphql_type.field,
                "schema": schema[graphql_type.object]["fields"][graphql_type.field],
                "version": graphql_type.version,
                "message": graphql_type.message,
            }

        if isinstance(graphql_type, DeprecatedObjectFieldArgumentType):
            args = list(
                schema[graphql_type.object]["fields"][graphql_type.field]["arguments"]
            )
            index = args.index(graphql_type.argument)

            yield {
                "id": f"{graphql_type.object}-{graphql_type.field}-{graphql_type.argument}",
                "type": "object-field-argument",
                "template": "object-field-argument.html",
                "interface": graphql_type.interface,
                "object": graphql_type.object,
                "field": graphql_type.field,
                "argument": graphql_type.argument,
                "field_schema": schema[graphql_type.object]["fields"][
                    graphql_type.field
                ],
                "schema": schema[graphql_type.object]["fields"][graphql_type.field][
                    "arguments"
                ][graphql_type.argument],
                "first": index == 0,
                "last": (index + 1) == len(args),
                "version": graphql_type.version,
                "message": graphql_type.message,
            }

        if isinstance(graphql_type, DeprecatedInputType):
            yield {
                "id": graphql_type.input,
                "type": "input",
                "template": "input.html",
                "input": graphql_type.input,
                "version": graphql_type.version,
                "message": graphql_type.message,
            }

        if isinstance(graphql_type, DeprecatedInputFieldType):
            yield {
                "id": f"{graphql_type.input}-{graphql_type.field}",
                "type": "input-field",
                "template": "input-field.html",
                "input": graphql_type.input,
                "field": graphql_type.field,
                "schema": schema[graphql_type.input]["fields"][graphql_type.field],
                "version": graphql_type.version,
                "message": graphql_type.message,
            }


@pass_eval_context
def parse_markdown(eval_ctx, value):
    if eval_ctx.autoescape:
        value = escape(value)

    value = re.sub(r"`(.*?)`", r'[START]\1[END]', value)
    value = value.replace("[START]", Markup('<strong class="text-danger font-monospace">'))
    value = value.replace("[END]", Markup('</strong>'))
    return Markup(value) if eval_ctx.autoescape else value
