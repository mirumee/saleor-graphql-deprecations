import re
from dataclasses import dataclass

from graphql import parse
from graphql.language import (
    DirectiveDefinitionNode,
    DocumentNode,
    EnumTypeDefinitionNode,
    InputObjectTypeDefinitionNode,
    InterfaceTypeDefinitionNode,
    ObjectTypeDefinitionNode,
    ScalarTypeDefinitionNode,
    SchemaDefinitionNode,
    UnionTypeDefinitionNode,
)

from .download_schema import download_schema


@dataclass
class DeprecatedNode:
    version: str


def get_deprecations(schema_url: str) -> list[DeprecatedNode]:
    schema_ast = parse(download_schema(schema_url))

    deprecations: list[DeprecatedNode] = []
    find_deprecations_in_ast(schema_ast, deprecations)

    return deprecations


SKIP_NODES = (
    SchemaDefinitionNode,
    DirectiveDefinitionNode,
)


def find_deprecations_in_ast(schema_ast: DocumentNode, deprecations: list[DeprecatedNode]):
    for graphql_type in schema_ast.definitions:
        if isinstance(graphql_type, (ObjectTypeDefinitionNode, InterfaceTypeDefinitionNode)):
            find_deprecations_in_object_type(graphql_type, deprecations)
        elif isinstance(graphql_type, InputObjectTypeDefinitionNode):
            find_deprecations_in_input_type(graphql_type, deprecations)
        elif isinstance(graphql_type, EnumTypeDefinitionNode):
            find_deprecations_in_enum_type(graphql_type, deprecations)
        elif isinstance(graphql_type, ScalarTypeDefinitionNode):
            find_deprecations_in_scalar_type(graphql_type, deprecations)
        elif isinstance(graphql_type, UnionTypeDefinitionNode):
            find_deprecations_in_union_type(graphql_type, deprecations)
        elif isinstance(graphql_type, SKIP_NODES):
            pass  # We skip some nodes that don't have deprecations
        else:
            raise ValueError(f"Unknown node type: {type(graphql_type).__name__}")


def find_deprecations_in_object_type(
    node: ObjectTypeDefinitionNode | InterfaceTypeDefinitionNode,
    deprecations: list[DeprecatedNode],
):
    if version := get_deprecated_version(node):
        deprecations.append(
            DeprecatedObjectType(version=version, object=node.name.value)
        )

    for field in node.fields:
        if version := get_deprecated_version(field):
            deprecations.append(
                DeprecatedObjectFieldType(
                    version=version,
                    object=node.name.value,
                    field=field.name.value,
                )
            )

        if field.arguments:
            for arg in field.arguments:
                if version := get_deprecated_version(field):
                    deprecations.append(
                        DeprecatedObjectFieldArgumentType(
                            version=version,
                            object=node.name.value,
                            field=field.name.value,
                            argument=arg.name.value,
                        )
                    )


@dataclass
class DeprecatedObjectType(DeprecatedNode):
    object: str


@dataclass
class DeprecatedObjectFieldType(DeprecatedNode):
    object: str
    field: str


@dataclass
class DeprecatedObjectFieldArgumentType(DeprecatedNode):
    object: str
    field: str
    argument: str


def find_deprecations_in_input_type(
    node: InputObjectTypeDefinitionNode,
    deprecations: list[DeprecatedNode],
):
    if version := get_deprecated_version(node):
        deprecations.append(
            DeprecatedInputType(version=version, input=node.name.value)
        )

    for field in node.fields:
        if version := get_deprecated_version(field):
            deprecations.append(
                DeprecatedInputFieldType(
                    version=version,
                    input=node.name.value,
                    field=field.name.value,
                )
            )


@dataclass
class DeprecatedInputType(DeprecatedNode):
    input: str


@dataclass
class DeprecatedInputFieldType(DeprecatedNode):
    input: str
    field: str


def find_deprecations_in_enum_type(
    node: EnumTypeDefinitionNode,
    deprecations: list[DeprecatedNode],
):
    if version := get_deprecated_version(node):
        deprecations.append(
            DeprecatedEnumType(version=version, enum=node.name.value)
        )

    for value in node.values:
        if version := get_deprecated_version(value):
            deprecations.append(
                DeprecatedEnumValueType(
                    version=version,
                    enum=node.name.value,
                    value=value.name.value,
                )
            )


@dataclass
class DeprecatedEnumType(DeprecatedNode):
    enum: str


@dataclass
class DeprecatedEnumValueType(DeprecatedNode):
    enum: str
    value: str


def find_deprecations_in_scalar_type(
    node: EnumTypeDefinitionNode,
    deprecations: list[DeprecatedNode],
):
    if version := get_deprecated_version(node):
        deprecations.append(
            DeprecatedScalarType(version=version, scalar=node.name.value)
        )


@dataclass
class DeprecatedScalarType(DeprecatedNode):
    scalar: str


def find_deprecations_in_union_type(
    node: UnionTypeDefinitionNode,
    deprecations: list[DeprecatedNode],
):
    if version := get_deprecated_version(node):
        deprecations.append(
            DeprecatedUnionType(version=version, union=node.name.value)
        )


@dataclass
class DeprecatedUnionType(DeprecatedNode):
    union: str


def get_deprecated_version(node):
    if hasattr(node, "description") and node.description:
        if version := parse_deprecated_message(node.description.value):
            return version

    if hasattr(node, "directives") and node.directives:
        for directive in node.directives:
            if directive.name.value == "deprecated":
                for arg in directive.arguments:
                    if arg.name.value == "reason":
                        return parse_deprecated_message(arg.value.value)
    
    return None


REMOVED_MESSAGE = "removed in saleor"
VERSION_RE = re.compile("[0-9]+\.[0-9]+")


def parse_deprecated_message(message: str):
    message = message.lower()
    if REMOVED_MESSAGE not in message:
        return None

    message = message[message.find(REMOVED_MESSAGE) + len(REMOVED_MESSAGE):].strip()
    return VERSION_RE.match(message)[0].strip()
