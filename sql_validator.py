import sqlglot
from sqlglot import exp


def _is_literal_true(expression):
    """Detect simple always-true conditions such as TRUE or 1 = 1."""
    if isinstance(expression, exp.Paren):
        return _is_literal_true(expression.this)

    if isinstance(expression, exp.Boolean):
        return expression.this is True

    if isinstance(expression, exp.EQ):
        left = expression.this
        right = expression.expression
        if isinstance(left, exp.Literal) and isinstance(right, exp.Literal):
            return left.this == right.this

    return False


def _has_unconditional_or(expression):
    """Reject UPDATE filters containing an always-true OR branch."""
    if isinstance(expression, exp.Paren):
        return _has_unconditional_or(expression.this)

    if isinstance(expression, exp.Or):
        return (
            _is_literal_true(expression.this)
            or _is_literal_true(expression.expression)
            or _has_unconditional_or(expression.this)
            or _has_unconditional_or(expression.expression)
        )

    return False


def validate_sql(query):
    """Allow one MySQL SELECT or a single-table UPDATE with a WHERE filter."""
    if not isinstance(query, str) or not query.strip():
        return False, "SQL query is empty."

    try:
        statements = sqlglot.parse(query, read="mysql")

        if len(statements) != 1 or statements[0] is None:
            return False, "Only one SQL statement is allowed."

        statement = statements[0]

        if any(getattr(node, "comments", None) for node in statement.walk()):
            return False, "SQL comments are not allowed."

        if isinstance(statement, exp.Select):
            if statement.args.get("into") is not None:
                return False, "SELECT INTO is not allowed."

            if statement.args.get("locks"):
                return False, "Locking SELECT queries are not allowed."

            return True, statement.sql(dialect="mysql")

        if isinstance(statement, exp.Update):
            # Only a straightforward, single-table UPDATE is supported.
            if not isinstance(statement.this, exp.Table):
                return False, "Only single-table UPDATE queries are allowed."

            if statement.args.get("from") is not None:
                return False, "UPDATE with FROM is not allowed."

            if any(isinstance(node, exp.Join) for node in statement.walk()):
                return False, "UPDATE with JOIN is not allowed."

            where_clause = statement.args.get("where")
            if where_clause is None:
                return False, "UPDATE requires a WHERE condition."

            condition = where_clause.this
            if _is_literal_true(condition) or _has_unconditional_or(condition):
                return False, "UPDATE condition is too broad. Use a specific WHERE condition."

            if not statement.args.get("expressions"):
                return False, "UPDATE must contain at least one column change."

            return True, statement.sql(dialect="mysql")

        return False, "Only SELECT and conditional UPDATE queries are allowed."

    except (sqlglot.errors.ParseError, ValueError, TypeError):
        return False, "Invalid SQL syntax."


def get_sql_operation(query):
    """Return SELECT or UPDATE for a valid query; otherwise return None."""
    is_valid, normalized_sql = validate_sql(query)
    if not is_valid:
        return None

    statement = sqlglot.parse_one(normalized_sql, read="mysql")
    if isinstance(statement, exp.Select):
        return "SELECT"
    if isinstance(statement, exp.Update):
        return "UPDATE"
    return None
