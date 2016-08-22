import logging
import difflib
import xml.etree.ElementTree as ET
from webhelpers.html import literal, HTML

from mako.lookup import TemplateLookup
from formbar import template_dir
from formbar.rules import Rule


template_lookup = TemplateLookup(directories=[template_dir],
                                 default_filters=['h'])

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
        if renderer.render_type in field._form.external_renderers:
            return field._form.external_renderers.get(renderer.render_type)(
                field, translate)
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
        elif renderer.render_type == "textoption":
            return TextoptionFieldRenderer(field, translate)
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
        elif dtype == "interval":
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
        return literal("").join(html)

    def _render_form_start(self):
        html = []
        html.append(HTML.tag("div", class_="formbar-form", _closed=False))
        html.append(HTML.tag("form", _closed=False,
                             id=self._form._config.id,
                             role="form",
                             class_=self._form._config.css,
                             action=self._form._config.action,
                             method=self._form._config.method,
                             autocomplete=self._form._config.autocomplete,
                             enctype=self._form._config.enctype,
                             evalurl=self._form._eval_url or ""))
        # Add hidden field with csrf_token if this is not None.
        if self._form._csrf_token:
            html.append(HTML.tag("input",
                                 type="hidden",
                                 name="csrf_token",
                                 value=self._form._csrf_token))
        return literal("").join(html)

    def _render_form_body(self, render_outline):
        values = {'form': self._form,
                  '_': self.translate,
                  'render_outline': render_outline,
                  'ElementTree': ET,
                  'Rule': Rule}
        return literal(self.template.render(**values))

    def _render_form_buttons(self):
        _ = self.translate
        html = []
        html.append(HTML.tag("div", _closed=False, class_="row row-fluid"))
        if len(self._form._config.get_pages()) > 0:
            html.append(HTML.tag("div",
                                 class_="col-sm-3 span3 button-pane"))
            html.append(HTML.tag("div", _closed=False,
                                 class_="col-sm-9 span9 button-pane"))
        else:
            html.append(HTML.tag("div", _closed=False,
                        class_="col-sm-12 span12 button-pane well-small"))

        # Render default buttons if no buttons have been defined for the
        # form.
        if len(self._form._config._buttons) == 0:
            html.append(HTML.tag("button", type="submit",
                                 name="_submit", value="",
                                 class_="btn btn-default hidden-print",
                                 c=_('Submit')))
            # If there is a next page than render and additional submit
            # button.
            if len(self._form.pages) > 1:
                html.append(HTML.tag("button", type="submit",
                                     name="_submit", value="nextpage",
                                     class_="btn btn-default hidden-print",
                                     c=_('Submit and proceed')))
        else:
            for b in self._form._config._buttons:
                if b.attrib.get("ignore"):
                    continue
                html.append(HTML.tag("button", _closed=False,
                            type=b.attrib.get("type") or "submit",
                            name="_%s" % b.attrib.get("type") or "submit",
                            value=b.attrib.get("value") or "",
                            class_=b.attrib.get("class")
                            or "btn btn-default hidden-print"))
                if b.attrib.get("icon"):
                    html.append(HTML.tag("i", class_=b.attrib.get("icon"),
                                         c=_(b.text)))
                html.append(_(b.text))
        html.append(HTML.tag("/div", _closed=False))
        html.append(HTML.tag("/div", _closed=False))
        return literal("").join(html)

    def _render_form_end(self):
        html = []
        html.append(HTML.tag("/form", _closed=False))
        html.append(HTML.tag("/div", _closed=False))
        return literal("").join(html)


