from brabbel.expression import Expression


class Rule(Expression):
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

    def __init__(self, expression, msg=None,
                 mode='post', triggers='error',
                 desired=False, required=False):
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
        Expression.__init__(self, expression)
        self.msg = msg
        if msg is None:
            self.msg = 'Expression "%s" failed' % self._expression
        self.mode = mode
        if mode is None:
            self.mode = 'post'
        self.triggers = triggers
        if triggers is None:
            self.triggers = 'error'
        self.required = required
        self.desired = desired

    def __repr__(self):
        return u"{},{}".format(self._expression, self.triggers)

    def evaluate(self, values=None):
        """Returns True or False. Evaluates the expression of the rule against
        the provided values.  If the expression fails because parsing fails or
        the expression does not evaluate to a boolean values the function
        returns False.

        :values: Dictionary with key value pairs containing values which
        can be used while evaluation
        :returns: True or False

        """
        if values is None:
            values = {}
        return bool(self._evaluate(self._expression_tree, values))
