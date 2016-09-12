import os
import re
import gettext
import logging
import pkg_resources
import xml.etree.ElementTree as ET
from formbar.rules import Rule

log = logging.getLogger(__name__)
_ = gettext.gettext

required_msg = _("This field is required. You must provide a value")
desired_msg = _("This field is desired. Please provide a value")


def get_text_and_html_content(item):
    """Will return the content (body) of an given element including HTML
    content. HTML content must be wrapped in a <html> tag.
    :returns: content of the item.

    """
    if len(item) > 0 and item[0].tag == "html":
        content = ET.tostring(item[0], method="html")
        return content.replace("html>", "span>")
    return item.text


def load(path):
    """Return the parsed XML form the given file. The function will load
    the file located in path and than returns the parsed content."""
    with open(path) as f:
        data = f.read()
        return parse(data, path)


def parse(xml, path=None):
    """Returns the parsed XML. This is a helper function to be used in
    connection with loading the configuration files.
    :xml: XML string to be parsed
    :returns: DOM of the parsed XML

    """
    if isinstance(xml, unicode):
        xml = xml.encode("utf-8")
    tree = ET.fromstring(xml)
    tree = handle_inheritance(tree, path)
    tree = handle_includes(tree, path)
    return tree


def get_file_location(location, basepath):
    if location.startswith("@"):
        path = location.split("/")
        app = pkg_resources.get_distribution(path[0].strip("@")).location
        return os.path.join(app, *path[1::])
    elif not os.path.isabs(location):
        return os.path.join(basepath, location)
    return location


def handle_inheritance(tree, path=None):
    """Will build a form based on a parent form. Will replace elements
    overwritten in the inherited form and add new elements.

    :tree: ElementTree
    :path: Path of the loaded form
    :returns: ElementTree

    """
    if path:
        basepath = os.path.dirname(path)
    else:
        basepath = ""

    if not "inherits" in tree.attrib:
        return tree
    ptree = load(get_file_location(tree.attrib["inherits"], basepath))

    # Workaroutn for missing support of getting parent elements. See
    # http://stackoverflow.com/
    # questions/2170610/access-elementtree-node-parent-node/2170994
    tree_parent_map = {c: p for p in tree.iter() for c in p}
    ptree_parent_map = {c: p for p in ptree.iter() for c in p}

    for element in tree.getiterator():
        if not "id" in element.attrib:
            continue
        # Is there a an element with the same id in the ptree?
        xpath = ".//*[@id='%s']" % element.attrib["id"]
        pelement = ptree.find(xpath)
        if pelement is not None:
            # Replace the parent element with the one in inherited
            # element.
            pparent = ptree_parent_map.get(pelement)
            if pparent is not None:
                pindex = pparent._children.index(pelement)
                pparent._children[pindex] = element
        else:
            # Add the element to the parent tree
            # 1. First get the parent of the new element and get the
            # same element from the parent tree.
            parent = tree_parent_map[element]
            if "id" in parent.attrib:
                xpath = ".//%s[id='%s']" % (parent.tag, parent.attrib["id"])
            else:
                xpath = "%s" % parent.tag

            if parent.tag == "configuration":
                ptree.append(element)
            elif "id" in parent.attrib:
                xpath = ".//%s[id='%s']" % (parent.tag, parent.attrib["id"])
                pelement = ptree.find(xpath)
                pelement.append(element)
            else:
                xpath = "%s" % parent.tag
                pelement = ptree.find(xpath)
                pelement.append(element)

    ptree = handle_includes(ptree, path)
    return ptree


