# saleor-graphql-deprecations

Deprecations tracker for Saleor's GraphQL API.

Two scripts are provided:

- `main`: "live" script that does real work, eg. pulls schema from Saleor's repo and compares against previous one.
- `localdev`: script that runs comparison logic against two local schema files (`schema-new.graphql` and `schema-old.graphql`). Useful for developing local comparison script.

**Crafted with ❤️ by [Mirumee Software](http://mirumee.com)**
hello@mirumee.com