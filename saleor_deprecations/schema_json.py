from graphql.language import (
    BooleanValueNode,
    ConstListValueNode,
    ConstObjectValueNode,
    DirectiveDefinitionNode,
    DocumentNode,
    EnumTypeDefinitionNode,
    EnumValueNode,
    FieldDefinitionNode,
    FloatValueNode,
    InputObjectTypeDefinitionNode,
    InterfaceTypeDefinitionNode,
    IntValueNode,
    ListTypeNode,
    ListValueNode,
    NamedTypeNode,
    NonNullTypeNode,
    NullValueNode,
    ObjectFieldNode,
    ObjectTypeDefinitionNode,
    ObjectValueNode,
    ScalarTypeDefinitionNode,
    SchemaDefinitionNode,
    StringValueNode,
    UnionTypeDefinitionNode,
    ValueNode,
    VariableNode,
)

from .deprecated_types import (
    DeprecatedEnumType,
    DeprecatedEnumValueType,
    DeprecatedInputType,
    DeprecatedInputFieldType,
    DeprecatedNode,
    DeprecatedObjectType,
    DeprecatedObjectFieldType,
    DeprecatedObjectFieldArgumentType,
    DeprecatedScalarType,
    DeprecatedUnionType,
)

SKIP_NODES = (
    SchemaDefinitionNode,
    DirectiveDefinitionNode,
)


def get_schema_json(
    schema_ast: DocumentNode, deprecated_types: list[DeprecatedNode] | None = None
):
    schema_json = {}

    for graphql_type in schema_ast.definitions:
        if isinstance(graphql_type, ObjectTypeDefinitionNode):
            schema_json[graphql_type.name.value] = get_graphql_object_type_json(
                graphql_type
            )
        elif isinstance(graphql_type, InterfaceTypeDefinitionNode):
            schema_json[graphql_type.name.value] = get_graphql_interface_type_json(
                graphql_type
            )
        elif isinstance(graphql_type, InputObjectTypeDefinitionNode):
            schema_json[graphql_type.name.value] = get_graphql_input_type_json(
                graphql_type
            )
        elif isinstance(graphql_type, EnumTypeDefinitionNode):
            schema_json[graphql_type.name.value] = get_graphql_enum_type_json(
                graphql_type
            )
        elif isinstance(graphql_type, ScalarTypeDefinitionNode):
            schema_json[graphql_type.name.value] = get_graphql_scalar_type_json(
                graphql_type
            )
        elif isinstance(graphql_type, UnionTypeDefinitionNode):
            schema_json[graphql_type.name.value] = get_graphql_union_type_json(
                graphql_type
            )
        elif isinstance(graphql_type, SKIP_NODES):
            pass  # We skip some nodes that don't have deprecations
        else:
            raise ValueError(f"Unknown node type: {type(graphql_type).__name__}")

    if deprecated_types:
        update_types_deprecated_flags(schema_json, deprecated_types)

    return sort_by_keys(schema_json)


def get_graphql_object_type_json(node: ObjectTypeDefinitionNode):
    return {
        "type": "object",
        "interfaces": [i.name.value for i in node.interfaces],
        "description": get_description(node),
        "deprecated": None,
        "fields": get_graphql_object_fields_json(node),
    }


def get_graphql_object_fields_json(
    node: ObjectTypeDefinitionNode | InterfaceTypeDefinitionNode,
):
    fields_json = {}

    for field in node.fields:
        fields_json[field.name.value] = {
            "type": print_type_node(field.type),
            "description": get_description(field),
            "deprecated": None,
            "arguments": get_graphql_object_field_args_json(field),
        }

    return sort_by_keys(fields_json)


def get_graphql_object_field_args_json(node: FieldDefinitionNode):
    args_json = {}

    for arg in node.arguments:
        args_json[arg.name.value] = {
            "type": print_type_node(arg.type),
            "description": get_description(arg),
            "deprecated": None,
            "default": print_value_node(arg.default_value),
        }

    return sort_by_keys(args_json)


def get_graphql_interface_type_json(node: InterfaceTypeDefinitionNode):
    return {
        "type": "interface",
        "interfaces": [i.name.value for i in node.interfaces],
        "description": get_description(node),
        "deprecated": None,
        "fields": get_graphql_object_fields_json(node),
    }


def get_graphql_input_type_json(node: InputObjectTypeDefinitionNode):
    return {
        "type": "input",
        "description": get_description(node),
        "deprecated": None,
        "fields": get_graphql_input_fields_json(node),
    }


