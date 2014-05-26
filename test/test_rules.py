import unittest
from formbar.rules import Rule, Parser


class TestParseRule(unittest.TestCase):

    def setUp(self):
        self.parser = Parser()

    def test_empty_expr(self):
        expr = ""
        self.assertRaises(ValueError, self.parser.parse, expr)

    # Test operators
    def test_eq_expr(self):
        expr = "$field=='string'"
        result = self.parser.parse(expr)
        self.assertEqual(expr, "".join(result.asList()))

    def test_uq_expr(self):
        expr = "$field!=3.2"
        result = self.parser.parse(expr)
        self.assertEqual(expr, "".join(result.asList()))

    def test_gt_expr(self):
        expr = "$field>4"
        result = self.parser.parse(expr)
        self.assertEqual(expr, "".join(result.asList()))

    def test_lt_expr(self):
        expr = "$field<$field"
        result = self.parser.parse(expr)
        self.assertEqual(expr, "".join(result.asList()))

    def test_lteq_expr(self):
        expr = "$field<=$field"
        result = self.parser.parse(expr)
        self.assertEqual(expr, "".join(result.asList()))

    def test_lteq_expr(self):
        expr = "2 le 4" # -> "2<=4"
        result = self.parser.parse(expr)
        self.assertEqual("2<=4", "".join(result.asList()))

    def test_gteq_expr(self):
        expr = "$field>=$field"
        result = self.parser.parse(expr)
        self.assertEqual(expr, "".join(result.asList()))

    def test_in_expr(self):
        expr = "$field in [ 1,2,3 ]"
        result = self.parser.parse(expr)
        self.assertEqual(expr, " ".join(result.asList()))

    def test_plus_expr(self):
        expr = "$field + $field"
        result = self.parser.parse(expr)
        self.assertEqual(expr, " ".join(result.asList()))

    def test_minus_expr(self):
        expr = "$field - $field"
        result = self.parser.parse(expr)
        self.assertEqual(expr, " ".join(result.asList()))

    def test_mul_expr(self):
        expr = "$field * $field"
        result = self.parser.parse(expr)
        self.assertEqual(expr, " ".join(result.asList()))

    def test_div_expr(self):
        expr = "$field / $field"
        result = self.parser.parse(expr)
        self.assertEqual(expr, " ".join(result.asList()))

    def test_proz_expr(self):
        expr = "$field / 100 * 10"
        result = self.parser.parse(expr)
        self.assertEqual(expr, " ".join(result.asList()))

    def test_grouping_expr(self):
        expr = "( $do_zg_ap + $do_zg_pxa + $do_zg_team + $do_zg_leit + $do_zg_doz ) < 100"
        result = self.parser.parse(expr)
        self.assertEqual(expr, " ".join(result.asList()))

    # Test function

    def test_function_len_expr(self):
        expr = "len($field)>=3"
        result = self.parser.parse(expr)
        self.assertEqual(expr, "".join(result.asList()))

    def test_function_bool_expr(self):
        expr = "bool($field)"
        result = self.parser.parse(expr)
        self.assertEqual('_bool($field)', "".join(result.asList()))

    def test_function_bool_expr2(self):
        expr = "bool( '_' )"
        result = self.parser.parse(expr)
        self.assertEqual("_bool('_')", "".join(result.asList()))

    def test_function_bool_expr3(self):
        expr = "bool( 'xxx' )"
        result = self.parser.parse(expr)
        self.assertEqual("_bool('xxx')", "".join(result.asList()))


