import unittest
from formbar.config import parse, Config, Form

XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<configuration>
    <source>
        <entity id="e0" name="default"/>
        <entity id="e1" name="age" type="integer" label="My age"/>
        <entity id="e2" name="birthday" label="My Birthday" type="date"
            autocomplete="off" css="datefield" number="1" readonly="true" />
    </source>
    <form id="testform">
    </form>
    <form id="customform" autocomplete="off" method="GET" action="http://"
        enctype="multipart/form-data">
        <row><col><field ref="e0"/></col></row>
        <row><col>
            <field ref="e1"/>
        </col></row>
        <row><col>
            <field ref="e2"/>
        </col></row>
    </form>
    <form id="ambigous">
    </form>
    <form id="ambigous">
    </form>
</configuration>
"""


class TestConfigParser(unittest.TestCase):

    def setUp(self):
        tree = parse(XML)
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
        tree = parse(XML)
        self.config = Config(tree)
        self.dform = self.config.get_form('testform')
        self.cform = self.config.get_form('customform')

    def test_get_fields(self):
        self.assertTrue(isinstance(self.cform.get_fields(), dict))
        self.assertEqual(len(self.cform.get_fields().items()), 3)

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


class TestFieldConfig(unittest.TestCase):

    def setUp(self):
        tree = parse(XML)
        self.config = Config(tree)
        self.form = self.config.get_form('customform')
        self.dfield = self.form.get_field('default')
        self.cfield = self.form.get_field('birthday')

    def test_get_field_mission(self):
        self.assertRaises(KeyError, self.form.get_field, 'missing')

    def test_autocomplete_default(self):
        self.assertEqual(self.dfield.autocomplete, 'on')

    def test_autocomplete_custom(self):
        self.assertEqual(self.cfield.autocomplete, 'off')

    def test_css_default(self):
        self.assertEqual(self.dfield.css, '')

    def test_css_custom(self):
        self.assertEqual(self.cfield.css, 'datefield')

    def test_label_default(self):
        self.assertEqual(self.dfield.label, self.dfield.name.capitalize())

    def test_label_custom(self):
        self.assertEqual(self.cfield.label, 'My Birthday')

    def test_number_default(self):
        self.assertEqual(self.dfield.number, '')

    def test_number_custom(self):
        self.assertEqual(self.cfield.number, '1')

    def test_type_default(self):
        self.assertEqual(self.dfield.type, 'string')

    def test_type_custom(self):
        self.assertEqual(self.cfield.type, 'date')

    def test_id_default(self):
        self.assertEqual(self.dfield.id, 'e0')

    def test_id_custom(self):
        self.assertEqual(self.cfield.id, 'e2')

    def test_name_default(self):
        self.assertEqual(self.dfield.name, 'default')

    def test_name_custom(self):
        self.assertEqual(self.cfield.name, 'birthday')

    def test_renderer_default(self):
        self.assertEqual(self.dfield.renderer, None)

    def test_renderer_custom(self):
        self.assertEqual(self.cfield.renderer, None)

    def test_help_default(self):
        self.assertEqual(self.dfield.help, None)

    def test_help_custom(self):
        self.assertEqual(self.cfield.help, None)

    def test_rules_default(self):
        self.assertEqual(len(self.dfield.rules), 0)

    def test_rules_custom(self):
        self.assertEqual(len(self.cfield.rules), 0)

if __name__ == '__main__':
    unittest.main()
