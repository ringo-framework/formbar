import os
from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker, scoped_session

engine = create_engine('sqlite:///:memory:', echo=False)
Session = scoped_session(sessionmaker())
Session.configure(bind=engine)
Base = declarative_base()


from mako.lookup import TemplateLookup
from formbar import example_dir, logging
from formbar.config import Config, load
from formbar.form import Form

template_lookup = TemplateLookup(directories=[example_dir],
                                 module_directory='/tmp/phormular_modules')
Base.metadata.create_all(engine)

log = logging.getLogger(__name__)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)

    def __init__(self, name, fullname, password):
        self.name = name
        self.fullname = fullname
        self.password = password

    def __repr__(self):
        return "<User('%s','%s', '%s')>" % (self.name, self.fullname,
                                            self.password)


def add_item():
    session = Session()
    ed_user = User('ed', 'Ed Jones', 'edspassword')
    session.add(ed_user)
    session.commit()
    return ed_user


def get_items():
    session = Session()
    return session.query(User).all()


def example_1(request):
    config = Config(load(os.path.join(example_dir, 'example1.xml')))
    form_config = config.get_form('example1')
    form = Form(form_config)

    if request.POST:
        form.validate(request.POST.mixed())

    template = template_lookup.get_template("index.mako")
    values = {'form': form.render()}
    return Response(template.render(**values))


def example_2(request):
    """Testfunction to check if SQL-Alchemy enabled forms to work"""
    config = Config(load(os.path.join(example_dir, 'example2.xml')))
    form_config = config.get_form('form')
    items = get_items()
    form = Form(form_config, items[0])

    if request.POST:
        values = request.POST.mixed()
        if form.validate(values):
            form.save()

    template = template_lookup.get_template("index.mako")
    values = {'form': form.render()}
    return Response(template.render(**values))

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    add_item()
    add_item()
    add_item()
    config = Configurator()
    config.add_route('root', '/')
    config.add_route('ex1', '/example1')
    config.add_route('ex2', '/example2')
    config.add_view(example_1, route_name='root')
    config.add_view(example_1, route_name='ex1')
    config.add_view(example_2, route_name='ex2')
    config.add_static_view('bootstrap', 'bootstrap', cache_max_age=3600)
    app = config.make_wsgi_app()
    server = make_server('0.0.0.0', 8080, app)
    server.serve_forever()
