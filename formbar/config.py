import logging
import xml.etree.ElementTree as ET
log = logging.getLogger(__name__)


def parse(xml):
    """Returns the parsed XML. This is a helper function to be used in
    connection with loading the configuration files.

    :xml: XML string to be parsed
    :returns: DOM of the parsed XML

    """
    return ET.fromstring(xml)


class Config(object):
    """Class for accessing the form configuration file. It provides methods to
    get certain elements from the configuration. """

    def __init__(self, tree):
        """Initialize a configuration with the DOM tree of an XML configuration
        for the form. If tree is not an instance of an ElementTree than raise a
        TypeError

        :tree: XML DOM tree of the configuration file

        """
        if isinstance(tree, ET.Element):
            self._tree = tree
        else:
            err = ('Config must instanciated with a '
                   'ElementTree.Element instance. "%s" was provided' % tree)
            log.error(err)
            raise ValueError(err)

    def get_element(self, name, id):
        """Returns an ``Element`` from the configuration. If the element can
        not be found it returns None. If there are more than one element of
        this name and the id, than raise an KeyException.

        If the intitail found element refers to another element by the 'ref'
        attribute the function is recalled as long as it can find the element.

        :name: Name of the element (e.g entity)
        :id: ID of the element
        :returns: ``Element`` or ``None``.

        """
        qstr = ".//%s" % (name)
        if id:
            qstr += "[@id='%s']" % id
        result = self._tree.findall(qstr)
        if len(result) > 1:
            raise KeyError('Element is ambigous')
        elif len(result) == 1:
            # If the found elements refernces another element than retry
            # getting the refed element
            ref = result[0].attrib.get('ref')
            if ref:
                return self.get_element(name, id=ref)
            return result[0]
        else:
            return None

    def get_form(self, id):
        """Returns a ``FormConfig`` instance with the configuration for a form
        with id in the configuration file. If the form can not be found a
        KeyError is raised.

        :id: ID of the form in the configuration file
        :returns: ``FormConfig`` instance

        """
        element = self.get_element('form', id)
        if element is None:
            err = 'Form with id "%s" can not be found' % id
            log.error(err)
            raise KeyError(err)
        return Form(element)


class Form(Config):
    """Class for accessing the configuration of a specific form. The form
    configuration only provides a subset of available attributes for forms."""

    def __init__(self, tree):
        """Initialize a form configuration with the DOM tree of a XML form
        configuration.

        :tree: XML DOM tree of the form configuration.

        """
        Config.__init__(self, tree)

        self.autocomplete = tree.attrib.get('autocomplete', 'on')
        """autocomplete. Configure the form to autocomplete (prefill) the
        fields in the form. Defaults to 'on'"""

        self.method = tree.attrib.get('method', 'POST')
        """method. HTTP method used for sending the data. Defaults to 'POST'
        Valid values are GET and POST."""

        self.action = tree.attrib.get('action', '')
        """action. URL where to send the data. Defaults to an empty string
        which means send data to the current url again."""

        self.enctype = tree.attrib.get('enctype', '')
        """enctype. Encoding type of the subbmitted values. Use
        'multipart/form-data' if you want to upload files. Defaults to an empty
        string."""