def get_graphql_input_fields_json(node: InputObjectTypeDefinitionNode):
    fields_json = {}

    for field in node.fields:
        fields_json[field.name.value] = {
            "type": print_type_node(field.type),
            "description": get_description(field),
            "deprecated": None,
            "default": print_value_node(field.default_value),
        }

    return sort_by_keys(fields_json)


def get_graphql_enum_type_json(node: EnumTypeDefinitionNode):
    return {
        "type": "enum",
        "description": get_description(node),
        "deprecated": None,
        "values": get_graphql_enum_values_json(node),
    }


def get_graphql_enum_values_json(node: EnumTypeDefinitionNode):
    values_json = {}

    for value in node.values:
        values_json[value.name.value] = {
            "description": get_description(value),
            "deprecated": None,
        }

    return sort_by_keys(values_json)


def get_graphql_scalar_type_json(node: ScalarTypeDefinitionNode):
    return {
        "type": "scalar",
        "description": get_description(node),
        "deprecated": None,
    }


def get_graphql_union_type_json(node: UnionTypeDefinitionNode):
    return {
        "type": "union",
        "description": get_description(node),
        "deprecated": None,
        "types": [t.name.value for t in node.types],
    }


def get_description(node):
    if node.description:
        return node.description.value

    return None


def sort_by_keys(data):
    return {key: data[key] for key in sorted(data)}


def print_type_node(type_node: NamedTypeNode | ListTypeNode | NonNullTypeNode):
    if isinstance(type_node, NamedTypeNode):
        return type_node.name.value

    if isinstance(type_node, ListTypeNode):
        return f"[{print_type_node(type_node.type)}]"

    if isinstance(type_node, NonNullTypeNode):
        return f"{print_type_node(type_node.type)}!"


def print_value_node(value: ValueNode):
    if value is None:
        return None

    if isinstance(value, IntValueNode):
        return int(value.value)

    if isinstance(value, FloatValueNode):
        return float(value.value)

    if isinstance(value, StringValueNode):
        return str(value.value)

    if isinstance(value, BooleanValueNode):
        return value.value

    if isinstance(value, NullValueNode):
        return None

    if isinstance(value, EnumValueNode):
        return f"ENUM.{value.value}"

    if isinstance(value, (ConstListValueNode, ListValueNode)):
        return [print_value_node(v) for v in value.values]

    if isinstance(value, (ConstObjectValueNode, ObjectValueNode)):
        return sort_by_keys(
            {v.name.value: print_value_node(v.value) for v in value.fields}
        )

    if isinstance(value, VariableNode):
        return f"${value.name.value}"

    if isinstance(value, ObjectFieldNode):
        return sort_by_keys(
            {v.name.value: print_value_node(v.value) for v in value.fields}
        )

    raise Exception(value)


def update_types_deprecated_flags(
    schema_json: dict, deprecated_types: list[DeprecatedNode]
):
    for deprecated_type in deprecated_types:
        if isinstance(deprecated_type, DeprecatedObjectType):
            schema_json[deprecated_type.object]["deprecated"] = deprecated_type.version

        if isinstance(deprecated_type, DeprecatedObjectFieldType):
            schema_json[deprecated_type.object]["fields"][deprecated_type.field][
                "deprecated"
            ] = deprecated_type.version

        if isinstance(deprecated_type, DeprecatedObjectFieldArgumentType):
            schema_json[deprecated_type.object]["fields"][deprecated_type.field][
                "arguments"
            ][deprecated_type.argument]["deprecated"] = deprecated_type.version

        if isinstance(deprecated_type, DeprecatedEnumType):
            schema_json[deprecated_type.enum]["deprecated"] = deprecated_type.version

        if isinstance(deprecated_type, DeprecatedEnumValueType):
            schema_json[deprecated_type.enum]["values"][deprecated_type.value][
                "deprecated"
            ] = deprecated_type.version

        if isinstance(deprecated_type, DeprecatedInputType):
            schema_json[deprecated_type.input]["deprecated"] = deprecated_type.version

        if isinstance(deprecated_type, DeprecatedInputFieldType):
            schema_json[deprecated_type.input]["fields"][deprecated_type.field][
                "deprecated"
            ] = deprecated_type.version

        if isinstance(deprecated_type, DeprecatedScalarType):
            schema_json[deprecated_type.scalar]["deprecated"] = deprecated_type.version

        if isinstance(deprecated_type, DeprecatedUnionType):
            schema_json[deprecated_type.union]["deprecated"] = deprecated_type.version
