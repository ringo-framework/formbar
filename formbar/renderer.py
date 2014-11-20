import logging
import difflib

from mako.lookup import TemplateLookup
from formbar import template_dir

template_lookup = TemplateLookup(directories=[template_dir])

log = logging.getLogger(__name__)


def get_renderer(field, translate):
    """Returns a Renderer. The renderer is choosen based on the
    configured renderer in the field configuration. If no renderer is
    configured the default FormAlchemy-Renderer is returned.

    :field: Field
    :translate: translation function
    :returns: Renderer

    """
    renderer = field._config.renderer
    if renderer is not None:
        # if there is a external Renderer defined for the given renderer
        # type then use this one.
        if field._form.external_renderers.has_key(renderer.render_type):
            return field._form.external_renderers.get(renderer.render_type)(field, translate)
        if renderer.render_type == "textarea":
            return TextareaFieldRenderer(field, translate)
        elif renderer.render_type == "info":
            return InfoFieldRenderer(field, translate)
        elif renderer.render_type == "dropdown":
            return DropdownFieldRenderer(field, translate)
        elif renderer.render_type == "selection":
            return SelectionFieldRenderer(field, translate)
        elif renderer.render_type == "radio":
            return RadioFieldRenderer(field, translate)
        elif renderer.render_type == "checkbox":
            return CheckboxFieldRenderer(field, translate)
        elif renderer.render_type == "datepicker":
            return DateFieldRenderer(field, translate)
        elif renderer.render_type == "password":
            return PasswordFieldRenderer(field, translate)
        elif renderer.render_type == "hidden":
            return HiddenFieldRenderer(field, translate)
        elif renderer.render_type == "html":
            return HTMLRenderer(field, translate)
        elif renderer.render_type == "formbareditor":
            return FormbarEditorRenderer(field, translate)
    else:
        # Try to determine the datatype of the field and set approriate
        # renderer.
        dtype = field.get_type()
        if dtype == "manytoone":
            return DropdownFieldRenderer(field, translate)
        elif dtype in ['manytomany', 'onetomany']:
            return SelectionFieldRenderer(field, translate)
        elif dtype == "date":
            return DateFieldRenderer(field, translate)
        elif dtype == "file":
            return FileFieldRenderer(field, translate)
        elif dtype == "time":
            return TimeFieldRenderer(field, translate)
        elif dtype == "email":
            return EmailFieldRenderer(field, translate)
    return TextFieldRenderer(field, translate)


class Renderer(object):
    """Basic renderer to render Form objects."""

    def render(self):
        """Returns the rendered element as string

        :returns: Rendered string of the element

        """
        return ""


class FormRenderer(Renderer):
    """Renderer for forms. The renderer will build the the HTML for the
    provided form instance."""

    def __init__(self, form, translate):
        """@todo: to be defined

        :form: @todo
        :translate: Function which return a translated string for a
        given msgid.

        """
        Renderer.__init__(self)

        self._form = form
        self.translate = translate
        self.template = template_lookup.get_template("form.mako")

    def render(self, buttons=True, outline=True):
        """Returns the rendered form as string.

        :buttons: Boolean flag to indicate if the form buttons should be
        rendererd. Defaults to true.
        :outline: Boolean flag to indicate that the outline for pages
        should be rendered. Defaults to true.
        :returns: rendered form.

        """
        html = []
        html.append(self._render_form_start())
        html.append(self._render_form_body(outline))
        if not self._form._config.readonly and buttons:
            html.append(self._render_form_buttons())
        html.append(self._render_form_end())
        return "".join(html)

    def _render_form_start(self):
        html = []
        html.append('<div class="formbar-form">')
        attr = {'id': self._form._config.id,
                'css': self._form._config.css,
                'action': self._form._config.action,
                'method': self._form._config.method,
                'autocomplete': self._form._config.autocomplete,
                'enctype': self._form._config.enctype,
                'evalurl': self._form._eval_url or "",
                '_': self.translate}
        html.append('<form id="%(id)s" class="%(css)s" role="form" '
                    'method="%(method)s" action="%(action)s" '
                    'autocomplete="%(autocomplete)s" enctype="%(enctype)s" '
                    'evalurl="%(evalurl)s">' % attr)
        # Add hidden field with csrf_token if this is not None.
        if self._form._csrf_token:
            html.append('<input type="hidden" name="csrf_token" value="%s"/>'
                        % self._form._csrf_token)
        return "".join(html)

    def _render_form_body(self, render_outline):
        values = {'form': self._form,
                  '_': self.translate,
                  'render_outline': render_outline}
        return self.template.render(**values)

    def _render_form_buttons(self):
        _ = self.translate
        html = []
        html.append('<div class="row row-fluid">')
        if len(self._form._config.get_pages()) > 0:
            html.append('<div class="col-sm-3 span3 button-pane"></div>')
            html.append('<div class="col-sm-9 span9 button-pane">')
        else:
            html.append('<div class="col-sm-12 span12 button-pane well-small">')

        # Render default buttons if no buttons have been defined for the
        # form.
        if len(self._form._config._buttons) == 0:
            html.append('<button type="submit" '
                        'class="btn btn-default">%s</button>' % _('Submit'))
            html.append('<button type="reset" '
                        'class="btn btn-default">%s</button>' % _('Reset'))
        else:
            for b in self._form._config._buttons:
                if b.attrib.get("icon"):
                    icon = '<i class="%s"/>' % b.attrib.get("icon")
                else:
                    icon = ""
                attr = {
                    'type': b.attrib.get("type") or "submit",
                    'value': b.attrib.get("value") or "",
                    'class': "btn btn-%s" % (b.attrib.get("class") or "default"),
                    'icon': icon,
                    'label': _(b.text) or "XXX"
                }
                html.append('<button type="%(type)s" name="_%(type)s"'
                            ' value="%(value)s" class="%(class)s">'
                            '%(icon)s %(label)s</button>'
                            % (attr))
        # Else render defined buttons.
        html.append('</div>')
        html.append('</div>')
        return "".join(html)

    def _render_form_end(self):
        html = []
        html.append('</form>')
        html.append('</div>')
        return "".join(html)


