import os
import datetime
import unittest

from formbar import test_dir
from formbar.config import load, Config
from formbar.form import Form, StateError

RESULT = """<div class="formbar-form"><form id="customform" class="testcss" method="GET" action="http://" autocomplete="off" >    \n        <div class="row-fluid"><tr>\n      \n        \n        <div class="span12">\n      \n\n        \n        \n        <label for="string">\n          String field\n        </label>\n          <input class="" id="string" name="DummyItem--string" type="text" />\n\n        </div>\n\n        </div>\n        \n          \n        \n        <div class="row-fluid"><tr>\n      \n        \n        <div class="span12">\n      \n\n        \n        \n        <label for="default">\n          Default\n        </label>\n          <input class="" id="default" name="DummyItem--default" type="text" />\n\n        </div>\n\n        </div>\n        <div class="row-fluid"><tr>\n      \n        \n        <div class="span6">\n      \n\n        \n        \n        <label for="float">\n          Float field\n        </label>\n          <input class="" id="float" name="DummyItem--float" type="text" />\n        <div class="text-help">\n          <i class="icon-info-sign"></i>\n          This is is a very long helptext which should span over\n      multiple rows. Further the will check if there are further html\n      tags allowed.\n        </div>\n\n        </div>\n        \n        <div class="span6">\n      \n\n        \n        \n        <label for="date">\n          Date field\n        </label>\n          <div class="readonlyfield">\n            &nbsp;\n          </div>\n        <div class="text-help">\n          <i class="icon-info-sign"></i>\n          This is my helptext\n        </div>\n\n        </div>\n\n        </div>\n        \n          \n        \n        <div class="row-fluid"><tr>\n      \n        \n        <div class="span6">\n      \n\n        \n        \n        <label for="string">\n          String field\n        </label>\n          <input class="" id="string" name="DummyItem--string" type="text" />\n\n        </div>\n        \n        <div class="span6">\n      \n\n        \n        \n        <label for="integer">\n          Integer field\n            <a href="#" data-toggle="tooltip" class="formbar-tooltip" data-original-title="Required field"><i class="icon-asterisk"></i></a>\n        </label>\n          <input class="" id="integer" name="DummyItem--integer" type="text" />\n\n        </div>\n\n        </div>\n\n\n\n\n\n<script>\n  $(\'.formbar-tooltip\').tooltip();\n</script>\n<div class="row-fluid"><div class="span12 button-pane well-small"><button type="submit" class="btn btn-primary">Submit</button><button type="reset" class="btn btn-warning">Reset</button></div></div></form></div>"""


class TestFormValidation(unittest.TestCase):

    def setUp(self):
        tree = load(os.path.join(test_dir, 'form.xml'))
        config = Config(tree)
        form_config = config.get_form('customform')
        self.form = Form(form_config)

    def test_form_init(self):
        pass

    def test_form_unknown_field(self):
        values = {'unknown': 'test', 'integer': '15', 'date': '1998-02-01'}
        self.assertRaises(KeyError, self.form.validate, values)

    def test_form_validate_fail(self):
        values = {'default': 'test', 'integer': '15', 'date': '1998-02-01'}
        self.assertEqual(self.form.validate(values), False)

    def test_form_validate_ok(self):
        values = {'default': 'test', 'integer': '16', 'date': '1998-02-01'}
        self.assertEqual(self.form.validate(values), True)

    def test_form_deserialize_int(self):
        values = {'default': 'test', 'integer': '16', 'date': '1998-02-01'}
        self.form.validate(values)
        self.assertEqual(self.form.data['integer'], 16)

    def test_form_deserialize_float(self):
        values = {'default': 'test', 'integer': '16',
                  'date': '1998-02-01', 'float': '87.5'}
        self.assertEqual(self.form.validate(values), True)
        self.assertEqual(self.form.data['float'], 87.5)

    def test_form_deserialize_date(self):
        values = {'default': 'test', 'integer': '16', 'date': '1998-02-01'}
        self.form.validate(values)
        self.assertEqual(self.form.data['date'], datetime.date(1998, 2, 1))

    def test_form_deserialize_string(self):
        values = {'default': 'test', 'integer': '16', 'date': '1998-02-01'}
        self.form.validate(values)
        self.assertEqual(self.form.data['default'], 'test')

    def test_form_save(self):
        values = {'default': 'test', 'integer': '16', 'date': '1998-02-01'}
        self.assertEqual(self.form.validate(values), True)

    def test_form_save_without_validation(self):
        self.assertRaises(StateError, self.form.save)


class TestFormRenderer(unittest.TestCase):

    def setUp(self):
        tree = load(os.path.join(test_dir, 'form.xml'))
        config = Config(tree)
        form_config = config.get_form('customform')
        self.form = Form(form_config)

    def test_form_render(self):
        html = self.form.render()
        self.assertEqual(html, RESULT)


if __name__ == '__main__':
    unittest.main()
