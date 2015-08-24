#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import xml.etree.ElementTree as ET
from tabulate import tabulate
from pprint import pprint


# Set RST section headers
#
# Sphinx convention: http://sphinx-doc.org/rest.html
#
#    # with overline, for parts
#    * with overline, for chapters
#    =, for sections
#    -, for subsections
#    ^, for subsubsections
#    ", for paragraphs
#
RST_SECTION_INDICATORS = (u'*', u'=', u'-', u'^', u'"')


def rst_title(title, level):
    """ Return title as an RST header of specified level """
    underline = RST_SECTION_INDICATORS[level] * len(title)
    if level == 0:  # Additional overline for certain high levels
        return '\n'.join([underline, title, underline])
    else:
        return '\n'.join([title, underline])


def reindent(s, numSpaces=3):
    """ Re-indent a multi-line string by a number of spaces (used for tables) """
    s = s.split('\n')
    s = [(' ' * numSpaces) + line for line in s]
    s = '\n'.join(s)
    return s


def walk(tree, node, elements=None):
    """
    Return a list of (relevant) elements of a given node.
    Follow refs recursively if necessary.
    """
    if elements is None:
        elements = []
    try:
        for n in node.iter('*'):
            if n.tag in ['field', 'section', 'page', 'subsection']:
                elements.append(n)
            elif n.tag == 'snippet':
                # find referenced snippet and start recursion
                if 'ref' in n.attrib:
                    snippet = tree.find("snippet[@id='{}']".format(n.attrib.get('ref')))
                    elements = walk(tree, snippet, elements)
    except AttributeError:
        pass
    return elements


def list_forms(tree):
    """ Return list of all forms defined in Formbar XML """
    form_nodes = tree.iter('form')
    form_ids = []
    for f in form_nodes:
        form_ids.append(f.attrib.get('id'))
    return form_ids


def parse_form(tree, form='update'):
    """ Return list of all (relevant) form items in document order """
    start_node = tree.find("form[@id='{}']".format(form))
    if start_node is None:
        return []
    ordered_list = walk(tree, start_node)
    return ordered_list


def get_tree_dict(tree):
    """ Parse XML; return a dict """
    dict = {}
    dict['root_metadata'] = {}
    # root document info
    root_metadata = tree.find('./metadata')
    if root_metadata is not None:
        for root_meta in root_metadata:
            mtype = root_meta.attrib.get('type')
            if mtype == 'intro':  # unique
                dict['root_metadata'][mtype] = root_meta.text
            else:  # potentially multiple items
                if not mtype in dict['root_metadata']:  # init list
                    dict['root_metadata'][mtype] = []
                dict['root_metadata'][mtype].append((root_meta.attrib.get('date'),
                        root_meta.text))
    # Individual entities
    for e in tree.iter('entity'):
        id = e.attrib.get('id')
        dict[id] = {}
        for name, value in e.attrib.items():
            dict[id][name] = value
        # Pflichtstatus
        if 'required' in dict[id]:
            dict[id]['requirement_level'] = 'Pflichtfeld'
        elif 'desired' in dict[id]:
            dict[id]['requirement_level'] = 'Forderfeld'
        # Renderer
        try:
            dict[id]['renderer'] = e.find('renderer').attrib.get('type')
        except AttributeError:
            dict[id]['renderer'] = 'NOT FOUND'
        # Options
        dict[id]['option'] = []
        for opt in e.findall('options/option'):
            option_value = opt.attrib.get('value')
            option_text = opt.text
            dict[id]['option'].append((option_value, option_text))
        # Metadata
        dict[id]['meta'] = {}
        for m in e.findall('metadata/meta'):
            mtype = m.attrib.get('type')
            if not mtype in dict[id]['meta']:  # init list
                dict[id]['meta'][mtype] = []
            if mtype == 'free':
                dict[id]['meta'][mtype].append((m.attrib.get('label'), m.text))
            else:
                dict[id]['meta'][mtype].append((m.attrib.get('date'), m.text))
        # Rule
        dict[id]['rule'] = {}
        dict[id]['rule']['meta'] = {}
        for r in e.findall('rule'):
            for name, value in r.attrib.items():
                dict[id]['rule'][name] = value
            for rule_meta in r.findall('metadata/meta'):
                mtype = rule_meta.attrib.get('type')
                if mtype == 'description':  # 'description' is unique per rule
                    dict[id]['rule']['meta'][mtype] = rule_meta.text
                elif not mtype in dict[id]['rule']['meta']:  # init list
                    dict[id]['rule']['meta'][mtype] = [('Datum', mtype)]
                    dict[id]['rule']['meta'][mtype].append(
                                (rule_meta.attrib.get('date'), rule_meta.text)
                            )
    return dict