class FieldRenderer(Renderer):
    """Renderer for fields. The renderer will build the the HTML for the
    provided field."""

    def __init__(self, field, translate):
        """Initialize the Renderer with the field instance.

        :field: Field instance

        """
        Renderer.__init__(self)

        self._field = field
        self._config = field._config.renderer
        self.translate = translate
        self.template = None
        #self.values = self._get_template_values()

    def __getattr__(self, name):
        """Give access to the config values of the renderer"""
        if self._config is None:
            return None
        return getattr(self._config, name)

    def _render_label(self):
        template = template_lookup.get_template("label.mako")
        values = self._get_template_values()
        return template.render(**values)

    def _render_errors(self):
        template = template_lookup.get_template("errors.mako")
        values = self._get_template_values()
        return template.render(**values)

    def _render_help(self):
        template = template_lookup.get_template("help.mako")
        values = self._get_template_values()
        return template.render(**values)

    def _render_diff(self, newvalue, oldvalue):
        """Will return a HTML string showing the differences between the old and
        the new string.

        The new string will have some markup to show the differences between
        the given strings. Words which has been deleted in the new string
        are marked with a *span* tag with the class *formed-deleted-value*.
        Elements which are new in the new string are marked with a span tag
        having the class *formed-new-value*.

        :old: Old string
        :new: New string
        :returns: A HTML string showing the differences.

        """
        out = []
        mode = None
        d = difflib.Differ()
        old = unicode(newvalue).split(" ")
        new = unicode(oldvalue).split(" ")
        diff = d.compare(old, new)
        for x in diff:
            if x[0:2] == "+ " and mode != "new":
                if mode:
                    out.append("</span>")
                    mode = None
                out.append('<span class="formbar-new-value">')
                mode = "new"
            elif x[0:2] == "- " and mode != "del":
                if mode:
                    out.append("</span>")
                    mode = None
                out.append('<span class="formbar-del-value">')
                mode = "del"
            elif x[0:2] == "  ":
                if mode:
                    out.append("</span>")
                    mode = None
            elif x[0:2] == "? ":
                continue
            out.append("%s " % "".join(x[2::]))
        if mode:
            out.append("</span>")
        return "".join(out)


    def _get_template_values(self):
        values = {'field': self._field,
                  'renderer': self,
                  '_': self.translate}
        return values

    def render(self):
        # TODO: Split rendering in four parts: label, fieldbody, errors,
        # help. Each in its own template.
        html = []
        has_errors = len(self._field.get_errors())
        has_warnings = len(self._field.get_warnings())
        html.append('<div class="form-group %s %s">' % ((has_errors and 'has-error'), (has_warnings and 'has-warning')))
        values = self._get_template_values()
        if self.label_width > 0 and self.label_position in ["left", "right"]:
            label_width = self.label_width
            label_align = self.label_align
            field_width = 12-self.label_width
            html.append('<div class="row">')
            if self.label_position == "left":
                html.append('<div class="col-sm-%s" align="%s">' % (label_width, label_align))
                html.append(self._render_label())
                html.append('</div>')
                html.append('<div class="col-sm-%s">' % field_width)
                html.append(self.template.render(**values))
                html.append(self._render_errors())
                html.append(self._render_help())
                html.append('</div>')
            else:
                html.append('<div class="col-sm-%s">' % field_width)
                html.append(self.template.render(**values))
                html.append(self._render_errors())
                html.append(self._render_help())
                html.append('</div>')
                html.append('<div class="col-sm-%s" align="%s">' % (label_width, label_align))
                html.append(self._render_label())
                html.append('</div>')
            html.append("</div>")
        else:
            html.append(self._render_label())
            html.append(self.template.render(**values))
            html.append(self._render_errors())
            html.append(self._render_help())
        html.append('</div>')
        return "".join(html)

