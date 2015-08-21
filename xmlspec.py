#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import argparse
import xml.etree.ElementTree as ET
from tabulate import tabulate
from pprint import pprint


def reindent(s, numSpaces=3):
    s = s.split('\n')
    s = [(' ' * numSpaces) + line for line in s]
    s = '\n'.join(s)
    return s


def get_tree_dict(config):
    """ Parse XML; return a dict """
    tree = ET.parse(config)
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
                dict[id]['meta'][mtype] = []  # XXX Add headers?
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

def walk(node, tree, elements=None):
    if elements is None:
        elements = []
    for n in node.iter('*'):
        if n.tag in ['field', 'section', 'page', 'subsection']:
            #print('DEBUG A', n.tag, n.attrib)
            elements.append(n)
        elif n.tag == 'snippet':
            # find referenced snippet and start recursion
            if 'ref' in n.attrib:
                #print('DEBUG B', n.tag, n.attrib)
                snippet = tree.find("snippet[@id='{}']".format(n.attrib.get('ref')))
                #print('DEBUG C', snippet.tag, snippet.attrib)
                elements.extend(walk(snippet, tree, elements))
    return elements


def list_forms(config):
    tree = ET.parse(config)
    form_nodes = tree.iter('form')
    form_ids = []
    for f in form_nodes:
        form_ids.append(f.attrib.get('id'))
    return

def parse_form(config, form):
    tree = ET.parse(config)
    start_node = tree.find("form[@id='{}']".format(form))
    ordered_list = walk(start_node, tree)
    for e in ordered_list:
        print(e.tag, e.attrib)
    return ordered_list


def format_rst(tree_dict):
    """ Print an RST document to stdout """
    for entity in tree_dict:
        if entity == 'root_metadata':
            # e.g. create preamble
            continue
        # Section titlle
        sec_title = tree_dict[entity]['name']
        sec_underline = '-' * len(sec_title)
        print('{}\n{}'.format(sec_title, sec_underline))
        #
        print(u':Nummer: {}'.format(tree_dict[entity].get('number', '--')))
        print(u':Name: ``{}``'.format(tree_dict[entity]['name']))
        print(u':Tabelle: <TODO>')
        print(u':Modell: <TODO>')
        print(u':Teil: <TODO>')
        print(u':Abschnitt: <TODO>')
        print(u':Label: {}'.format(tree_dict[entity].get('label')))
        print(u':ID: {}'.format(tree_dict[entity]['id']))
        print(u':Datentyp: {}'.format(tree_dict[entity].get('type')))
        print(u':Darstellung: {}'.format(tree_dict[entity]['renderer']))
        print(u':Pflichtstatus: {}'.
                format(tree_dict[entity].get('requirement_level')))
        # Options
        print(u':Wertebereich:')
        print(reindent(tabulate(tree_dict[entity]['option'],
                ('Wert', 'Option'), tablefmt='rst')))
        # Rule
        print(u':F-Contraints: {}'.
                format(tree_dict[entity]['rule']['meta'].get('description',
                    'FEHLT!'), tablefmt='rst'))
        # Changes
        changes = tree_dict[entity]['meta'].get('change')
        if changes:
            print(u':Änderungen/Begründungen:')
            print(reindent(tabulate(tree_dict[entity]['meta'].get('change'),
                    ('Datum', u'Begründung'), tablefmt='rst')))
        else:
            print(u':Änderungen/Begründungen: Keine')
        # Print custom/free-form fields
        for free_label, free_text in tree_dict[entity]['meta'].get('free', []):
            print(u':{}: {}'.format(free_label, free_text))
        print('\n')


def main(config, format):
    # tmp
    #forms = list_forms(config)
    parse_form(config, 'update')
    return
    #
    tree_dict = get_tree_dict(config)
    if format == 'json':
        pprint(tree_dict)
    elif format == 'rst':
        format_rst(tree_dict)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Convert a Formbar XML specification file into various formats.')
    parser.add_argument('config', metavar='config', type=file,
            help='A form configuration file')
    parser.add_argument('--json', action='store_true', dest='format_json',
            default=False, help='Output in JSON format')
    parser.add_argument('--rst', action='store_true', dest='format_rst',
            default=True, help='Output in RST format (default)')
    args = parser.parse_args()
    if args.format_json:
        format = 'json'
    else:
        format = 'rst'
    main(args.config, format)

# vim: set expandtab:
