#!/usr/bin/env python
import logging
from formbar.config import Config, Field, parse
import sys, argparse

log = logging.getLogger(name="formbar.contrib.generate")


def _get_config(config):
    return Config(parse(config.read()))


def _get_fields(config):
    fields = []
    for en in config.get_elements('entity'):
        fields.append(Field(en))
    return fields

def filter_tag(field, tags):
    if tags == "":
        return True
    for tag in tags.split(","):
        if tag in field.tags:
            return True
    return False

def print_fieldnames(config, args):
    out = [field.name for field in _get_fields(config) if field.type is not "info" and filter_tag(field, args.tags)]
    if args.aslist:
        print "[%s]" % ",".join("'%s'" % field for field in out)
    else:
        print "\n".join(out)

def print_rules(config, args):
    elements = []
    elements.extend(config.get_elements('rules'))
    elements.extend(config.get_elements('if'))
    out = [element.attrib.get("expr") for element in elements]
    if args.aslist:
        print "[%s]" % ",".join("'%s'" % field for field in out)
    else:
        print "\n".join(out)

def print_model(config, args):

    def generate_Column(field):
        datatypes = {
            "string": "sa.String",
            "text": "sa.Text",
            "integer": "sa.Integer",
            "date": "sa.Date",
            "datetime": "sa.DateTime",
            "interval": "sa.Interval",
            "float": "sa.Float",
            "number": "sa.Numeric",
            "decimal": "sa.Decimal",
            "boolean": "sa.Boolean",
            "blob": "sa.LargeBinary"
        }
        datatype = datatypes.get(field.type)
        if datatype is None:   
            log.warning(("No type found for '%s' using default 'sa.String'. "
                         % field.name))
            datatype = "sa.String"
        if datatype is "sa.String" or datatype is "sa.Text":
            col = "%s = sa.Column('%s', %s, nullable=False, default='')"
            return col % (field.name, field.name, datatype)
        else:
            col = "%s = sa.Column('%s', %s)"
            return col % (field.name, field.name, datatype)

    out = [generate_Column(field) for field in _get_fields(config) if field.type is not "info" and filter_tag(field, args.tags)]
    print "\n".join(out)


def main(args):
    config_tree = _get_config(args.config)
    if args.action == "model":
        print_model(config_tree, args)
    if args.action == "fieldnames":
        print_fieldnames(config_tree, args)
    if args.action == "rules":
        print_rules(config_tree, args)
    else:
        print "nothing to do"


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate various informations from a form configuration file')
    parser.add_argument('action', choices=['model', 'fieldnames', 'rules'], help='Output to generate')
    parser.add_argument('config', metavar='config', type=file, help='A form configuration file')
    parser.add_argument('--tags', metavar='tags', help='Only choose fields with given tags. If empty all fields are returned.', default="")
    parser.add_argument('--aslist', dest='aslist', action="store_true")
    args = parser.parse_args()
    main(args)
    sys.exit(0)