class InfoFieldRenderer(FieldRenderer):
    """A Renderer to render simple fa_field elements"""

    def __init__(self, field, translate):
        FieldRenderer.__init__(self, field, translate)
        self.template = template_lookup.get_template("infofield.mako")

class TextFieldRenderer(FieldRenderer):
    """A Renderer to render simple fa_field elements"""

    def __init__(self, field, translate):
        FieldRenderer.__init__(self, field, translate)
        self.template = template_lookup.get_template("textfield.mako")

class TimeFieldRenderer(FieldRenderer):
    """A Renderer to render simple fa_field elements"""

    def __init__(self, field, translate):
        FieldRenderer.__init__(self, field, translate)
        self.template = template_lookup.get_template("timefield.mako")

class EmailFieldRenderer(FieldRenderer):
    """A Renderer to render email fields"""

    def __init__(self, field, translate):
        FieldRenderer.__init__(self, field, translate)
        self.template = template_lookup.get_template("email.mako")


class FileFieldRenderer(FieldRenderer):
    """A Renderer to render simple fa_field elements"""

    def __init__(self, field, translate):
        FieldRenderer.__init__(self, field, translate)
        self.template = template_lookup.get_template("filefield.mako")


class TextareaFieldRenderer(FieldRenderer):
    """A Renderer to render simple fa_field elements"""

    def __init__(self, field, translate):
        FieldRenderer.__init__(self, field, translate)
        self.template = template_lookup.get_template("textarea.mako")


class DateFieldRenderer(FieldRenderer):
    """A Renderer to render simple fa_field elements"""

    def __init__(self, field, translate):
        FieldRenderer.__init__(self, field, translate)
        self.template = template_lookup.get_template("datefield.mako")


class PasswordFieldRenderer(FieldRenderer):
    """A Renderer to render passwordfield elements"""

    def __init__(self, field, translate):
        FieldRenderer.__init__(self, field, translate)
        self.template = template_lookup.get_template("password.mako")

class HiddenFieldRenderer(FieldRenderer):
    """A Renderer to render hidden elements"""

    def __init__(self, field, translate):
        FieldRenderer.__init__(self, field, translate)
        self.template = template_lookup.get_template("hidden.mako")

    def render(self):
        html = []
        values = self._get_template_values()
        html.append(self.template.render(**values))
        return "".join(html)

class HTMLRenderer(FieldRenderer):
    """A Renderer to render generic HTML"""

    def __init__(self, field, translate):
        FieldRenderer.__init__(self, field, translate)
        self.template = template_lookup.get_template("html.mako")

    def render(self):
        html = []
        values = self._get_template_values()
        html.append(self._render_label())
        html.append(self.template.render(**values))
        return "".join(html)


class OptionFieldRenderer(FieldRenderer):
    """Superclass for fields element which supports selecting one or
    more options from a selection"""
    # TODO: Implement filtering of items here if possible. See Plorma
    # implementation of the ListingFieldRenderer to see how this
    # ignoring is implemented. (ti) <2013-10-11 22:39>
    def __init__(self, field, translate):
        FieldRenderer.__init__(self, field, translate)
        self._cache_options = None

    def _get_template_values(self):
        values = FieldRenderer._get_template_values(self)
        # Add the options to the values dictionary
        if self._cache_options is None:
            self._cache_options = self._field.get_options()
        values['options'] = self._cache_options
        return values

class DropdownFieldRenderer(OptionFieldRenderer):
    """A Renderer to render dropdown list"""

    def __init__(self, field, translate):
        OptionFieldRenderer.__init__(self, field, translate)
        self.template = template_lookup.get_template("dropdown.mako")

class SelectionFieldRenderer(OptionFieldRenderer):
    """A Renderer to render selection field"""

    def __init__(self, field, translate):
        OptionFieldRenderer.__init__(self, field, translate)
        self.template = template_lookup.get_template("selection.mako")

class RadioFieldRenderer(OptionFieldRenderer):
    """A Renderer to render selection field"""

    def __init__(self, field, translate):
        OptionFieldRenderer.__init__(self, field, translate)
        self.template = template_lookup.get_template("radio.mako")

class CheckboxFieldRenderer(OptionFieldRenderer):
    """A Renderer to render selection field"""

    def __init__(self, field, translate):
        OptionFieldRenderer.__init__(self, field, translate)
        self.template = template_lookup.get_template("checkbox.mako")

class FormbarEditorRenderer(FieldRenderer):
    """A Renderer to render the formbar editor widget used to edit
    formbar form definitons."""

    def __init__(self, field, translate):
        FieldRenderer.__init__(self, field, translate)
        self.template = template_lookup.get_template("formbareditor.mako")

# TODO: Check which of the following Renderers are needed (ti). It looks
# like they are outdated as they are using old FormAlchemy fa_*.mako
# templates <2013-10-11 22:31>

class ListFieldRenderer(FieldRenderer):
    """A Renderer to render selection list"""

    def __init__(self, field, translate):
        FieldRenderer.__init__(self, field, translate)
        self.template = template_lookup.get_template("fa_field.mako")
