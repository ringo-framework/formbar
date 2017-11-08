#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from formbar.config import Config, Field, parse
import sys
import argparse

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
    fields = [field for field in _get_fields(config) if field.type is not "info" and filter_tag(field, args.tags)]
    out = []
    for field in fields:
        if (not args.filtertype
            or field.type == args.filtertype):
            if args.printtype:
                out.append("{} ({})".format(field.name, field.type if field.type else "string"))
            else:
                out.append(field.name)
    if args.aslist:
        print "[%s]" % ",".join("'%s'" % field for field in out)
    else:
        print "\n".join(out)


def _render_options(options):
    out = []
    for o in options:
        out.append(u"{}) {}".format(o[1], o[0]))
    return u"\n".join(out)


def _render_renderer(field):
    if field.renderer:
        return field.renderer.type
    return ""


def _render_rules(field):
    out = []
    for r in field.get_rules():
        if r.required or r.desired:
            continue
        out.append(u"{},{},{}".format(r._expression, r.msg, r.triggers))
    return u"\n".join(out)


def _render_conditions(config, field):
    out = []
    for cond in config.get_elements('if'):
        for cond_field in cond.findall('field'):
            if cond_field.attrib.get("ref") == field.id:
                out.append(cond.attrib.get("expr"))
    return u"\n".join(out)


def print_fields(config, args):
    """Print infos on fields in CSV"""
    fields = [field for field in _get_fields(config) if field.type is not "info" and filter_tag(field, args.tags)]
    out = []
    out.append('"ID","Name","Label","Number","Typ","Required","Desired","Help","Renderer","Options","Rules","Conditions","Comment"')
    for field in fields:
        if (not args.filtertype
            or field.type == args.filtertype):
            out.append(u'"{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}",""'.format(
                field.id,
                field.name,
                field.label,
                field.number,
                field.type or "string",
                field.required,
                field.desired,
                field.help or "",
                _render_renderer(field),
                _render_options(field.options),
                _render_rules(field),
                _render_conditions(config, field)
            )
        )
    if args.out:
        args.out.write("\n".join(out).encode("UTF8"))
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

def print_conditionals(config, args):
    elements = []
    elements.extend(config.get_elements('if'))
    out = ["Reset: {}, Type {}, Expression: {}, Fields: {}".format("True" if element.attrib.get("reset-value") else "False", element.attrib.get("type") if element.attrib.get("type") else "hide", element.attrib.get("expr"), [f.attrib.get("ref") for f in element.findall(".//field")]) for element in elements]
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
            "currency": "sa.Float",
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
    elif args.action == "fieldnames":
        print_fieldnames(config_tree, args)
    elif args.action == "fields":
        print_fields(config_tree, args)
    elif args.action == "rules":
        print_rules(config_tree, args)
    elif args.action == "conditionals":
        print_conditionals(config_tree, args)
    else:
        print "nothing to do"


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate various informations from a form configuration file')
    parser.add_argument('action', choices=['model', 'fields', 'fieldnames', 'rules', 'conditionals'], help='Output to generate')
    parser.add_argument('config', metavar='config', type=file, help='A form configuration file')
    parser.add_argument('--filter-type', help='Only show fields with the given type.', dest='filtertype', default="")
    parser.add_argument('--print-type', dest='printtype', action="store_true")
    parser.add_argument('--tags', metavar='tags', help='Only choose fields with given tags. If empty all fields are returned.', default="")
    parser.add_argument('--aslist', dest='aslist', action="store_true")
    parser.add_argument('--out', metavar='out', type=argparse.FileType('w'), help='Output')
    args = parser.parse_args()
    main(args)
    sys.exit(0)
