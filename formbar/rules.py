import logging
from pyparsing import (
    operatorPrecedence,
    Group,
    oneOf,
    Forward,
    Optional,
    delimitedList,
    opAssoc,
    Keyword,
    Literal,
    Word,
    alphas,
    alphanums,
    nums,
    Regex,
    ParseResults,
    ParserElement,
    ParseException
)

log = logging.getLogger(__name__)

ParserElement.enablePackrat()

opmap = {
    "eq": "==",
    "ne": "!=",
    "gt": ">",
    "ge": ">=",
    "le": "<=",
    "lt": "<",
    "plus": "+",
    "minus": "-",
    "mul": "*",
    "div": "/"
}


def convertOperator(op):
    """Returns operater for a given string. Operators can be expressed
    as string known from the shell as "<" can not be included in XML"""
    op = op[0]
    return opmap.get(op, op)

RULE = Forward()
EXPR = Forward()
f_len = Literal("len")
f_bool = Literal("bool").setParseAction(lambda x: ['_bool'])
functor = f_len | f_bool

LPAR = Literal("(")
RPAR = Literal(")")
LBR = Literal("[")
RBR = Literal("]")
TRUE = Keyword("True")
FALSE = Keyword("False")
VAR = Word("$" + alphanums + "_")
STR = Word("'" + alphanums + "_" + "'")
FLOAT = Regex(r'\d+(\.\d*)?([eE]\d+)?')
NUM =  FLOAT | Word(nums)
LIST = LBR + Optional(delimitedList(STR | NUM, combine=True)) + RBR
FUNC = functor + LPAR + Optional(delimitedList(EXPR, combine=True)) + RPAR
OPERAND = FUNC | LIST | NUM | STR | VAR | FALSE | TRUE

expop = Literal('^')
negop = Literal('not')
boolop = oneOf('and or')
eqop = oneOf('== != < > <= >= gt lt eq ne ge le in').setParseAction(convertOperator)
signop = oneOf('+ -').setParseAction(convertOperator)
multop = oneOf('* / mul div').setParseAction(convertOperator)
plusop = oneOf('+ - plus minus').setParseAction(convertOperator)

EXPR << OPERAND
RULE << operatorPrecedence(EXPR,
                           [(expop, 2, opAssoc.RIGHT),
                            (signop, 1, opAssoc.RIGHT),
                            (negop, 1, opAssoc.RIGHT),
                            (multop, 2, opAssoc.LEFT),
                            (eqop, 2, opAssoc.LEFT),
                            (boolop, 2, opAssoc.LEFT),
                            (plusop, 2, opAssoc.LEFT)])


def _bool(value):
    """Helper function for checking rules. The fuction is used to check
    if there is a value provided. So it will check if the value is not
    an emtpy string or None and returns True in this case. Else False.

    :value: value to be checked
    :returns: True or False

    """
    if value is None:
        return False
    return bool(unicode(value))


class Rule(object):
    """Rule class. Rules must evaluate to True or False. If the
    expression does not evaluate to a Boolean value the evaluate
    function will return False. Each Rule can have a msg.''pre'

    Further the rule has a mode which configures the time when the rules
    gets evaluation in the validation process. 'pre' means checking the
    rule before the data has been converted into a python type. 'post'
    means checkig the value after it has been converted into a python
    type. This way you can do checks not only on string as submitted
    from the forms but also an the converted datatypes.
    """

    def __init__(self, expr, msg=None, mode='post', triggers='error'):
        """Initialize the rule with the expression and mode.

        :expr: string represention of the expression which will be
        checked.
        :msg: string error msg for the rule. If not provied use the
        string represention of the provided expression.
        :mode: string of the mode when to evaluate this rule. Defaults
        to 'post'
        :triggers: string of the type of "effect" this rule should
        generate if the evaluation fails. Can either be a error message
        or a warning. In case of a warning the validation of the form
        will fail. In case of a warning only a warning message will be
        displayer. Defaults to 'error'
        """
        self.expr = expr
        self.msg = msg
        if msg is None:
            self.msg = 'Expression "%s" failed' % " ".join(str(expr))
        self.mode = mode
        if mode is None:
            self.mode = 'post'
        self.triggers = triggers
        if triggers is None:
            self.triggers = 'error'

    def _evaluate(self, tree, values=None):
        stack = []
        if not values:
            values = {}
        for t in tree:
            if isinstance(t, ParseResults):
                stack.append(str(self._evaluate(t, values)))
            else:
                if t.startswith("$"):
                    value = values[t.strip("$")]
                    if isinstance(value, basestring):
                        value = '"""%s"""' % value
                    t = t.replace(t, unicode(value))
                stack.append(t)
        result = eval(" ".join(stack))
        log.debug("Eval: %s: %s" % (result, stack))
        return result

    def evaluate(self, values):
        """Returns True or False. Evaluates the expression of the rule against
        the provided values.  If the expression fails because parsing fails or
        the expression does not evaluate to a boolean values the function
        returns False.

        :values: Dictionary with the values from the submission
        :returns: True or False

        """
        try:
            return bool(self._evaluate(self.expr, values))
        except:
            log.exception("")
            log.error("Can not evalute '%s' "
                      "with values: %s" % (self.expr, values))
            return False


class Parser(object):
    """Parser for ``Rule`` instances"""

    def parse(self, expression):
        """Will parse and check the expr. If parsing fails a ValueError will be
        raised

        :expression: string of expression
        :returns: string of expression

        """
        try:
            result = RULE.parseString(expression)
            return result
        except ParseException, e:
            log.error("%s: '%s'" % (e, expression))
            raise ValueError('Can not parse "%s"' % expression)

if __name__ == "__main__":
    values = {
        "t": 1,
        "f": 0,
        "z": 2,
        "y": "1",
        "name": "test",
        "x": [1, 2, 3],
    }
    tests = [("$t", True),
             ("$f", False),
             ("$t and $f", False),
             ("$t and not $f", True),
             ("not not $t", True),
             ("not($t and $f)", True),
             ("$f or not $t and $t", False),
             ("$f or not $t or not $f", True),
             ("$f or not ($t and $t)", False),
             ("$t or $f or $t", True),
             ("$t or $f or $t and False", True),
             ("($t or $f or $t) and False", False),
             ("$t + $t == $z", True),
             ("(200 * 5 / 3) > $t", True),
             ("$t in $x", True),
             ("$f in $x", False),
             ("bool($f)", False),
             ("bool($t)", True),
             ("$t gt $f", True),
             ("'test' == $name", True),
             ("len($x) == 3", True),
             ("($t in [1,2,4] and $f == 0) or ($t in [0,3,5] and $f == 1) or ($t in ['', 6])", True),
             ("($y eq '1' and $z in [1,2] ) or ( $y '3' and $z in [3,4] ) or ( $y in ['','2','4'] )", True),
             ]

    for t, expected in tests:
        p = Parser()
        rule = Rule(p.parse(t))
        res = rule.evaluate(values)
        success = "PASS" if res == expected else "FAIL"
        print success, ":", t, "->", res, rule.expr
