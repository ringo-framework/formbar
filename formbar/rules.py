import logging
from pyparsing import Literal, Word, alphanums, Regex, \
    oneOf, Forward, Optional, delimitedList, ParseException, OneOrMore

log = logging.getLogger(__name__)

def _bool(value):
    """Helper function for checking rules. The fuction is used to check
    if there is a value provided. So it will check if the value is not
    an emtpy string or None and returns True in this case. Else False.

    :value: value to be checked
    :returns: True or False

    """
    if value is not None:
        value = unicode(value)
    return bool(value)

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
            self.msg = 'Expression "%s" failed' % " ".join(expr)
        self.mode = mode
        if mode is None:
            self.mode = 'post'
        self.triggers = triggers
        if triggers is None:
            self.triggers = 'error'

    def evaluate(self, values):
        """Returns True or False. Evaluates the expression of the rule against
        the provided values.  If the expression fails because parsing fails or
        the expression does not evaluate to a boolean values the function
        returns False.

        :values: Dictionary with the values from the submission
        :returns: True or False

        """
        rule = []
        for token in self.expr:
            if token.startswith('$'):
                token = values.get(token.strip('$'))
                if isinstance(token, basestring):
                    # Allow " and ' in the token
                    token = '"""%s"""' % token
            try:
                rule.append(str(token))
            except UnicodeEncodeError:
                # eval only seems to like ascii strings. Convert
                # it to ascii before actually evaluate it. Replace non
                # ascii chars
                rule.append(token.encode("ascii","replace"))
        try:
            rule_str = u" ".join(rule)
            # Replace all linebreaks as eval can not handle strings with
            # linebreaks. This is only relevant for textareas.
            rule_str = rule_str.replace('\n', ' ').replace('\r', '')
            result = eval(rule_str)
            log.debug("Rule: %s -> %s" % (rule_str, result))
            return result
        except Exception, e:
            log.error(
                'Evaluation of "%s" failed with error "%s"' % (rule_str, e))
            return False


# Syntax definition for the parser.
LPAR, RPAR = Literal("("), Literal(")")
LSBR, RSBR = Literal("["), Literal("]")


f_len = Literal("len")
f_bool = Literal("bool").setParseAction(lambda x: ['_bool'])
functor = f_len | f_bool

fieldname = Word("$" + alphanums + "_")
integer = Regex(r"-?\d+")
string = Regex(r"'-?\w+'")
real = Regex(r"-?\d+\.\d*")


def convertOperator(op):
    """Returns operater for a given string. Operators can be expressed
    as string known from the shell as "<" can not be included in XML"""
    top = "unknown"
    op = op[0]
    if op == "eq":
        top = "=="
    elif op == "ne":
        top = "!="
    elif op == "gt":
        top = ">"
    elif op == "ge":
        top = ">="
    elif op == "lt":
        top = "<"
    elif op == "le":
        top = "<="
    elif op == "in":
        top = "in"
    elif op == "==":
        top = "=="
    elif op == "and":
        top = "and"
    elif op == "or":
        top = "or"
    elif op == "plus":
        top = "+"
    elif op == "minus":
        top = "-"
    elif op == "mul":
        top = "*"
    elif op == "div":
        top = "/"
    return [top]

op_eq = Literal("eq").setParseAction(convertOperator)
op_ne = Literal("ne").setParseAction(convertOperator)
op_gt = Literal("gt").setParseAction(convertOperator)
op_ge = Literal("ge").setParseAction(convertOperator)
op_lt = Literal("lt").setParseAction(convertOperator)
op_le = Literal("le").setParseAction(convertOperator)
op_in = Literal("in").setParseAction(convertOperator)
op_and = Literal("and").setParseAction(convertOperator)
op_or = Literal("or").setParseAction(convertOperator)
op_plus = Literal("plus").setParseAction(convertOperator)
op_minus = Literal("minus").setParseAction(convertOperator)
op_mul = Literal("mul").setParseAction(convertOperator)
op_div = Literal("div").setParseAction(convertOperator)
operator = (oneOf('== < > <= >= != in and or + - * /')
            | op_eq | op_ne | op_gt | op_ge | op_lt | op_le | op_in | op_and | op_or | op_plus | op_minus | op_mul | op_div)

operand = Forward()
function_call = functor + LPAR + Optional(delimitedList(operand)) + RPAR
option_list = LSBR + Optional(delimitedList(operand, combine=True)) + RSBR
operand << (option_list | function_call | functor | real | integer | string | fieldname)
expr = operand + operator + operand | operand
grouping = LPAR + OneOrMore( expr | operator + expr ) + RPAR
term = grouping | expr
rule = term + Optional(OneOrMore( operator + term))


class Parser(object):
    """Parser for ``Rule`` instances"""

    def parse(self, expr):
        """Will parse and check the expr. If parsing fails a ValueError will be
        raised

        :expr: string of expression
        :returns: string of expression

        """
        try:
            result = rule.parseString(expr)
            return result
        except ParseException, e:
            #log.error(e)
            raise ValueError('Can not parse "%s"' % expr)