def handle_includes(tree, path):
    """Will replace all include element with the content of the include
    file.

    :tree: ElementTree
    :path: Path of the loaded form
    :returns: ElementTree

    """
    if path:
        basepath = os.path.dirname(path)
    else:
        basepath = ""

    # Workaroutn for missing support of getting parent elements. See
    # http://stackoverflow.com/
    # questions/2170610/access-elementtree-node-parent-node/2170994
    parent_map = {c: p for p in tree.iter() for c in p}
    # handle includes in form
    for include_placeholder in tree.findall(".//include"):
        location = include_placeholder.attrib["src"]
        entity_prefix = include_placeholder.attrib.get("entity-prefix")
        element = include_placeholder.attrib.get("element")
        include_tree = load(get_file_location(location, basepath))

        if entity_prefix is not None:
            include_tree = handle_entity_prefix(include_tree, entity_prefix)

        if element is not None:
            include_tree = include_tree.find(".//*[@id='%s']" % element)
        parent = parent_map[include_placeholder]
        index = parent._children.index(include_placeholder)
        # Check if the content to be included is wrapped in a
        # 'configuration' section.
        if include_tree.tag == "configuration":
            parent.remove(parent._children[index])
            for child in include_tree:
                parent.append(child)
        else:
            parent._children[index] = include_tree
    return tree


def handle_entity_prefix(tree, prefix):

    # Collect name of fields which are defined in this form. This is
    # used as we only want to handle prefixes on fieldname and
    # expression for fields which are defined in the form.
    fieldnames = [f.get("name") for f in tree.findall(".//entity")]

    def replace_fieldnames(expr, prefix, fieldnames):
        # TODO: Handle % and @ variables to? (ti) <2015-12-17 09:30>
        # Note: This algorithmn is hackish and handles some corner cases
        # with replacements of similar fields names.
        #
        # Example:
        # Consider the following expr = "$foo and $foo_bar" And we want
        # to add a prefix "baz".
        #
        # The code will iterate over all unique fields in the expression
        # and replaces the fieldname with prefix+fieldname.
        #
        # Problem:
        # If we start with the longest field name first the in first
        # iteration the expression looks like this:
        # $foo and $baz.foo_bar.
        # With the next iteration on "foo" the expression will look like
        # this:
        # $baz.foo and $baz.baz.foo_bar with is obvsisouly wrong because
        # of the double baz.baz.
        #
        # Solution:
        # To handle this problem we sort the fields in the expression to
        # start with the shortest fieldname. The the result looks like
        # this on the first iteration:
        # $baz.foo and $baz.foo_bar.
        # Note the replacing "foo" also replaces "foo_bar".
        # Now on the next iteration of "foo_bar" we check if there is
        # already a prefixed version of this in the expression. If so we
        # ignore the replacement to prevent double prefixes.
        fields = re.findall(r'\$[\.\w]+', expr)
        fields = sorted(set(fields), key=lambda x: len(x))
        for field in fields:
            field = field.strip("$")
            # Only replace name of fields which has has been defined in
            # this tree or it is been already replaced.
            if field not in fieldnames or prefix+field in expr:
                continue
            expr = expr.replace(field, prefix+field)
        return expr

    # Handle fields
    for field in tree.findall(".//entity"):
        field.attrib["name"] = prefix+field.attrib["name"]
    # Handle rules
    for rule in tree.findall(".//rule"):
        rule.attrib["expr"] = replace_fieldnames(rule.attrib["expr"],
                                                 prefix, fieldnames)
    # Handle conditional
    for cond in tree.findall(".//if"):
        cond.attrib["expr"] = replace_fieldnames(cond.attrib["expr"],
                                                 prefix, fieldnames)
    return tree


def flatten_form_fields(fields, root=None):
    """Refacoring helper method. Currently the fields dictionary of the
    for saves all fields in a dictionary with fields per page. This
    method will flatten the given given fields dictionary removing
    the page information. I a root (page) is given only the fields
    for the given page are returned.

    TODO: Make this method obsolete by changing the datastructure of the
    fields dictionary. Save mapping of page2fields in a separate
    varibale (ti) <2016-01-11 16:44>
    """
    if root is None:
        tmpfields = {}
        for page in fields:
            for field in fields[page]:
                tmpfields[field] = fields[page][field]
        return tmpfields
    else:
        page_id = root.attrib.get("id")
        return fields[page_id]


