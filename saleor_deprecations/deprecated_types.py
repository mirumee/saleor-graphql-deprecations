import re
from dataclasses import dataclass

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


@dataclass
class DeprecatedNode:
    version: str
    message: str


def get_deprecated_types(schema_ast: str) -> list[DeprecatedNode]:
    deprecated_types: list[DeprecatedNode] = []
    find_deprecations_in_ast(schema_ast, deprecated_types)

    return deprecated_types


SKIP_NODES = (
    SchemaDefinitionNode,
    DirectiveDefinitionNode,
)


def find_deprecations_in_ast(
    schema_ast: DocumentNode, deprecated_types: list[DeprecatedNode]
):
    for graphql_type in schema_ast.definitions:
        if isinstance(
            graphql_type, (ObjectTypeDefinitionNode, InterfaceTypeDefinitionNode)
        ):
            visit_object_type(graphql_type, deprecated_types)
        elif isinstance(graphql_type, InputObjectTypeDefinitionNode):
            visit_input_type(graphql_type, deprecated_types)
        elif isinstance(graphql_type, EnumTypeDefinitionNode):
            visit_enum_type(graphql_type, deprecated_types)
        elif isinstance(graphql_type, ScalarTypeDefinitionNode):
            visit_scalar_type(graphql_type, deprecated_types)
        elif isinstance(graphql_type, UnionTypeDefinitionNode):
            visit_union_type(graphql_type, deprecated_types)
        elif isinstance(graphql_type, SKIP_NODES):
            pass  # We skip some nodes that don't have deprecations
        else:
            raise ValueError(f"Unknown node type: {type(graphql_type).__name__}")


def visit_object_type(
    node: ObjectTypeDefinitionNode | InterfaceTypeDefinitionNode,
    deprecated_types: list[DeprecatedNode],
):
    interface = isinstance(node, InterfaceTypeDefinitionNode)
    if deprecated := get_deprecated_status(node):
        version, message = deprecated
        deprecated_types.append(
            DeprecatedObjectType(
                version=version,
                message=message,
                interface=interface,
                object=node.name.value,
            )
        )

    for field in node.fields:
        if deprecated := get_deprecated_status(field):
            version, message = deprecated
            deprecated_types.append(
                DeprecatedObjectFieldType(
                    version=version,
                    message=message,
                    interface=interface,
                    object=node.name.value,
                    field=field.name.value,
                )
            )

        if field.arguments:
            for arg in field.arguments:
                if deprecated := get_deprecated_status(arg):
                    version, message = deprecated
                    deprecated_types.append(
                        DeprecatedObjectFieldArgumentType(
                            version=version,
                            message=message,
                            interface=interface,
                            object=node.name.value,
                            field=field.name.value,
                            argument=arg.name.value,
                        )
                    )


@dataclass
class DeprecatedObjectType(DeprecatedNode):
    interface: bool
    object: str


@dataclass
class DeprecatedObjectFieldType(DeprecatedNode):
    interface: bool
    object: str
    field: str


@dataclass
class DeprecatedObjectFieldArgumentType(DeprecatedNode):
    interface: bool
    object: str
    field: str
    argument: str


def visit_input_type(
    node: InputObjectTypeDefinitionNode,
    deprecated_types: list[DeprecatedNode],
):
    if deprecated := get_deprecated_status(node):
        version, message = deprecated
        deprecated_types.append(
            DeprecatedInputType(
                version=version,
                message=message,
                input=node.name.value,
            )
        )

    for field in node.fields:
        if deprecated := get_deprecated_status(field):
            version, message = deprecated
            deprecated_types.append(
                DeprecatedInputFieldType(
                    version=version,
                    message=message,
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


def visit_enum_type(
    node: EnumTypeDefinitionNode,
    deprecated_types: list[DeprecatedNode],
):
    if deprecated := get_deprecated_status(node):
        version, message = deprecated
        deprecated_types.append(
            DeprecatedEnumType(
                version=version,
                message=message,
                enum=node.name.value,
            )
        )

    for value in node.values:
        if deprecated := get_deprecated_status(value):
            version, message = deprecated
            deprecated_types.append(
                DeprecatedEnumValueType(
                    version=version,
                    message=message,
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


def visit_scalar_type(
    node: EnumTypeDefinitionNode,
    deprecated_types: list[DeprecatedNode],
):
    if deprecated := get_deprecated_status(node):
        version, message = deprecated
        deprecated_types.append(
            DeprecatedScalarType(
                version=version,
                message=message,
                scalar=node.name.value,
            )
        )


@dataclass
class DeprecatedScalarType(DeprecatedNode):
    scalar: str


def visit_union_type(
    node: UnionTypeDefinitionNode,
    deprecated_types: list[DeprecatedNode],
):
    if deprecated := get_deprecated_status(node):
        version, message = deprecated
        deprecated_types.append(
            DeprecatedUnionType(
                version=version,
                message=message,
                union=node.name.value,
            )
        )


@dataclass
class DeprecatedUnionType(DeprecatedNode):
    union: str


def get_deprecated_status(node):
    if hasattr(node, "description") and node.description:
        if version := parse_deprecated_message(node.description.value):
            return version, node.description.value.strip()

    if hasattr(node, "directives") and node.directives:
        for directive in node.directives:
            if directive.name.value == "deprecated":
                for arg in directive.arguments:
                    if arg.name.value == "reason":
                        return (
                            parse_deprecated_message(arg.value.value),
                            arg.value.value.strip(),
                        )

    return None


REMOVED_MESSAGE = "removed in saleor"
VERSION_RE = re.compile("[0-9]+\.[0-9]+")


def parse_deprecated_message(message: str):
    message = message.lower()
    if REMOVED_MESSAGE not in message:
        return None

    message = message[message.find(REMOVED_MESSAGE) + len(REMOVED_MESSAGE) :].strip()
    return VERSION_RE.match(message)[0].strip()
