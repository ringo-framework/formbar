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


def print_model(config):
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

    out = [generate_Column(field) for field in _get_fields(config) if field.type is not "info"]
    print "\n".join(out)


def main(config, action):
    config_tree = _get_config(config)
    if action == "model":
        print_model(config_tree)
    else:
        print "nothing to do"


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate various informations from a form configuration file')
    parser.add_argument('action', choices=['model'], help='Output to generate')
    parser.add_argument('config', metavar='config', type=file, help='A form configuration file')
    args = parser.parse_args()
    main(args.config, args.action)
    sys.exit(0)