class TestEvaluateRule(unittest.TestCase):

    def setUp(self):
        self.parser = Parser()

    def build_rule(self, expr, desired=False):
        result = self.parser.parse(expr)
        if desired:
            triggers="warning"
        else:
            triggers="error"
        rule = Rule(result, triggers=triggers)
        return rule

    def test_default_mode(self):
        values = {"field": "string"}
        expr = "$field=='string'"
        rule = self.build_rule(expr)
        self.assertEqual(rule.mode, 'post')

    def test_eq_expr_ok(self):
        values = {"field": "string"}
        expr = "$field=='string'"
        rule = self.build_rule(expr)
        self.assertEqual(rule.evaluate(values), True)

    def test_eq_expr_fail(self):
        values = {"field": "hstring"}
        expr = "$field=='string'"
        rule = self.build_rule(expr)
        self.assertEqual(rule.evaluate(values), False)

    def test_uq_expr_ok(self):
        values = {"field": "string"}
        expr = "$field=='string'"
        rule = self.build_rule(expr)
        self.assertEqual(rule.evaluate(values), True)

    def test_uq_expr_fail(self):
        values = {"field": "hstring"}
        expr = "$field!='string'"
        rule = self.build_rule(expr)
        self.assertEqual(rule.evaluate(values), True)

    def test_gt_expr_ok(self):
        values = {"field": 5}
        expr = "$field>4"
        rule = self.build_rule(expr)
        self.assertEqual(rule.evaluate(values), True)

    def test_gt_expr_fail(self):
        values = {"field": 5}
        expr = "$field>5"
        rule = self.build_rule(expr)
        self.assertEqual(rule.evaluate(values), False)

    def test_gteq_expr_ok(self):
        values = {"field": 4}
        expr = "$field>=4"
        rule = self.build_rule(expr)
        self.assertEqual(rule.evaluate(values), True)

    def test_gteq_expr_fail(self):
        values = {"field": 4}
        expr = "$field>=5"
        rule = self.build_rule(expr)
        self.assertEqual(rule.evaluate(values), False)

    def test_lt_expr_ok(self):
        values = {"field": 3}
        expr = "$field<4"
        rule = self.build_rule(expr)
        self.assertEqual(rule.evaluate(values), True)

    def test_lt_expr_fail(self):
        values = {"field": 5}
        expr = "$field<5"
        rule = self.build_rule(expr)
        self.assertEqual(rule.evaluate(values), False)

    def test_lteq_expr_ok(self):
        values = {"field": 3}
        expr = "$field<=4"
        rule = self.build_rule(expr)
        self.assertEqual(rule.evaluate(values), True)

    def test_lteq2_expr_ok(self):
        values = {}
        expr = " 2 le 4"
        rule = self.build_rule(expr)
        self.assertEqual(rule.evaluate(values), True)

    def test_lteq_expr_fail(self):
        values = {"field": 6}
        expr = "$field<=5"
        rule = self.build_rule(expr)
        self.assertEqual(rule.evaluate(values), False)

    def test_len_expr_ok(self):
        values = {"field": "test"}
        expr = "len($field)<=5"
        rule = self.build_rule(expr)
        self.assertEqual(rule.evaluate(values), True)

    def test_len_expr_fail(self):
        values = {"field": "test is too long"}
        expr = "len($field)<=5"
        rule = self.build_rule(expr)
        self.assertEqual(rule.evaluate(values), False)

    def test_bool_ok(self):
        values = {"field": "we have a value"}
        expr = "bool('xxx')"
        rule = self.build_rule(expr)
        self.assertEqual(rule.evaluate(values), True)

    def test_required_ok(self):
        values = {"field": "we have a value"}
        expr = "bool($field)"
        rule = self.build_rule(expr)
        self.assertEqual(rule.evaluate(values), True)

    def test_required_fail(self):
        values = {"field": ""}
        expr = "bool($field)"
        rule = self.build_rule(expr)
        self.assertEqual(rule.evaluate(values), False)

    def test_desired_ok(self):
        values = {"field": "we have a value"}
        expr = "bool($field)"
        rule = self.build_rule(expr, desired=True)
        self.assertEqual(rule.evaluate(values), True)

    def test_desired_fail(self):
        values = {"field": ""}
        expr = "bool($field)"
        rule = self.build_rule(expr, desired=True)
        self.assertEqual(rule.evaluate(values), False)

if __name__ == '__main__':
    unittest.main()
