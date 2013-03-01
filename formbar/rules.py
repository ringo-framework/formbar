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

    def __init__(self, expr, msg=None, mode='pre'):
        """Initialize the rule with the expression and mode.

        :expr: string represention of the expression which will be
        checked.
        :msg: string error msg for the rule. If not provied use the
        string represention of the provided expression.
        :mode: string of the mode when to evaluate this rule. Defaults
        to 'pre'
        """
        self.expr = expr
        self.msg = msg
        if msg is None:
            self.msg = 'Expression "%s" failed' % expr
        self.mode = mode

    def evaluate(self):
        """Returns True or False. Evaluates the expression of the rule.
        If the expression fails because parsing fails or the expression
        does not evaluate to a boolean values the function returns
        False.

        :returns: True or False

        """
        return False
