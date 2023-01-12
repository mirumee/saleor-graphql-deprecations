def diff_schemas(old_schema: dict, current_schema: dict) -> list:
    differences = []

    # Types
    differences += find_new_types(old_schema, current_schema)
    differences += find_deleted_types(old_schema, current_schema)
    differences += find_deprecated_types(old_schema, current_schema)

    # Objects/Interfaces/Inputs
    differences += find_new_fields(old_schema, current_schema)
    differences += find_deleted_fields(old_schema, current_schema)
    differences += find_deprecated_fields(old_schema, current_schema)

    # Objects/Interfaces
    differences += find_new_fields_arguments(old_schema, current_schema)
    differences += find_deleted_fields_arguments(old_schema, current_schema)
    differences += find_deprecated_fields_arguments(old_schema, current_schema)

    # Enums
    differences += find_new_enums_values(old_schema, current_schema)
    differences += find_deleted_enums_values(old_schema, current_schema)
    differences += find_deprecated_enums_values(old_schema, current_schema)

    # Unions
    differences += find_new_unions_types(old_schema, current_schema)
    differences += find_deleted_unions_types(old_schema, current_schema)

    return differences


def find_new_types(old_schema, current_schema) -> list:
    differences = []
    for current_name, current_data in current_schema.items():
        if (
            current_name in old_schema
            and current_data["type"] == old_schema[current_name]["type"]
        ):
            continue

        differences.append({"diff": "type_new", "type": current_name})

    return differences


def find_deleted_types(old_schema, current_schema) -> list:
    differences = []
    for old_name, old_data in old_schema.items():
        if (
            old_name in current_schema
            and old_data["type"] == current_schema[old_name]["type"]
        ):
            continue

        differences.append({"diff": "type_deleted", "type": old_name})

    return differences


def find_deprecated_types(old_schema, current_schema) -> list:
    differences = []
    for current_name, current_data in current_schema.items():
        if not current_data["deprecated"]:
            continue

        if (
            current_name not in old_schema
            or current_data["type"] != old_schema[current_name]["type"]
        ):
            continue

        if current_data["deprecated"] != old_schema[current_name]["deprecated"]:
            differences.append(
                {
                    "diff": "type_deprecated",
                    "type": current_name,
                    "version": current_data["deprecated"],
                }
            )

    return differences


def find_new_fields(old_schema, current_schema) -> list:
    differences = []
    for current_name, current_data in current_schema.items():
        if current_data["type"] not in ("object", "interface", "input"):
            continue

        if (
            current_name not in old_schema
            or current_data["type"] != old_schema[current_name]["type"]
        ):
            continue

        current_fields = current_data["fields"]
        old_fields = old_schema[current_name]["fields"]

        for current_field in current_fields:
            if current_field in old_fields:
                continue

            differences.append(
                {
                    "diff": "field_new",
                    "type": current_name,
                    "field": current_field,
                }
            )

    return differences


def find_deleted_fields(old_schema, current_schema) -> list:
    differences = []
    for current_name, current_data in current_schema.items():
        if current_data["type"] not in ("object", "interface", "input"):
            continue

        if (
            current_name not in old_schema
            or current_data["type"] != old_schema[current_name]["type"]
        ):
            continue

        current_fields = current_data["fields"]
        old_fields = old_schema[current_name]["fields"]

        for old_field in old_fields:
            if old_field in current_fields:
                continue

            differences.append(
                {
                    "diff": "field_deleted",
                    "type": current_name,
                    "field": old_field,
                }
            )

    return differences


def find_deprecated_fields(old_schema, current_schema) -> list:
    differences = []
    for current_name, current_data in current_schema.items():
        if current_data["type"] not in ("object", "interface", "input"):
            continue

        if (
            current_name not in old_schema
            or current_data["type"] != old_schema[current_name]["type"]
        ):
            continue

        current_fields = current_data["fields"]
        old_fields = old_schema[current_name]["fields"]

        for current_field, current_field_data in current_fields.items():
            if not current_field_data["deprecated"] or current_field not in old_fields:
                continue

            old_field_data = old_fields[current_field]
            if current_field_data["deprecated"] != old_field_data["deprecated"]:
                differences.append(
                    {
                        "diff": "field_deprecated",
                        "type": current_name,
                        "field": current_field,
                        "version": current_field_data["deprecated"],
                    }
                )

    return differences


def find_new_fields_arguments(old_schema, current_schema) -> list:
    differences = []
    for current_name, current_data in current_schema.items():
        if current_data["type"] != ("object", "interface"):
            continue

        if (
            current_name not in old_schema
            or current_data["type"] != old_schema[current_name]["type"]
        ):
            continue

        current_fields = current_data["fields"]
        old_fields = old_schema[current_name]["fields"]

        for current_field, current_field_data in current_fields.items():
            if not current_field_data["arguments"] or current_field not in old_fields:
                continue

            old_arguments = old_fields[current_field]["arguments"]
            for current_argument in current_field_data["arguments"]:
                if current_argument not in old_arguments:
                    differences.append(
                        {
                            "diff": "argument_new",
                            "type": current_name,
                            "field": current_field,
                            "argument": current_argument,
                        }
                    )

    return differences