def format_rst(tree_dict, form_layout=None):
    """ Print an RST document to stdout """
    out = []
    out.append(format_rst_intro(tree_dict))
    page = ''
    section = ''
    subsection = ''
    if form_layout is None:
        out.append(rst_title('Entities', 0))
        for entity in tree_dict:
            if entity != 'root_metadata':
                out.append(format_rst_entity(tree_dict, entity, section, subsection))
        return '\n'.join(out)
    for item in form_layout:
        if item.tag == 'page':
            # Print an RST section title to indicate Formbar form pages
            new_page = item.attrib.get('label')
            if new_page != page:  # Print page title (chapter in RST)
                out.append(rst_title(new_page, 0))
            page = new_page
        elif item.tag == 'section':
            new_section = item.attrib.get('label')
            if new_section != section:  # Print section title (chapter in RST)
                out.append(rst_title(new_section, 1))
            section = new_section
        elif item.tag == 'subsection':
            new_subsection = item.attrib.get('label')
            if new_section != subsection:  # Print subsection title (chapter in RST)
                out.append(rst_title(new_subsection, 2))
            subsection = new_subsection
        elif item.tag == 'field':
            entity = item.attrib.get('ref')
            out.append(format_rst_entity(tree_dict, entity, section, subsection))
    return '\n'.join(out)


def format_rst_intro(tree_dict):
    """ Print form root metadata in RST format """
    out = []
    node = 'root_metadata'
    title = u'Präambel'
    if tree_dict[node]:
        out.append(rst_title(title, 0))
    if 'intro' in tree_dict[node]:
        intro = tree_dict[node]['intro']
        out.append(intro + '\n')
    if 'comment' in tree_dict[node]:
        out.append(':Kommentare:')
        out.append(reindent(tabulate(tree_dict[node]['comment'],
                ('Datum', 'Kommentar'), tablefmt='rst')))
        out.append(u'\n')
    return '\n'.join(out)


def format_rst_entity(tree_dict, entity, section='', subsection=''):
    """ Print RST formatted information for a single entity """
    out = []
    # Section title
    name = tree_dict[entity]['id']
    out.append(rst_title(name, 3,))
    #
    out.append(u':Label: {}'.format(tree_dict[entity].get('label')))
    out.append(u':Nummer: {}'.format(tree_dict[entity].get('number', '--')))
    out.append(u':Name: ``{}``'.format(name))
    out.append(u':Teil: {}'.format(section))
    out.append(u':Abschnitt: {}'.format(subsection))
    out.append(u':Datentyp: {}'.format(tree_dict[entity].get('type')))
    out.append(u':Darstellung: {}'.format(tree_dict[entity]['renderer']))
    out.append(u':Pflichtstatus: {}'.
            format(tree_dict[entity].get('requirement_level')))
    # Options
    options = tree_dict[entity]['option']
    if options:
        out.append(u':Wertebereich:')
        out.append(reindent(tabulate(options,
                ('Wert', 'Option'), tablefmt='rst')))
    else:
        out.append(u':Wertebereich: Kein')
    # Rule
    rule_expr = tree_dict[entity]['rule'].get('expr')
    rule_desc = tree_dict[entity]['rule']['meta'].get('description')
    # Print meta description if available, else print rule expression verbatim
    if rule_desc:
        rule = rule_desc
    elif rule_expr:
        rule = '``{}``'.format(rule_expr)
    else:
        rule = 'Keine'
    out.append(u':F-Contsraints: {}'.format(rule))
    # Changes
    changes = tree_dict[entity]['meta'].get('change')
    if changes:
        out.append(u':Änderungen/Begründungen:')
        out.append(reindent(tabulate(tree_dict[entity]['meta'].get('change'),
                (u'Datum', u'Begründung'), tablefmt='rst')))
    else:
        out.append(u':Änderungen/Begründungen: Keine')
    # Print custom/free-form fields
    for free_label, free_text in tree_dict[entity]['meta'].get('free', []):
        out.append(u':{}: {}'.format(free_label, free_text))
    out.append(u'\n')
    return '\n'.join(out)


def main(args):
    tree = ET.parse(args.config)
    #forms = list_forms(config)  # disabled because we hard-coded the 'update' form below
    tree_dict = get_tree_dict(tree)
    if args.format_json:
        pprint(tree_dict)
    elif args.format_rst:
        form_layout = parse_form(tree, args.form)
        if form_layout:
            rst = format_rst(tree_dict, form_layout)
        else:
            rst = format_rst(tree_dict, None)
        print(rst.encode('utf-8'))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Convert a Formbar XML specification file into various formats.')
    parser.add_argument('config', metavar='config', type=file,
            help='A form configuration file')
    parser.add_argument('--form', action='store', default='update',
            help="Choose which form to parse (default: 'update')")
    parser.add_argument('--rst', action='store_true', dest='format_rst',
            default=True, help='Output in RST format (default)')
    parser.add_argument('--json', action='store_true', dest='format_json',
            default=False, help='Output in JSON format')
    args = parser.parse_args()
    # FIXME: not checking for mutual exclusive options etc.
    main(args)

# vim: set expandtab:
