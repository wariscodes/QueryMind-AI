import unittest

from sql_validator import get_sql_operation, validate_sql


class SQLValidatorTests(unittest.TestCase):
    def assert_valid(self, query, expected_operation):
        valid, result = validate_sql(query)
        self.assertTrue(valid, result)
        self.assertEqual(get_sql_operation(query), expected_operation)

    def assert_invalid(self, query):
        valid, result = validate_sql(query)
        self.assertFalse(valid, f"Unexpectedly accepted: {query}")

    def test_simple_select(self):
        self.assert_valid("SELECT * FROM customers", "SELECT")

    def test_select_with_filter(self):
        self.assert_valid(
            "SELECT * FROM customers WHERE city = 'Delhi'", "SELECT"
        )

    def test_select_with_join(self):
        self.assert_valid(
            "SELECT c.customer_name, o.total_amount "
            "FROM customers AS c "
            "JOIN orders AS o ON c.customer_id = o.customer_id",
            "SELECT",
        )

    def test_select_with_aggregation(self):
        self.assert_valid(
            "SELECT status, COUNT(*) FROM orders GROUP BY status", "SELECT"
        )

    def test_update_with_specific_where(self):
        self.assert_valid(
            "UPDATE customers SET city = 'Jaipur' WHERE customer_id = 5",
            "UPDATE",
        )

    def test_update_without_where_is_rejected(self):
        self.assert_invalid("UPDATE customers SET city = 'Jaipur'")

    def test_update_with_where_one_equals_one_is_rejected(self):
        self.assert_invalid(
            "UPDATE customers SET city = 'Jaipur' WHERE 1 = 1"
        )

    def test_update_with_unconditional_or_is_rejected(self):
        self.assert_invalid(
            "UPDATE customers SET city = 'Jaipur' "
            "WHERE customer_id = 5 OR 1 = 1"
        )

    def test_update_with_join_is_rejected(self):
        self.assert_invalid(
            "UPDATE customers c JOIN orders o "
            "ON c.customer_id = o.customer_id "
            "SET c.city = 'Jaipur' WHERE o.order_id = 10"
        )

    def test_insert_is_rejected(self):
        self.assert_invalid(
            "INSERT INTO customers (customer_name) VALUES ('Test User')"
        )

    def test_delete_is_rejected(self):
        self.assert_invalid("DELETE FROM customers WHERE customer_id = 1")

    def test_drop_is_rejected(self):
        self.assert_invalid("DROP TABLE customers")

    def test_multiple_statements_are_rejected(self):
        self.assert_invalid("SELECT * FROM customers; SELECT * FROM orders")

    def test_empty_query_is_rejected(self):
        self.assert_invalid("   ")

    def test_select_into_is_rejected(self):
        self.assert_invalid(
            "SELECT customer_id FROM customers INTO OUTFILE 'x.csv'"
        )

    def test_locking_select_is_rejected(self):
        self.assert_invalid("SELECT * FROM customers FOR UPDATE")


if __name__ == "__main__":
    unittest.main(verbosity=2)
