import datetime
import unittest
from test_configparser import XML
from formbar.config import parse, Config
from formbar.form import Form, StateError


class TestFormValidation(unittest.TestCase):

    def setUp(self):
        config = Config(parse(XML))
        form_config = config.get_form('customform')
        self.form = Form(form_config)

    def test_form_init(self):
        pass

    def test_form_unknown_field(self):
        values = {'unknown': 'test', 'age': '15', 'birthday': '1998-02-01'}
        self.assertRaises(KeyError, self.form.validate, values)

    def test_form_validate_fail(self):
        values = {'default': 'test', 'age': '15', 'birthday': '1998-02-01'}
        self.assertEqual(self.form.validate(values), False)

    def test_form_validate_ok(self):
        values = {'default': 'test', 'age': '16', 'birthday': '1998-02-01'}
        self.assertEqual(self.form.validate(values), True)

    def test_form_deserialize_int(self):
        values = {'default': 'test', 'age': '16', 'birthday': '1998-02-01'}
        self.form.validate(values)
        self.assertEqual(self.form.data['age'], 16)

    def test_form_deserialize_float(self):
        values = {'default': 'test', 'age': '16',
                  'birthday': '1998-02-01', 'weight': '87.5'}
        self.assertEqual(self.form.validate(values), True)
        self.assertEqual(self.form.data['weight'], 87.5)

    def test_form_deserialize_date(self):
        values = {'default': 'test', 'age': '16', 'birthday': '1998-02-01'}
        self.form.validate(values)
        self.assertEqual(self.form.data['birthday'], datetime.date(1998, 2, 1))

    def test_form_deserialize_string(self):
        values = {'default': 'test', 'age': '16', 'birthday': '1998-02-01'}
        self.form.validate(values)
        self.assertEqual(self.form.data['default'], 'test')

    def test_form_save(self):
        values = {'default': 'test', 'age': '16', 'birthday': '1998-02-01'}
        self.assertEqual(self.form.validate(values), True)

    def test_form_save_without_validation(self):
        self.assertRaises(StateError, self.form.save)


class TestFormRenderer(unittest.TestCase):

    def setUp(self):
        config = Config(parse(XML))
        form_config = config.get_form('customform')
        self.form = Form(form_config)

    def test_form_render(self):
        html = self.form.render()
        self.assertEqual(html, "Hello world")


if __name__ == '__main__':
    unittest.main()