class FieldRenderer(Renderer):
    """Renderer for fields. The renderer will build the the HTML for the
    provided field."""

    def __init__(self, field, translate):
        """Initialize the Renderer with the field instance.

        :field: Field instance

        """
        Renderer.__init__(self)
        self._field = field
        self._active = True
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
        values = {'field': self._field,
                  '_': self.translate}
        return literal(template.render(**values))

    def _render_errors(self):
        template = template_lookup.get_template("errors.mako")
        values = {'field': self._field,
                  '_': self.translate,
                  'active': self._active}
        return literal(template.render(**values))

    def _render_help(self):
        template = template_lookup.get_template("help.mako")
        values = {'field': self._field,
                  '_': self.translate}
        return literal(template.render(**values))

    def _render_diff(self, newvalue, oldvalue):
        """Will return a HTML string showing the differences between the old
        and the new string.

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
                    out.append(HTML.tag("/span", _closed=False))
                    mode = None
                out.append(HTML.tag("span", _closed=False,
                                    class_="formbar-new-value"))
                mode = "new"
            elif x[0:2] == "- " and mode != "del":
                if mode:
                    out.append(HTML.tag("/span", _closed=False))
                    mode = None
                out.append(HTML.tag("span", _closed=False,
                                    class_="formbar-del-value"))
                mode = "del"
            elif x[0:2] == "  ":
                if mode:
                    out.append(HTML.tag("/span", _closed=False))
                    mode = None
            elif x[0:2] == "? ":
                continue
            out.append("%s " % "".join(x[2::]))
        if mode:
            out.append(HTML.tag("/span", _closed=False))
        return literal("").join(out)

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
        active = 'active' if self._active else 'inactive'
        # Handle indent. Set indent_with css only if the elements are
        # actually have an indent and the lable position allows an
        # indent.
        indent_width = ""
        if self.elements_indent \
           and self.label_position not in ["left", "right"]:
            indent_width = self.indent_width
        class_options = ((has_errors and 'has-error'),
                         (has_warnings and 'has-warning'),
                         (active),
                         indent_width)
        html.append(HTML.tag("div", _closed=False,
                    rules=u"{}".format(";".join(self._field.rules_to_string)),
                    formgroup="{}".format(self._field.name),
                    desired="{}".format(self._field.desired),
                    required="{}".format(self._field.required),
                    class_=("form-group %s %s %s %s" % class_options)))
        values = self._get_template_values()
        if self.label_width > 0 and self.label_position in ["left", "right"]:
            label_width = self.label_width
            label_align = self.label_align
            field_width = 12 - self.label_width
            html.append(HTML.tag("div", _closed=False, class_="row"))
            if self.label_position == "left":
                html.append(HTML.tag("div", _closed=False,
                                     class_=("col-sm-%s" % label_width),
                                     align=("%s" % label_align)))
                html.append(self._render_label())
                html.append(HTML.tag("/div", _closed=False))
                html.append(HTML.tag("div", _closed=False,
                                     class_=("col-sm-%s" % field_width)))
                html.append(literal(self.template.render(**values)))
                html.append(self._render_errors())
                html.append(self._render_help())
                html.append(HTML.tag("/div", _closed=False))
            else:
                html.append(HTML.tag("div", _closed=False,
                                     class_=("col-sm-%s" % field_width)))
                html.append(literal(self.template.render(**values)))
                html.append(self._render_errors())
                html.append(self._render_help())
                html.append(HTML.tag("/div", _closed=False))
                html.append(HTML.tag("div", _closed=False,
                                     class_=("col-sm-%s" % label_width),
                                     align=("%s" % label_align)))
                html.append(self._render_label())
                html.append(HTML.tag("/div", _closed=False))
            html.append(HTML.tag("/div", _closed=False))
        else:
            html.append(self._render_label())
            html.append(literal(self.template.render(**values)))
            html.append(self._render_errors())
            html.append(self._render_help())
        html.append(HTML.tag("/div", _closed=False))
        return literal("").join(html)


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
        html.append(literal(self.template.render(**values)))
        return literal("").join(html)


class HTMLRenderer(FieldRenderer):
    """A Renderer to render generic HTML"""

    def __init__(self, field, translate):
        FieldRenderer.__init__(self, field, translate)
        self.template = template_lookup.get_template("html.mako")

    def render(self):
        html = []
        values = self._get_template_values()
        html.append(self._render_label())
        html.append(literal(self.template.render(**values)))
        return literal("").join(html)


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


class TextoptionFieldRenderer(OptionFieldRenderer):
    """A Renderer to render textoption field. A textoption field is a
    mixture of a selection field and a text field. The value can be as
    comma separated list into the text field while the actual values are
    selected in the background."""

    def __init__(self, field, translate):
        OptionFieldRenderer.__init__(self, field, translate)
        self.template = template_lookup.get_template("textoption.mako")


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
