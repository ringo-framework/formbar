#@TODO: Write tests for the formalchemy helpers.
import logging
import formalchemy
from formalchemy.fields import (
    TextFieldRenderer,
    IntegerFieldRenderer,
    PasswordFieldRenderer,
    TextAreaFieldRenderer,
)

log = logging.getLogger(__name__)


class DummyItem(object):
    pass


def populate_dummy_item(cls, config):
    """Will populate the given class with data entities defined in the field
    configuration. This is a helper function used in the ``get_fieldset``
    function."""
    fields = config.get_fields()
    for name, field in fields.iteritems():
        setattr(cls, name, formalchemy.Field())


def get_data(fs):
    """Returns a dictionary with the data of the given fieldset.


    :fs: Fieldset.
    :returns: Dictionary with the values of the fieldset.

    """
    values = {}
    for field in fs.render_fields.values():
        values[field.key] = field.value
    return values


def get_renderer(datatype):
    """Returns the correct Renderer depending of the given datatype

    :datatype: datatype as string.
    :returns: Renderer.

    """
    if datatype == 'text':
        return TextFieldRenderer
    elif datatype == 'integer':
        return IntegerFieldRenderer
    elif datatype == 'float':
        return TextAreaFieldRenderer
    elif datatype == 'decimal':
        return TextAreaFieldRenderer
    elif datatype == 'textarea':
        return TextAreaFieldRenderer
    elif datatype == 'password':
        return PasswordFieldRenderer
    else:
        return None


def get_fieldset(item, config, dbsession=None):
    """Returns a FA fieldset. If an item is provied the fieldset is
    based on the items attributes. If no item is provided a
    ``DummyItem`` is created with the entities defined in the config
    file."""
    # @TODO: Check if it is ok the not include the {Model}-{pk} prefix
    # to the naming in the fieldnames.
    if item is None:
        populate_dummy_item(DummyItem, config)
        fs = formalchemy.FieldSet(DummyItem, format="%(name)s")
    else:
        fs = formalchemy.FieldSet(item, dbsession, format="%(name)s")

    configured_fields = []
    additional_fields = []
    for name, field in config.get_fields().iteritems():
        try:
            fa_field = configure_field(fs[name],
                                       config.get_field(name),
                                       config.readonly)
            configured_fields.append(fa_field)
        except AttributeError:
            # Field is not included in the origin fieldset. So add an
            # additional field to the fs.
            additional_fields.append(field)
            continue

    # Configure the fieldset with the configured fields.
    log.debug("Configured fields: %s" % [f.name for f in configured_fields])
    fs.configure(include=configured_fields)

    # Finally add additional fields
    for field in additional_fields:
        fa_field = configure_field(formalchemy.Field(field.name),
                                   config.get_field(field.name),
                                   config.readonly)
        fs.append(fa_field)

    return fs


def configure_field(field, config, readonly=False):
    """Returns a modified FA field. Function takes a FA field as argument and
    modifies some attributes like the renderer, label and other things dependig
    on the field configuration.

    :field: FormAlchemy field
    :config: Configuration for the field

    """

    additional_html_options = {}
    overwrite_html_options = {}

    # Set label
    field.label_text = config.label

    # Get the renderer for the field
    datatype = config.type.lower()
    renderer = get_renderer(datatype)
    if renderer is not None:
        field = field.with_renderer(renderer)

    # Is the field marked to be readonly?
    if config.readonly or readonly:
        field = field.readonly()

    # Should the field have enabled autocomplete?
    if config.required:
        field = field.required()

    # Should the field have enabled autocomplete?
    if config.autocomplete == "off":
        additional_html_options['autocomplete'] = "off"

#    # Assign validators to the field for basic datetype checks
#    if config.type == "integer":
#        field = field.validate(integer)
#    elif config.type == "float":
#        field = field.validate(float_)
#
    # Added custom css classes
    additional_html_options['class'] = config.css
    field = field.with_html(**additional_html_options)

    # Overwrite the id attribute to make the label working.
    # id would usally be [fieldset_prefix-]ModelName-[pk]-fieldname
    # but we only need the fieldname here
    overwrite_html_options['id'] = config.name
    field = field.attrs(**overwrite_html_options)

    # Setup metadata
    #attr = {}
    #field.with_metadata(**attr)
    return field
