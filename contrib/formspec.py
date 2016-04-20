#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import argparse
import gettext
from formbar.config import Config, parse

def _(message):
    if message == "":
        return ""
    result = gettext.gettext(message)
    if isinstance(result, unicode):
        result = result.encode("UTF-8")
    return result


def _get_config(config):
    return Config(parse(config.read()))


def reindent(s, numSpaces=3):
    """
    Re-indent a multi-line string by a number of spaces (used for tables)
    """
    s = s.split('\n')
    s = [(' ' * numSpaces) + line for line in s]
    s = '\n'.join(s)
    return s


def render_page(element):
    out = []
    out.append("*"*len(_(element.attrib.get("label"))))
    out.append(_(element.attrib.get("label")))
    out.append("*"*len(_(element.attrib.get("label"))))
    return "\n".join(out)


def render_section(element):
    out = []
    out.append(_(element.attrib.get("label")))
    out.append("="*len(_(element.attrib.get("label"))))
    return "\n".join(out)


def render_subsection(element):
    out = []
    out.append(_(element.attrib.get("label")))
    out.append("-"*len(_(element.attrib.get("label"))))
    return "\n".join(out)


def _render_label(element):
    key = _('Label')
    value = _(element.attrib.get("label"))
    try:
        if value and isinstance(value, unicode):
            value = value.encode("UTF-8")
    except:
        value = "ERROR: Could not convert Label"
    return ":{key}: {value}".format(key=key, value=value)


def _render_required(element):
    key = _('Pflichtstatus')
    required = _(element.attrib.get("required"))
    desired = _(element.attrib.get("desired"))
    if not required and not desired:
        value = ""
    elif required:
        value = "Pflichtfeld"
    else:
        value = "Forderfeld"
    try:
        if value and isinstance(value, unicode):
            value = value.encode("UTF-8")
    except:
        value = "ERROR: Could not convert Label"
    return ":{key}: {value}".format(key=key, value=value)

def _render_name(element):
    key = _('Name')
    value = element.attrib.get("name")
    if value:
        value = value.encode("UTF-8")
    return ":{key}: {value}".format(key=key, value=value)


def _render_type(element):
    key = _('Type')
    value = element.attrib.get("type", "string")
    renderer = _get_renderer(element)
    # Currently we do not have a relation datatype but the presence of a
    # listing or link renderer is a strong indication that this field is
    # a relation.
    if renderer in ["listing", "link"]:
        value = "relation"
    if value:
        value = value.encode("UTF-8")
    return ":{key}: {value}".format(key=key, value=value)


def _render_id(element):
    key = _('ID')
    value = element.attrib.get("id")
    if value:
        value = value.encode("UTF-8")
    return ":{key}: {value}".format(key=key, value=value)


def _render_help(element):
    key = _('Help')
    value = element.find(".//help")
    if value is not None:
        value = _(value.text.encode("UTF-8"))
        return ":{key}: {value}".format(key=key, value=value)
    return ""


def _get_renderer(element):
    renderer = element.find("renderer")
    if renderer is not None:
        value = renderer.attrib.get("type")
    else:
        value = "text"
    return value


def _render_renderer(element):
    key = _('Renderer')
    value = _get_renderer(element)
    if value:
        value = value.encode("UTF-8")
    return ":{key}: {value}".format(key=key, value=value)


def _render_rst_table(options):
    out = []
    out.append("")
    # Determine length of bars
    keys = options.keys()
    keys.append(_('Option'))
    values = options.values()
    values.append(_('Value'))
    mln = len(max(keys, key=len))
    mlv = len(max(values, key=len))
    out.append("%s %s" % (mln*"=", mlv*"="))
    out.append("%s %s" % (_('Value').ljust(mln), _('Option').ljust(mlv)))
    out.append("%s %s" % (mln*"=", mlv*"="))
    for k in sorted(options):
        value = options[k]
        k = k or "NULL"
        name = k.encode("UTF-8").ljust(mln)
        out.append("%s %s" % (name, value))
    out.append("%s %s" % (mln*"=", mlv*"="))
    out.append("")
    return "\n".join(out)


def _render_options(element):
    """TODO: Docstring for _render_options.

    :element: TODO
    :returns: TODO

    """
    options = {}
    for option in element.findall("options/option"):
        name = _(option.text.encode("UTF-8"))
        options[option.attrib.get('value')] = name
    if options:
        return reindent(_render_rst_table(options))
    return ""


