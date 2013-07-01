#@TODO: Write tests for the formalchemy helpers.
import logging
import formalchemy
from formalchemy.fields import (
    TextFieldRenderer,
    IntegerFieldRenderer,
    PasswordFieldRenderer,
    TextAreaFieldRenderer,
    EmailFieldRenderer,
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
        fa_field = formalchemy.Field()
        setattr(cls, name, fa_field)


def get_data(fs):
    """Returns a dictionary with the data of the given fieldset.


    :fs: Fieldset.
    :returns: Dictionary with the values of the fieldset.

    """
    values = {}
    for field in fs.render_fields.values():
        values[field.key] = field.value
    return values


def set_renderer(field, config):
    """Returns the field with optionally changed renderer. The Renderer
    is depending of the given field

    :field: Configured FA field.
    :config: configuration of the field.
    :returns: Renderer.

    """
    datatype = config.type.lower()
    # If there are any options configured for the field user a
    # dropdown field on default.
    if len(config.options) > 0:
        if config.options_display == 'dropdown':
            field = field.dropdown(options=config.options)
        # TODO: Radio and Checkbox fields causes and error. See
        # issue #2
        elif config.options_display == 'radio':
            field = field.radio(options=config.options)
        elif field.options_display == 'checkbox':
            field = field.checkbox(options=config.options)
    elif datatype == 'text':
        field = field.with_renderer(TextFieldRenderer)
    elif datatype == 'email':
        field = field.with_renderer(EmailFieldRenderer)
    elif datatype == 'integer':
        field = field.with_renderer(IntegerFieldRenderer)
    elif datatype == 'float':
        field = field.with_renderer(TextFieldRenderer)
    elif datatype == 'decimal':
        field = field.with_renderer(TextFieldRenderer)
    elif datatype == 'textarea':
        field = field.with_renderer(TextAreaFieldRenderer)
    elif datatype == 'password':
        field = field.with_renderer(PasswordFieldRenderer)
    return field


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
                                       config.get_field(name))
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
                                   config.get_field(field.name))
        fs.append(fa_field)

    return fs


def configure_field(field, config):
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

    # Set the renderer for the field
    field = set_renderer(field, config)

    # Is the field marked to be readonly?
    if config.readonly:
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
