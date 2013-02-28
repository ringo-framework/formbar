import unittest
from formbar.config import parse, Config, Form

XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<configuration>
    <form id="testform">
    </form>
    <form id="customform" autocomplete="off" method="GET" action="http://"
        enctype="multipart/form-data">
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


if __name__ == '__main__':
    unittest.main()