def _render_rules(element):
    out = []
    rules = element.findall("rule")
    if len(rules) == 0:
        return ""
    out.append("\n**{}**\n\n".format(_("Rules")))
    for num, rule in enumerate(rules):
        key = "{0}.".format(num+1)
        value = rule.attrib.get("expr")
        msg = rule.attrib.get("msg", "")
        if value:
            value = value.encode("UTF-8")
        if msg:
            msg = ": {}".format(msg.encode("UTF-8"))
        out.append("{key} {value} {msg}".format(key=key, value=value, msg=msg))
        out.append("")
        out.append(reindent(render_meta(rule), 3))
    return "\n".join(out)


def render_meta(element, header=None, metatype=None):
    out = []
    if metatype:
        metaelements = element.findall("metadata/meta[@type='%s']" % metatype)
    else:
        metaelements = element.findall("metadata/meta")
    if len(metaelements) == 0:
        return ""

    if header:
        out.append("\n**{}**\n\n".format(header))
    for num, element in enumerate(metaelements):
        value = element.text
        date = element.attrib.get("date")
        if value:
            value = value.encode("UTF-8")
        out.append("{num}. {date} {value}".format(num=num+1, date=date, value=value))
    return "\n".join(out)


def render_field(element):
    out = []
    title = element.attrib.get("name")
    out.append("\n.. index:: {}\n".format(title))
    out.append("\n.. rubric:: {}\n".format(title))
    out.append(_render_label(element))
    out.append(_render_name(element))
    out.append(_render_required(element))
    out.append(_render_type(element))
    options = _render_options(element)
    if options:
        out.append(options)
    out.append(_render_id(element))
    out.append(_render_renderer(element))
    help_ = _render_help(element)
    if help_:
        out.append(help_)
    rules = _render_rules(element)
    if rules:
        out.append(rules)
    changes = render_meta(element, _('Changes'), "change")
    if changes:
        out.append(changes)
    comments = render_meta(element, _('Comments'), "comment")
    if comments:
        out.append(comments)
    return "\n".join(out)


def render_spec(config, title, form):
    out = []
    out.append("#"*len(title))
    out.append(title)
    out.append("#"*len(title))
    out.append(render_meta(config._tree))
    elements = get_spec_elements(config, form)
    num_elements = len(elements)
    for num, element in enumerate(elements):
        if element.tag == "page":
            out.append(render_page(element))
        elif element.tag == "section":
            out.append(render_section(element))
        elif element.tag == "subsection":
            out.append(render_subsection(element))
        elif element.tag == "entity":
            out.append(render_field(element))
            if num+1 < num_elements:
                out.append("\n-----\n")
        out.append("")
    outx = []
    for line in out:
        if isinstance(line, unicode):
            line = line.encode("utf8")
        outx.append(line)
    return "\n".join(outx)


def get_fields(config, node):
    elements = []
    for element in config.walk(node, {}, include_layout=True):
        if element.tag == "field":
            ref = element.attrib.get('ref')
            element = config._parent.get_element('entity', ref)
        elements.append(element)
    return elements


def get_spec_elements(config, form="update"):
    form_config = config.get_form(form)
    elements = []
    pages = form_config.get_pages()
    if len(pages) > 0:
        for page in pages:
            elements.append(page)
            elements.extend(get_fields(form_config, page))
    else:
        elements.extend(get_fields(form_config, form_config._tree))
    return elements


def main(args):
    config = _get_config(args.config)
    title = args.title or os.path.basename(args.config.name)
    print render_spec(config, title, args.form)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Convert a Formbar XML specification ' +
                    'file into various formats.')
    parser.add_argument('config', metavar='config',
            type=argparse.FileType('rU'), help='A form configuration file')
    parser.add_argument('--title', action='store',
            help="Choose title of the topmost rst heading (default: The filename)")
    parser.add_argument('--form', action='store', default='update',
            help="Choose which form to parse (default: 'update')")
    parser.add_argument('--translation', action='store',
            help="Path to translation MO file")
    args = parser.parse_args()
    if args.translation:
        gettext.bindtextdomain('formspec', args.translation)
        gettext.textdomain('formspec')
    else:
        _ = lambda x: x
    main(args)

# vim: set expandtab:
