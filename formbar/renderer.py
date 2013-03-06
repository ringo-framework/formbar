import logging
import pkg_resources
import os

from mako.lookup import TemplateLookup

base_dir = pkg_resources.get_distribution("formbar").location
template_dir = os.path.join(base_dir, 'templates')
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
        html.append('<div class="span12 well-small">')
        html.append('<button type="submit" class="btn btn-primary">%s</button>' % 'Submit')
        html.append('<button type="reset" class="btn btn-warning">%s</button>' % 'Reset')
        html.append('</div>')
        html.append('</div>')
        return "".join(html)

    def _render_form_end(self):
        html = []
        html.append('</form>')
        html.append('</div>')
        return "".join(html)
