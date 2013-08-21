#!/usr/bin/env python
from formbar.config import Config, Field, parse
import sys, argparse

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
        nullable = field.required is False
        default = None
        if field.type == "string":
            dtype = "sa.Text"
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
        else:
            dtype = "sa.Text"
        out.append("%s = sa.Column('%s', %s, nullable=%s, default=%r)" %
                   (name, name, dtype, nullable, default))
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
