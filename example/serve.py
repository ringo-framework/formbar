import os
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response

from mako.lookup import TemplateLookup
from formbar import example_dir

template_lookup = TemplateLookup(directories=[example_dir],
                                 module_directory='/tmp/phormular_modules')

from formbar import test_dir
from formbar.config import Config, load
from formbar.form import Form


def index(request):
    config = Config(load(os.path.join(test_dir, 'form.xml')))
    form_config = config.get_form('customform')
    form = Form(form_config)

    template = template_lookup.get_template("index.mako")
    values = {'form': form.render()}
    return Response(template.render(**values))

if __name__ == '__main__':
    config = Configurator()
    config.add_route('hello', '/')
    config.add_view(index, route_name='hello')
    config.add_static_view('bootstrap', 'bootstrap', cache_max_age=3600)
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
