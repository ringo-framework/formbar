import os
import datetime
import unittest

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine('sqlite:///:memory:', echo=False)
Session = scoped_session(sessionmaker())
Session.configure(bind=engine)
Base = declarative_base()

from formbar import test_dir
from formbar.config import load, Config
from formbar.form import Form, StateError, Validator

RESULT="""<html><body><div class="formbar-form"><form id="customform" class="testcss" method="GET" action="http://" autocomplete="off"> <div class="row-fluid"> <div class="span12"> <label for="string"> String field</label> <div class="readonlyfield"> &nbsp; </div> </div> </div> <div class="row-fluid"> <div class="span6"> <label for="default"> Default</label> <div class="readonlyfield"> &nbsp; </div> </div> <div class="span6"> <label for="select"> Select</label> <div class="readonlyfield"> &nbsp; </div> </div> </div> <div class="row-fluid"> <div class="span6"> <label for="float"> Float field</label> <div class="readonlyfield"> &nbsp; </div> <div class="text-help"> <i class="icon-info-sign"></i> This is is a very long helptext which should span over multiple rows. Further the will check if there are further html tags allowed.</div> </div> <div class="span6"> <label for="date"> <sup>(1)</sup> Date field</label> <div class="readonlyfield"> &nbsp; </div> <div class="text-help"> <i class="icon-info-sign"></i> This is my helptext</div> </div> </div> <div class="row-fluid"> <div class="span6"> <label for="string"> String field</label> <div class="readonlyfield"> &nbsp; </div> </div> <div class="span6"> <label for="integer"> Integer field <a href="#" data-toggle="tooltip" class="formbar-tooltip" data-original-title="Required fa_field"><i class="icon-asterisk"></i></a></label> <div class="readonlyfield"> &nbsp; </div> </div> </div>
</form></div></body></html>"""

def external_validator(field, data):
    return 16 == data[field]


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(Integer)

    def __init__(self, name=None, fullname=None, password=None):
        self.name = name
        self.fullname = fullname
        self.password = password

    def __repr__(self):
        return "<User('%s','%s', '%s')>" % (self.name, self.fullname,
                                            self.password)

class TestInheritedForm(unittest.TestCase):

    def setUp(self):
        tree = load(os.path.join(test_dir, 'inherited.xml'))
        config = Config(tree)
        form_config = config.get_form('customform')
        self.form = Form(form_config)

    def test_form_init(self):
        pass

    def test_string_field(self):
        field = self.form.get_field("string")
        self.assertEqual(field.label, "Inherited String field")

    def test_form_fields(self):
        self.assertEqual(len(self.form.fields.values()), 10)

