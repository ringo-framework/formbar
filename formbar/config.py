import gettext
import logging
import xml.etree.ElementTree as ET
from formbar.rules import Rule

log = logging.getLogger(__name__)
_ = gettext.gettext



def load(path):
    """Return the parsed XML form the given file. The function will load
    the file located in path and than returns the parsed content."""
    with open(path) as f:
        data = f.read()
        return parse(data)


def parse(xml):
    """Returns the parsed XML. This is a helper function to be used in
    connection with loading the configuration files.
    :xml: XML string to be parsed
    :returns: DOM of the parsed XML

    """
    if isinstance(xml, unicode):
        xml = xml.encode("utf-8")
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

    def get_elements(self, name):
        """Returns a list of all elements found in the tree with the given
        name. If no elements can be found. Return an empty list.

        :name: name of the elements to be found
        :returns: list of elements

        """
        qstr = ".//%s" % (name)
        return self._tree.findall(qstr)

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
        """Returns a :class:`.Form` instance with the configuration for a form
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
        return Form(element, self)


class Form(Config):
    """Class for accessing the configuration of a specific form. The form
    configuration only provides a subset of available attributes for forms."""

    def __init__(self, tree, parent):
        """Initialize a form configuration with the DOM tree of a XML form
        configuration. On initialisation the form will be configured that means
        that all included fields will be configured.

        :tree: XML DOM tree of the form configuration.
        :parent: XML DOM tree of the parent configuration.

        """
        Config.__init__(self, tree)

        self._parent = parent
        """Reference to parent configuration"""

        self.id = tree.attrib.get('id', '')
        """id. ID of the form"""

        self.readonly = tree.attrib.get('readonly', 'false') == 'true'
        """Flag to set the form as a readonly form. If set all fields in
        the form.  will be rendered as a simple textfield which does not
        allow to change or enter any data. Defaults to False"""

        self.css = tree.attrib.get('css', '')
        """css. CSS class(es) to be added to the form"""

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

        self._id2name = {}
        """Dictionary with a mapping of id to fieldnames"""

        self._initialized = False
        """Flag to indicate that the form has been setup"""

        self._buttons = self.get_buttons()
        """Buttons of the form"""
        self._fields = self.get_fields()
        self._initialized = True
        """Dictionary with all fields in the form. The name of the field is the
        key in the dictionary"""

    def get_buttons(self, root=None):
        # Get all Buttons for the form.
        buttons = []
        if root is None:
            root = self._tree
        for b in root.findall('.//button'):
            buttons.append(b)
        return buttons

    def get_pages(self, root=None):
        # Get all fields for the form.
        pages = []

        if root is None:
            root = self._tree

        # Search for fields
        for p in root.findall('.//page'):
            pages.append(p)

        # Now search for snippets
        for s in root.findall('.//snippet'):
            sref = s.attrib.get('ref')
            if sref:
                s = self._parent.get_element('snippet', sref)
                pages.extend(self.get_pages(s))
        return pages

    def walk(self, root, values, evaluate=False):
        """Will walk the tree recursivley and yields every field node.
        If evaluate parameter is true, then the function will only
        return fields which are relevant after the conditionals in the
        form has been evaluated.

        :root: Root node
        :values: Dictionary with values which are used for evaluating
        conditionals.
        :evaluate: Flag to indicate if evaluation should be done on
        conditionals
        :returns: yields field elements

        """
        for child in root:
            if len(child) > 0:
                if child.tag == "if":
                    rule = Rule(child.attrib.get('expr'))
                    if evaluate and not rule.evaluate(values):
                        continue
                    for elem in self.walk(child, values, evaluate):
                        yield elem
                else:
                    for elem in self.walk(child, values, evaluate):
                        yield elem
            elif child.tag == "snippet":
                sref = child.attrib.get('ref')
                if sref:
                    snippet = self._parent.get_element('snippet', sref)
                    for elem in self.walk(snippet, values, evaluate):
                        yield elem
            elif child.tag == "field":
                yield child

    def get_fields(self, root=None, values={},
                   reload_fields=False, evaluate=False):
        """Returns a dictionary of included fields in the form. Fields fetched
        by searching all field elements in the form or snippets and
        "subsnippets" in the forms.

        :returns: A dictionary with the configured fields in the form. The name
        of the field is the key of the dictionary.
        """

        # Are the fields already initialized? Ignore cache if we get
        # fields for a particular page
        if self._initialized and root is None and reload_fields is False:
            return self._fields

        # Get all fields for the form.
        fields = {}

        if root is None:
            root = self._tree

        for node in self.walk(root, values, evaluate):
            ref = node.attrib.get('ref')
            entity = self._parent.get_element('entity', ref)
            field = Field(entity)
            # Inherit readonly flag to all fields in this field.
            if self.readonly:
                field.readonly = self.readonly
            fields[field.name] = field
            self._id2name[ref] = field.name
        return fields

    def get_field(self, name):
        """Returns the field with the name from the form. If the field can not
        be found a KeyError is raised.

        :name: name of the field to get
        :returns: ``Field``
        """

        fields = self.get_fields()
        try:
            return fields[name]
        except KeyError, e:
            log.error('Tried to get field "%s"'
                      ' which is not included in the form' % name)
            raise e


class Field(Config):
    """Configuration of a Field"""

    def __init__(self, entity):
        """Inits a field with the entity DOM element.

        :entity: entity DOM element

        """
        Config.__init__(self, entity)

        # Attributes of the field
        self.id = entity.attrib.get('id')
        """Id of the field. Usally only used to refer to the field.
        Example labels."""

        self.name = entity.attrib.get('name', "")
        """Name of the field. values will be submitted using this name"""

        self.label = entity.attrib.get('label', self.name.capitalize())
        """Label of the field. If no label is provied the a capitalized
        form of the name is used. To not render a label at all define a
        label with an empty string."""

        self.number = entity.attrib.get('number', '')
        """A ordering number for the field. In some form it is helpfull
        to be able to refer to a specific field by its number. The
        number will be rendered next to the label of the field."""

        self.type = entity.attrib.get('type')
        """The datatype for this field. The data type is important for
        converting the submitted data into a python value. Note that
        this option is ignored if the form is used to render an
        SQLAlchemy mapped item."""

        self.css = entity.attrib.get('css', '')
        """A string which will be added to the class tag of the form"""

        self.required = entity.attrib.get('required', 'false') == 'true'
        """Flag to mark the field as a required field. If this tag is
        set an additional rule will be added to the field and an astrix
        is rendered at the label of the field. Note that this option
        might not be needed to be set if the form is used to render a
        SQLAlchemy mapped item as this. In this case the required flag
        is already set by the underlying FormAlchemy library by checking
        if the database field is 'NOT NULL'. Defaults to False"""

        self.desired= entity.attrib.get('desired', 'false') == 'true'
        """Flag to mark the field as a desired field. If this tag is
        set an additional rule will be added to the field and an star
        symbol is rendered at the label of the field. Defaults to
        False"""

        self.readonly = entity.attrib.get('readonly', 'false') == 'true'
        """Flag to set the field as a readonly field. If set the field
        will be rendered as a simple textfield which does not allow to
        change or enter any data. Defaults to False"""

        self.autocomplete = entity.attrib.get('autocomplete', 'on')
        """Flag to enable or disable the automcomplete feature for this
        field. Defaults to enabled autocompletion"""

        self.value = entity.attrib.get('value', "")
        """Default value of the field. Note that this value might be
        overwritten while rendering the form if the field is within the
        submitted values on a form submission. Defaults to empty
        string. This attribute is also used for Infofields to define the
        value which should be displayed (If no expression is defined)"""

        self.tags = []
        """Tags of the field. Fields can have tags. Tags can be used to
        mark fields in the form and become handy if a application wants
        to find fields having a specific tag."""
        for tag in entity.attrib.get('tags', "").split(","):
            if tag:
                self.tags.append(tag.strip())

        # Subelements of the fields
        # Options (For dropdown, checkbox and radio fields)
        self.options = []
        options = entity.find('options')
        if not self.value and options is not None and options.attrib.get('value'):
            self.options = options.attrib.get('value')
        elif options is not None:
            for option in options:
                self.options.append((option.text, option.attrib.get('value')))

        # Help
        self.help = None
        help = entity.find('help')
        if help is not None:
            self.help = help.text

        # Renderer
        self.renderer = None
        renderer_config = entity.find('renderer')
        if renderer_config is not None:
            self.renderer = Renderer(renderer_config)

        # Get rules
        self.rules = []
        # Add automatic genertated rules based on the required or
        # desired flag
        if self.required:
            expr = "bool($%s)" % self.name
            msg = _("This field is required. You must provide a value")
            mode = "pre"
            self.rules.append(Rule(expr, msg, mode))
        if self.desired:
            expr = "bool($%s)" % self.name
            msg = _("This field is desired. Pleas provide a value")
            mode = "pre"
            triggers = "warning"
            self.rules.append(Rule(expr, msg, mode, triggers))
        # Add rules added the the field.
        for rule in self._tree.findall('rule'):
            expr = rule.attrib.get('expr')
            msg = rule.attrib.get('msg')
            mode = rule.attrib.get('mode')
            triggers = rule.attrib.get('triggers')
            self.rules.append(Rule(expr, msg, mode, triggers))



class Renderer(Config):
    """Configuration class for FieldRenderers. This class gives an
    interface to the Renderer configuration for fields if the field
    should be rendererd differently than the standard way."""

    def __init__(self, entity):
        """@todo: to be defined """
        Config.__init__(self, entity)

        # Attributes of the Renderer
        self.render_type = entity.attrib.get('type')
        """
        Type of the Renderer. Known Renderers:
        - Datepicker
        - Textarea
        - HTML
        """
        self.label_position = "top"
        """Optional. If defined the label will placed left, top
        or right to the field.  Defaults to top"""
        self.label_align = "left"
        """Optional. If defined the label will be aligned left or right,
        Defaults to left This only applies for lables which are
        positioned on the left or right side"""
        self.label_width = 2
        """Optional. If defined the label will have the defined width.
        Defaults to 2 cols. The Fieldwidth will be reduced by the label
        width. This only applies for lables which are positioned on the
        left or right side."""
        label_config = entity.find('label')
        if label_config is not None:
            self.label_position = label_config.attrib.get("position") or "top"
            if self.label_position == "left":
                self.label_align = label_config.attrib.get("align") or "right"
            elif self.label_position == "right":
                self.label_align = label_config.attrib.get("align") or "left"
            self.label_width = int(label_config.attrib.get("width") or 2)

        # Warning! The body of the renderer may include all valid and
        # invalid html data including scripting. Use with caution here as
        # this may become a large security hole if some users inject
        # malicious code!
        self.body = None
        """The body attribute is currently only used by the HTML
        Renderer and has the content to be rendererd."""
        if self.render_type == "html" and len(entity) > 0:
            self.body = ET.tostring(entity[0], method="html")

    def __getattr__(self, name):
        return self._tree.attrib.get(name)
