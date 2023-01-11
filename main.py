from saleor_deprecations import get_deprecations


if __name__ == "__main__":
    deprecations = get_deprecations(
        "https://raw.githubusercontent.com/"
        "saleor/saleor/main/saleor/graphql/schema.graphql"
    )

    print(deprecations)