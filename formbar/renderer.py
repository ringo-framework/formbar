import logging

from mako.lookup import TemplateLookup
from formbar import template_dir

template_lookup = TemplateLookup(directories=[template_dir],
                                 module_directory='/tmp/phormular_modules')

log = logging.getLogger(__name__)


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

    def __init__(self, form):
        """@todo: to be defined

        :form: @todo

        """
        Renderer.__init__(self)

        self._form = form
        self.template = template_lookup.get_template("form.mako")

    def render(self, values={}):
        """Returns the rendered form as string. If values are provided
        these values are used to prefill the form and eventually
        overwrite values in the form.

        :values: dictionary with values which should be used to prefill
        the form.
        :returns: rendered form.

        """
        html = []
        html.append(self._render_form_start())
        html.append(self._render_form_body())
        if not self._form._config.readonly:
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
                'enctype': self._form._config.enctype}
        html.append('<form id="%(id)s" class="%(css)s" '
                    'method="%(method)s" action="%(action)s" '
                    'autocomplete="%(autocomplete)s" >' % attr)
        return "".join(html)

    def _render_form_body(self):
        values = {'form': self._form}
        return self.template.render(**values)

    def _render_form_buttons(self):
        html = []
        html.append('<div class="row-fluid">')
        html.append('<div class="span12 button-pane well-small">')
        html.append('<button type="submit" '
                    'class="btn btn-primary">%s</button>' % 'Submit')
        html.append('<button type="reset" '
                    'class="btn btn-warning">%s</button>' % 'Reset')
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

    def __init__(self, field):
        """Initialize the Renderer with the field instance.

        :field: Field instance

        """
        Renderer.__init__(self)

        self._field = field
        self.template = template_lookup.get_template("field.mako")

    def render(self):
        # TODO: Split rendering in four parts: label, fieldbody, errors,
        # help. Each in its own template.
        values = {'field': self._field}
        return self.template.render(**values)