def filter_form_fields(form, fields, values=None):
    """Refacoring helper method. Will a return dictiony of fields which
    are in 'active' conditionals.  Active means the expression in the
    conditional will evaluate to true using the given set of values."""
    if values is None:
        values = {}
    # FIXME: The only way get only fields which are
    # relevant (e.g in evaluable conditionals) is to "reinit"
    # the fields.
    filtered_fields = flatten_form_fields(form.init_fields(values,
                                                           evaluate=True))
    tmp_fields = {}
    for fieldname, field in fields.iteritems():
        if fieldname in filtered_fields:
            tmp_fields[fieldname] = field
    return tmp_fields


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
            raise KeyError('Element is ambigous %s:' % id)
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
        self._fields = self.init_fields()
        self._initialized = True
        """Dictionary with all fields per page in a dictionary.
        {
            "p1": [<formbar.config.Field>, ...],
            "p2": [<formbar.config.Field>, ...]
        }
        """

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

    def walk(self, root, values, evaluate=False, include_layout=False):
        """Will walk the tree recursivley and yields every field node.
        Optionally you can yield every layout elements too.  If evaluate
        parameter is true, then the function will only return fields
        which are relevant after the conditionals in the form has been
        evaluated.

        :root: Root node
        :values: Dictionary with values which are used for evaluating
        conditionals.
        :evaluate: Flag to indicate if evaluation should be done on
        conditionals
        :include_layout: Flag to indicate to include layout elements
        too.
        :returns: yields field elements

        """
        for child in root:
            if len(child) > 0:
                if child.tag == "if":
                    rule = Rule(child.attrib.get('expr'))
                    try:
                        if evaluate and not rule.evaluate(values):
                            continue
                    except TypeError:
                        # FIXME: This error can happen if the rule
                        # refers to values which are not contained in
                        # the provided values dictionary. The value
                        # might be missing because the converting of the
                        # value failed or the value was missing at
                        # all.(e.g the field was a selection field and
                        # was "disabled" in a conditional. In this case
                        # the value is not sent. (ti) <2015-04-28 16:52>
                        continue
                    for elem in self.walk(child, values,
                                          evaluate, include_layout):
                        yield elem
                elif include_layout and child.tag in ["section",
                                                      "subsection"]:
                    yield child
                    for elem in self.walk(child, values,
                                          evaluate, include_layout):
                        yield elem
                else:
                    for elem in self.walk(child, values,
                                          evaluate, include_layout):
                        yield elem
            elif child.tag == "snippet":
                sref = child.attrib.get('ref')
                if sref:
                    snippet = self._parent.get_element('snippet', sref)
                    for elem in self.walk(snippet, values,
                                          evaluate, include_layout):
                        yield elem
            elif child.tag == "field":
                yield child

    def init_fields(self, values=None, evaluate=False):
        """Will return the fields in the form as a dictionary. The
        dicionary will containe all fields per page to make the access
        to the fields on a page faster (e.g get_errors and get_warnings):

        {
            "p1": [<formbar.config.Field>, ...],
            "p2": [<formbar.config.Field>, ...]
        }

        Fields fetched by searching all field elements in the form or
        snippets and "subsnippets" in the forms.

        The attribute ``values`` and ``evaluate`` are used for
        evaluating the rules on initialisation to only include relevant
        fields.
        """
        if values is None:
            values = {}
        fields = {}
        pages = self.get_pages()
        if len(pages) == 0:
            pages.append(self._tree)
        for page in pages:
            page_id = page.attrib.get("id")
            fields[page_id] = {}
            for node in self.walk(page, values, evaluate):
                ref = node.attrib.get('ref')
                entity = self._parent.get_element('entity', ref)
                field = Field(entity)
                # Inherit readonly flag to all fields in this field.
                if self.readonly:
                    field.readonly = self.readonly
                fields[page_id][field.name] = field
                self._id2name[ref] = field.name
        return fields

    def get_fields(self, root=None, values={}, evaluate=False):
        """Returns a dictionary of included fields in the form.

        :returns: A dictionary with the configured fields in the form.
        The name of the field is the key of the dictionary.
        """

        # TODO: Move filtering (evaluation) out of this method ()
        # <2016-01-11 15:33>
        if not self._initialized:
            self._fields = self.init_fields(values)
        fields = flatten_form_fields(self._fields, root)
        if evaluate:
            fields = filter_form_fields(self, fields, values)
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

        self.placeholder = entity.attrib.get('placeholder')
        """Defines a placeholder for this field that overrides the default
        placeholder."""

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

        self.desired = entity.attrib.get('desired', 'false') == 'true'
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

        self.autofocus = entity.attrib.get('autofocus', 'false') == 'true'
        """Flag to enable focusing the field on pageload. Note that only
        one field in the form can have the autofocus attribute."""

        self.value = entity.attrib.get('value', u"")
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
        if not self.value \
           and options is not None \
           and options.attrib.get('value'):
            self.options = options.attrib.get('value')
        elif options is not None:
            for option in options:
                self.options.append((option.text,
                                     option.attrib.get('value'),
                                     option.attrib))

        # Help
        self.help = None
        help_item = entity.find('help')
        if help_item is not None:
            self.help_display = help_item.attrib.get("display", "tooltip")
            self.help = get_text_and_html_content(help_item)

        # Renderer
        self.renderer = None
        renderer_config = entity.find('renderer')
        if renderer_config is not None:
            self.renderer = Renderer(renderer_config)

    def get_rules(self):
        rules = []
        # Add automatic genertated rules based on the required or
        # desired flag
        if self.required:
            expr = "bool($%s)" % self.name
            mode = "pre"
            rules.append(Rule(expr, required_msg, mode))
        if self.desired:
            expr = "bool($%s)" % self.name
            mode = "pre"
            triggers = "warning"
            rules.append(Rule(expr, desired_msg, mode, triggers))
        # Add rules added the the field.
        for rule in self._tree.findall('rule'):
            expr = rule.attrib.get('expr')
            msg = rule.attrib.get('msg')
            mode = rule.attrib.get('mode')
            triggers = rule.attrib.get('triggers')
            rules.append(Rule(expr, msg, mode, triggers))
        return rules

    def get_validators(self):
        validators = []
        for validator in self._tree.findall('validator'):
            # Import dynamically the validator
            src = validator.attrib.get("src")
            msg = validator.attrib.get("msg")
            validators.append((src, msg))
        return validators


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
        self.elements_indent = entity.attrib.get("indent", "")
        """Optional if set the field and help elements will be have a
        small indent. The value of the attribute defines the style.
        Currently only applies to the Radio renderer if label alignment
        is 'top'."""
        self.indent_style = ""
        self.indent_border = ""
        self.indent_width = "indent-sm"
        if self.elements_indent:
            style = self.elements_indent.split("-")[0]
            self.indent_style = "indent-%s" % style
        if self.elements_indent.find("bordered") > -1:
            self.indent_border = "indent-bordered"
        if self.elements_indent.find("lg") > -1:
            self.indent_width = "indent-lg"
        if self.elements_indent.find("md") > -1:
            self.indent_width = "indent-md"
        self.label_background = ""
        """Optional. If defined the label will get a light background
        color"""
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
        self.number = "left"
        """Optional. Position of the number in the label. Can be `left`
        or `right`. Defaults to `left`"""
        label_config = entity.find('label')
        if label_config is not None:
            self.number = label_config.attrib.get("number") or "left"
            self.label_position = label_config.attrib.get("position") or "top"
            if label_config.attrib.get("background") == "true":
                self.label_background = "background"
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