class TestFormValidation(unittest.TestCase):

    def setUp(self):
        tree = load(os.path.join(test_dir, 'form.xml'))
        config = Config(tree)
        form_config = config.get_form('customform')
        self.form = Form(form_config)

    def test_form_init(self):
        pass

    def test_form_unknown_field(self):
        values = {'unknown': 'test', 'integer': '15', 'date': '1998-02-01'}
        self.form.validate(values)
        # Check that the unknown field has been filtered out as it was
        # not part of the form.
        self.assertEqual(self.form.data.has_key('unknown'), False)

    def test_form_validate_fail(self):
        values = {'default': 'test', 'integer': '15', 'date': '1998-02-01'}
        self.assertEqual(self.form.validate(values), False)

    def test_form_validate_fail_checkvalues(self):
        values = {'default': 'test', 'integer': '15', 'date': '1998-02-01'}
        self.assertEqual(self.form.validate(values), False)
        self.assertEqual(self.form.submitted_data['integer'], '15')
        self.assertEqual(self.form.submitted_data['date'], '1998-02-01')

    def test_form_validate_ok(self):
        values = {'default': 'test', 'integer': '16', 'date': '1998-02-01'}
        validator = Validator('integer',
                              'Error message',
                              external_validator)
        self.form.add_validator(validator)
        self.assertEqual(self.form.validate(values), True)

    def test_form_validate_ext_validator_fail(self):
        values = {'default': 'test', 'integer': '15', 'date': '1998-02-01'}
        validator = Validator('integer',
                              'Error message',
                              external_validator)
        self.form.add_validator(validator)
        self.assertEqual(self.form.validate(values), False)

    def test_form_validate_ext_validator_ok(self):
        values = {'default': 'test', 'integer': '16', 'date': '1998-02-01'}
        self.assertEqual(self.form.validate(values), True)

    def test_form_deserialize_int(self):
        values = {'default': 'test', 'integer': '16', 'date': '1998-02-01'}
        self.form.validate(values)
        self.assertEqual(self.form.data['integer'], 16)

    def test_form_deserialize_float(self):
        values = {'default': 'test', 'integer': '16',
                  'date': '1998-02-01', 'float': '87.5'}
        self.assertEqual(self.form.validate(values), True)
        self.assertEqual(self.form.data['float'], 87.5)

    def test_form_deserialize_date(self):
        values = {'default': 'test', 'integer': '16',
                  'float': '87.5', 'date': '1998-02-01'}
        self.form.validate(values)
        self.assertEqual(self.form.data['date'], datetime.date(1998, 2, 1))

    def test_form_deserialize_string(self):
        values = {'default': 'test', 'integer': '16', 'date': '1998-02-01', 'float': '99'}
        self.form.validate(values)
        self.assertEqual(self.form.data['default'], 'test')

    def test_form_deserialize_time(self):
        values = {'default': 'test', 'integer': '16', 'date': '1998-02-01', 'float': '99', 'time': '00:12:11'}
        self.form.validate(values)
        self.assertEqual(self.form.data['time'], 731)

    def test_form_deserialize_interval(self):
        values = {'default': 'test', 'integer': '16', 'date': '1998-02-01', 'float': '99', 'interval': '00:12:11'}
        self.form.validate(values)
        self.assertEqual(self.form.data['interval'], datetime.timedelta(0, 731))

    def test_form_convert_interval_ok(self):
        values = {'default': 'test', 'integer': '16', 'date': '1998-02-01', 'float': '99', 'interval': '01:12'}
        self.form.validate(values)
        self.assertEqual(self.form.data['interval'], datetime.timedelta(hours=1, minutes=12))
    
    def test_form_convert_interval_false(self):
        values = {'default': 'test', 'integer': '16', 'date': '1998-02-01', 'float': '99', 'interval': '00:12:11'}
        self.form.validate(values)
        self.assertEqual(self.form.data['interval'] == datetime.timedelta(1), False)
    
    def test_form_convert_interval_mm_ok(self):
        values = {'default': 'test', 'integer': '16', 'date': '1998-02-01', 'float': '99', 'interval': '12'}
        self.form.validate(values)
        self.assertEqual(self.form.data['interval'], datetime.timedelta(minutes=12))
    
    def test_form_save(self):
        values = {'default': 'test', 'integer': '16', 'date': '1998-02-01'}
        self.assertEqual(self.form.validate(values), True)

    def test_form_warnings(self):
        values = {'select': '2', 'default': 'test', 'integer': '16', 'date': '1998-02-01'}
        self.form.validate(values)
        warnings = self.form.get_warnings()
        self.assertEqual(len(warnings), 2)

    def test_form_save_without_validation(self):
        self.assertRaises(StateError, self.form.save)

    def test_form_fields(self):
        self.assertEqual(len(self.form.fields.values()), 9)

    def test_form_field_select_options(self):
        selfield = self.form.get_field('select')
        self.assertEqual(len(selfield.get_options()), 4)

    def test_generated_rules(self):
        num_rules = 0
        fields = self.form.fields
        for field in fields:
            num_rules += len(self.form.get_field(field).get_rules())
        self.assertEqual(num_rules, 5)

    def test_generated_warning_rules(self):
        num_rules = 0
        fields = self.form.fields
        for fieldname in fields:
            field = self.form.get_field(fieldname)
            rules = [r for r in field.get_rules() if r.triggers=="warning"]
            num_rules += len(rules)
        self.assertEqual(num_rules, 2)

    def test_generated_error_rules(self):
        num_rules = 0
        fields = self.form.fields
        for fieldname in fields:
            field = self.form.get_field(fieldname)
            rules = [r for r in field.get_rules() if r.triggers=="error"]
            num_rules += len(rules)
        self.assertEqual(num_rules, 3)


class TestFormRenderer(unittest.TestCase):

    def setUp(self):
        tree = load(os.path.join(test_dir, 'form.xml'))
        config = Config(tree)
        form_config = config.get_form('customform')
        self.form = Form(form_config)

    # Disable this test. Find better way to check if the rendering is
    # ok.
    #def test_form_render(self):
    #    html = self.form.render()
    #    html = " ".join(html.replace('\n','').split())
    #    check = " ".join(RESULT.replace('\n','').split())
    #    self.assertEqual(html, check)


class TestFormAlchemyForm(unittest.TestCase):

    def _insert_item(self):
        item = User('ed', 'Ed Jones', 'edspassword')
        self.session.add(item)
        self.session.commit()
        return item

    def setUp(self):
        Base.metadata.create_all(engine)
        tree = load(os.path.join(test_dir, 'form.xml'))
        self.config = Config(tree)
        self.session = Session()

    def tearDown(self):
        Session.remove()

    def test_read(self):
        form_config = self.config.get_form('userform1')
        item = self._insert_item()
        form = Form(form_config, item)
        self.assertEqual(len(form.fields), 2)

    def test_create(self):
        form_config = self.config.get_form('userform2')
        item = User()
        form = Form(form_config, item)
        self.assertEqual(len(form.fields), 3)

    def test_create_save(self):
        form_config = self.config.get_form('userform2')
        item = User()
        # Important! Provide the dbsession if you want to create a new
        # item
        form = Form(form_config, item, self.session)
        values = {"name": "paulpaulpaul", "fullname": "Paul Wright",
                  "password": "1"}
        if form.validate(values):
            saved_item = form.save()
            self.assertEqual(saved_item, item)
        result = self.session.query(User).all()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "paulpaulpaul")

    def test_edit_save(self):
        form_config = self.config.get_form('userform2')
        item = self._insert_item()
        item = self._insert_item()
        result = self.session.query(User).all()
        form = Form(form_config, item)
        result = self.session.query(User).all()
        values = {"name": "paulpaulpaul", "fullname": "Paul Wright",
                  "password": "1"}
        if form.validate(values):
            form.save()
        result = self.session.query(User).all()
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].name, "ed")
        self.assertEqual(result[1].name, "paulpaulpaul")


if __name__ == '__main__':
    unittest.main()
