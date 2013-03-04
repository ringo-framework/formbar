import unittest
from test_configparser import XML
from formbar.config import parse, Config
from formbar.form import Form


class TestParseRule(unittest.TestCase):

    def setUp(self):
        config = Config(parse(XML))
        form_config = config.get_form('customform')
        self.form = Form(form_config)

    def test_form_init(self):
        pass

    def test_form_validate_fail(self):
        values = {'default': 'test', 'age': '15', 'birthday': '1998-02-01'}
        self.assertEqual(self.form.validate(values), False)

    def test_form_validate_ok(self):
        values = {'default': 'test', 'age': 16, 'birthday': '1998-02-01'}
        self.assertEqual(self.form.validate(values), True)

    def test_form_save(self):
        values = {'default': 'test', 'age': '16', 'birthday': '1998-02-01'}
        self.assertEqual(self.form.validate(values), True)


if __name__ == '__main__':
    unittest.main()