def find_deleted_fields_arguments(old_schema, current_schema) -> list:
    differences = []
    for current_name, current_data in current_schema.items():
        if current_data["type"] != ("object", "interface"):
            continue

        if (
            current_name not in old_schema
            or current_data["type"] != old_schema[current_name]["type"]
        ):
            continue

        current_fields = current_data["fields"]
        old_fields = old_schema[current_name]["fields"]

        for current_field, current_field_data in current_fields.items():
            if (
                not old_fields[current_field]["arguments"]
                or current_field not in old_fields
            ):
                continue

            current_arguments = current_field_data["arguments"]
            for old_argument in old_fields[current_field]["arguments"]:
                if old_argument not in current_arguments:
                    differences.append(
                        {
                            "diff": "argument_deleted",
                            "type": current_name,
                            "field": current_field,
                            "argument": old_argument,
                        }
                    )

    return differences


def find_deprecated_fields_arguments(old_schema, current_schema) -> list:
    differences = []
    for current_name, current_data in current_schema.items():
        if current_data["type"] != ("object", "interface"):
            continue

        if (
            current_name not in old_schema
            or current_data["type"] != old_schema[current_name]["type"]
        ):
            continue

        current_fields = current_data["fields"]
        old_fields = old_schema[current_name]["fields"]

        for current_field, current_field_data in current_fields.items():
            if not current_field_data["arguments"] or current_field not in old_fields:
                continue

            old_field_arguments = old_fields[current_field]["arguments"]
            if not old_field_arguments:
                continue

            for current_argument, current_argument_data in current_field_data[
                "arguments"
            ].items():
                if (
                    not current_argument_data["deprecated"]
                    or current_argument not in old_field_arguments
                ):
                    continue

                if (
                    current_argument_data["deprecated"]
                    != old_field_arguments[current_argument]["deprecated"]
                ):
                    differences.append(
                        {
                            "diff": "argument_deprecated",
                            "type": current_name,
                            "field": current_field,
                            "argument": current_argument,
                            "version": current_argument_data["deprecated"],
                        }
                    )

    return differences


def find_new_enums_values(old_schema, current_schema) -> list:
    differences = []
    for current_name, current_data in current_schema.items():
        if current_data["type"] != "enum":
            continue

        if (
            current_name in old_schema
            and current_data["type"] != old_schema[current_name]["type"]
        ):
            continue

        old_values = old_schema[current_name]["values"]
        for current_value in current_data["values"]:
            if current_value not in old_values:
                differences.append(
                    {
                        "diff": "enum_value_new",
                        "enum": current_name,
                        "value": current_value,
                    }
                )

    return differences


def find_deleted_enums_values(old_schema, current_schema) -> list:
    differences = []
    for current_name, current_data in current_schema.items():
        if current_data["type"] != "enum":
            continue

        if (
            current_name in old_schema
            and current_data["type"] != old_schema[current_name]["type"]
        ):
            continue

        for old_value in old_schema[current_name]["values"]:
            if old_value not in current_data["values"]:
                differences.append(
                    {
                        "diff": "enum_value_deleted",
                        "enum": current_name,
                        "value": old_value,
                    }
                )

    return differences


def find_deprecated_enums_values(old_schema, current_schema) -> list:
    differences = []
    for current_name, current_data in current_schema.items():
        if current_data["type"] != "enum":
            continue

        if (
            current_name in old_schema
            and current_data["type"] != old_schema[current_name]["type"]
        ):
            continue

        old_values = old_schema[current_name]["values"]
        for current_value, current_value_data in current_data["values"].items():
            if not current_value_data["deprecated"] or current_value not in old_values:
                continue

            if (
                current_value_data["deprecated"]
                != old_values[current_value]["deprecated"]
            ):
                differences.append(
                    {
                        "diff": "enum_value_deprecated",
                        "enum": current_name,
                        "value": current_value,
                        "version": current_value_data["deprecated"],
                    }
                )

    return differences


def find_new_unions_types(old_schema, current_schema) -> list:
    differences = []
    for current_name, current_data in current_schema.items():
        if current_data["type"] != "union":
            continue

        if (
            current_name in old_schema
            and current_data["type"] != old_schema[current_name]["type"]
        ):
            continue

        old_types = old_schema[current_name]["types"]
        for current_type in current_data["types"]:
            if current_type not in old_types:
                differences.append(
                    {
                        "diff": "union_type_new",
                        "union": current_name,
                        "type": current_type,
                    }
                )

    return differences


def find_deleted_unions_types(old_schema, current_schema) -> list:
    differences = []
    for current_name, current_data in current_schema.items():
        if current_data["type"] != "union":
            continue

        if (
            current_name in old_schema
            and current_data["type"] != old_schema[current_name]["type"]
        ):
            continue

        for old_type in old_schema[current_name]["types"]:
            if old_type not in current_data["types"]:
                differences.append(
                    {
                        "diff": "union_type_deleted",
                        "union": current_name,
                        "type": old_type,
                    }
                )

    return differences
