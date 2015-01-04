import os
from sqlalchemy.orm import scoped_session
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response

# FIXME: Why is this import needed? If not present the server will fail
# to work. (ti) <2014-05-20 17:08>
from sqlalchemy.orm import scoped_session

from mako.lookup import TemplateLookup
from formbar import example_dir, logging
from formbar.config import Config, load
from formbar.form import Form
from formbar.rules import Rule

template_lookup = TemplateLookup(directories=[example_dir])

log = logging.getLogger(__name__)


def set_current_form_page(request):
    """Will save the currently selected page in the form into a
    sessions. Note this is only a dummy implementation. This function
    needs to be implemented."""
    return {"success": True}

def evaluate(request):
    """Will return a JSON response with the result of the evaluation of
    the submitted formbar rule."""
    rule = Rule(request.GET.get('rule'))
    result = rule.evaluate({})
    return {"success": True,
            "data": result,
            "params": {"msg": rule.msg}}

def example(request):
    config = Config(load(os.path.join(example_dir, 'example.xml')))
    form_config = config.get_form('example')
    form = Form(form_config, eval_url="/evaluate", request=request)

    if request.POST:
        form.validate(request.POST)
    else:
        form.validate({})

    template = template_lookup.get_template("index.mako")
    values = {'form': form.render()}
    return Response(template.render(**values))


if __name__ == '__main__':
    config = Configurator()
    config.add_route('root', '/')
    config.add_route('ex1', '/example')
    config.add_route('evaluate', '/evaluate')
    config.add_route('set_current_form_page', '/set_current_form_page')
    config.add_view(example, route_name='root')
    config.add_view(example, route_name='ex1')
    config.add_view(evaluate, route_name='evaluate', renderer="json")
    config.add_view(set_current_form_page, route_name='set_current_form_page', renderer="json")
    config.add_static_view('bootstrap', 'bootstrap', cache_max_age=3600)
    config.add_static_view('css', 'css', cache_max_age=3600)
    config.add_static_view('js', 'js', cache_max_age=3600)
    app = config.make_wsgi_app()
    server = make_server('127.0.0.1', 8080, app)
    print "Server is available on http://127.0.0.1:8080"
    server.serve_forever()
