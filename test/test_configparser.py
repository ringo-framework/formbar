import unittest
import os
from formbar import test_dir
from formbar.config import load, Config, Form


class TestConfigParser(unittest.TestCase):

    def setUp(self):
        tree = load(os.path.join(test_dir, 'form.xml'))
        self.config = Config(tree)

    def test_get_ambigous_element_fail(self):
        """ Check if an KeyError is raised on ambigous elements. """
        self.assertRaises(
            KeyError, self.config.get_element, 'form', 'ambigous')

    def test_build_form_fail(self):
        """Check if a ValueError is raised if the Config is not instanciated
        with an ElementTree.Element.
        """
        self.assertRaises(ValueError, Config, None)

    def test_build_form_ok(self):
        pass

    def test_get_form_ok(self):
        """ Check if a Form instance is retrieved. """
        form = self.config.get_form('testform')
        self.assertTrue(isinstance(form, Form))

    def test_get_form_fail(self):
        """ Check if an KeyError is raised. """
        self.assertRaises(KeyError, self.config.get_form, '_testform')


class TestFormParser(unittest.TestCase):

    def setUp(self):
        tree = load(os.path.join(test_dir, 'form.xml'))
        self.config = Config(tree)
        self.dform = self.config.get_form('testform')
        self.cform = self.config.get_form('customform')

    def test_get_fields(self):
        self.assertTrue(isinstance(self.cform.get_fields(), dict))
        self.assertEqual(len(self.cform.get_fields().items()), 9)

    def test_get_field_e1(self):
        field = self.cform.get_field(self.cform._id2name['e1'])
        self.assertEqual(field.id, 'e1')

    def test_autocomplete_default(self):
        self.assertEqual(self.dform.autocomplete, 'on')

    def test_autocomplete_custom(self):
        self.assertEqual(self.cform.autocomplete, 'off')

    def test_method_default(self):
        self.assertEqual(self.dform.method, 'POST')

    def test_method_custom(self):
        self.assertEqual(self.cform.method, 'GET')

    def test_action_default(self):
        self.assertEqual(self.dform.action, '')

    def test_action_custom(self):
        self.assertEqual(self.cform.action, 'http://')

    def test_enctype_default(self):
        self.assertEqual(self.dform.enctype, '')

    def test_enctype_custom(self):
        self.assertEqual(self.cform.enctype, 'multipart/form-data')

    def test_css_default(self):
        self.assertEqual(self.dform.css, '')

    def test_css_custom(self):
        self.assertEqual(self.cform.css, 'testcss')

    def test_readonly_default(self):
        self.assertEqual(self.dform.readonly, False)

    def test_readonly_custom(self):
        self.assertEqual(self.cform.readonly, False)

    def test_id_default(self):
        self.assertEqual(self.dform.id, 'testform')

    def test_id_custom(self):
        self.assertEqual(self.cform.id, 'customform')


class TestFieldConfig(unittest.TestCase):

    def setUp(self):
        tree = load(os.path.join(test_dir, 'form.xml'))
        self.config = Config(tree)
        self.form = self.config.get_form('customform')
        self.form2 = self.config.get_form('userform2')
        self.dfield = self.form.get_field('default')
        self.cfield = self.form.get_field('date')
        self.ifield = self.form.get_field('integer')
        self.sfield = self.form2.get_field('name')
        self.hfield = self.form.get_field('html')
        self.tfield = self.form.get_field('interval')

    def test_get_field_mission(self):
        self.assertRaises(KeyError, self.form.get_field, 'missing')

    def test_autocomplete_default(self):
        self.assertEqual(self.dfield.autocomplete, 'on')

    def test_autocomplete_custom(self):
        self.assertEqual(self.cfield.autocomplete, 'off')

    def test_required_default(self):
        self.assertEqual(self.dfield.required, False)

    def test_requried_custom(self):
        ifield = self.form.get_field('integer')
        self.assertEqual(ifield.required, True)

    def test_desired_default(self):
        self.assertEqual(self.dfield.desired, False)

    def test_desired_custom(self):
        ifield = self.form.get_field('float')
        self.assertEqual(ifield.desired, True)

    def test_readonly_default(self):
        self.assertEqual(self.sfield.readonly, False)

    def test_readonly_custom(self):
        self.assertEqual(self.dfield.readonly, False)

    def test_css_default(self):
        self.assertEqual(self.dfield.css, '')

    def test_css_custom(self):
        self.assertEqual(self.cfield.css, 'datefield')

    def test_label_default(self):
        self.assertEqual(self.dfield.label, self.dfield.name.capitalize())

    def test_label_custom(self):
        self.assertEqual(self.cfield.label, 'Date field')

    def test_number_default(self):
        self.assertEqual(self.dfield.number, '')

    def test_number_custom(self):
        self.assertEqual(self.cfield.number, '1')

    def test_type_default(self):
        self.assertEqual(self.dfield.type, None)

    def test_type_custom(self):
        self.assertEqual(self.cfield.type, 'date')

    def test_id_default(self):
        self.assertEqual(self.dfield.id, 'e0')

    def test_id_custom(self):
        self.assertEqual(self.cfield.id, 'e4')

    def test_name_default(self):
        self.assertEqual(self.dfield.name, 'default')

    def test_name_custom(self):
        self.assertEqual(self.cfield.name, 'date')

    def test_renderer_default(self):
        self.assertEqual(self.dfield.renderer, None)

    def test_renderer_custom(self):
        self.assertNotEqual(self.cfield.renderer, None)

    def test_help_default(self):
        self.assertEqual(self.dfield.help, None)

    def test_help_custom(self):
        self.assertEqual(self.cfield.help, 'This is my helptext')

    def test_rules_default(self):
        self.assertEqual(len(self.dfield.get_rules()), 0)

    def test_rules_custom(self):
        self.assertEqual(len(self.ifield.get_rules()), 2)

    def test_validators_default(self):
        self.assertEqual(len(self.dfield.get_validators()), 0)

    def test_validators_custom(self):
        self.assertEqual(len(self.ifield.get_validators()), 1)

    def test_html_renderer_fails(self):
        """Only html renderer have the body attribute set"""
        self.assertEqual(self.cfield.renderer.body, None)

    def test_html_renderer(self):
        self.assertEqual(self.hfield.renderer.body.strip(), "<div>Test</div>")

    def test_tags_default(self):
        self.assertEqual(self.dfield.tags, [])

    def test_tags_custom(self):
        self.assertEqual(self.hfield.tags, ["tag1", "tag2"])

if __name__ == '__main__':
    unittest.main()
