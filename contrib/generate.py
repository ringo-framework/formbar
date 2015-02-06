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
    out = []
    for field in _get_fields(config):
        name = field.name
        extra_attributes = []
        if field.type == "string":
            dtype = "sa.String"
            extra_attributes.append("nullable=False")
            extra_attributes.append("default=''")
        elif field.type == "text":
            dtype = "sa.Text"
            extra_attributes.append("nullable=False")
            extra_attributes.append("default=''")
        elif field.type == "integer":
            dtype = "sa.Integer"
        elif field.type == "date":
            dtype = "sa.Date"
        elif field.type == "datetime":
            dtype = "sa.DateTime"
        elif field.type == "float":
            dtype = "sa.Float"
        elif field.type == "number":
            dtype = "sa.Numeric"
        elif field.type == "decimal":
            dtype = "sa.Decimal"
        elif field.type == "boolean":
            dtype = "sa.Boolean"
        elif field.type == "blob":
            dtype = "sa.LargeBinary"
        elif field.type == "info":
            continue # ignore this type
        # Default
        else:
            log.warning(("No type found for '%s' using default 'sa.String'. "
                         % field.name))
            dtype = "sa.String"
            extra_attributes.append("nullable=False")
            extra_attributes.append("default=''")

        if extra_attributes:
            column_format = "%s = sa.Column('%s', %s, %s)"
            out.append(column_format % (name, name,
                                        dtype, ", ".join(extra_attributes)))
        else:
            column_format = "%s = sa.Column('%s', %s)"
            out.append(column_format % (name, name, dtype))

    print "\n".join(out)

def main (config, action):
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
