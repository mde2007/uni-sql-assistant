import sqlglot
from sqlglot import exp


def explain_sql(sql):
    tree = sqlglot.parse_one(sql, read="postgres")

    tables = sorted({table.name for table in tree.find_all(exp.Table)})
    joins = [join.sql(dialect="postgres") for join in tree.find_all(exp.Join)]
    aggregates = [agg.sql(dialect="postgres") for agg in tree.find_all(exp.AggFunc)]

    where = tree.args.get("where")
    group = tree.args.get("group")
    limit = tree.args.get("limit")

    filters = None
    if where is not None:
        filters = where.this.sql(dialect="postgres")

    group_by = []
    if group is not None:
        group_by = [e.sql(dialect="postgres") for e in group.expressions]

    limit_value = None
    if limit is not None:
        limit_value = limit.expression.sql()

    return {
        "tables": tables,
        "joins": joins,
        "filters": filters,
        "group_by": group_by,
        "aggregates": aggregates,
        "limit": limit_value,
    }