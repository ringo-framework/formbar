import xml.etree.ElementTree as ET
from formbar.config import get_text_and_html_content


def extract_i18n_formconfig(fileobj, keywords, comment_tags, options):
    """Extract messages from XML form configuration files.
    :param fileobj: the file-like object the messages should be extracted
                    from
    :param keywords: a list of keywords (i.e. function names) that should
                     be recognized as translation functions
    :param comment_tags: a list of translator tags to search for and
                         include in the results
    :param options: a dictionary of additional options (optional)
    :return: an iterator over ``(lineno, funcname, message, comments)``
             tuples
    :rtype: ``iterator``
    """

    config = ET.parse(fileobj).getroot()

    # FIXME: Fix linenumbering. No real linenummer, just iterate somehow
    lineno = 0
    for entitytoken in config.iter('entity'):
        lineno += 1
        # "_" is one of the default keywords which marks a string
        # for extraction. As the json file does not have any
        # keywords. Set a dummy funcname here.
        yield (lineno,
               "_",
               entitytoken.attrib.get('label'),
               ["Label for %s field in form config"
                % (entitytoken.attrib.get('name'))])
    for helptoken in config.iter('help'):
        lineno += 1
        # "_" is one of the default keywords which marks a string
        # for extraction. As the json file does not have any
        # keywords. Set a dummy funcname here.
        yield (lineno,
               "_",
               get_text_and_html_content(helptoken),
               [])
    for ruletoken in config.iter('rule'):
        lineno += 1
        # "_" is one of the default keywords which marks a string
        # for extraction. As the json file does not have any
        # keywords. Set a dummy funcname here.
        yield (lineno,
               "_",
               ruletoken.attrib.get('msg'),
               [])
    for valtoken in config.iter('validator'):
        lineno += 1
        # "_" is one of the default keywords which marks a string
        # for extraction. As the json file does not have any
        # keywords. Set a dummy funcname here.
        yield (lineno,
               "_",
               valtoken.attrib.get('msg'),
               [])
    for ruletoken in config.iter('page'):
        lineno += 1
        # "_" is one of the default keywords which marks a string
        # for extraction. As the json file does not have any
        # keywords. Set a dummy funcname here.
        yield (lineno,
               "_",
               ruletoken.attrib.get('label'),
               [])
    for ruletoken in config.iter('section'):
        lineno += 1
        # "_" is one of the default keywords which marks a string
        # for extraction. As the json file does not have any
        # keywords. Set a dummy funcname here.
        yield (lineno,
               "_",
               ruletoken.attrib.get('label'),
               [])
    for ruletoken in config.iter('subsection'):
        lineno += 1
        # "_" is one of the default keywords which marks a string
        # for extraction. As the json file does not have any
        # keywords. Set a dummy funcname here.
        yield (lineno,
               "_",
               ruletoken.attrib.get('label'),
               [])
    for ruletoken in config.iter('subsubsection'):
        lineno += 1
        # "_" is one of the default keywords which marks a string
        # for extraction. As the json file does not have any
        # keywords. Set a dummy funcname here.
        yield (lineno,
               "_",
               ruletoken.attrib.get('label'),
               [])
    for ruletoken in config.iter('fieldset'):
        lineno += 1
        # "_" is one of the default keywords which marks a string
        # for extraction. As the json file does not have any
        # keywords. Set a dummy funcname here.
        yield (lineno,
               "_",
               ruletoken.attrib.get('label'),
               [])
    for ruletoken in config.iter('text'):
        lineno += 1
        # "_" is one of the default keywords which marks a string
        # for extraction. As the json file does not have any
        # keywords. Set a dummy funcname here.
        yield (lineno,
               "_",
               ruletoken.text,
               [])
    for optiontoken in config.iter('option'):
        lineno += 1
        # "_" is one of the default keywords which marks a string
        # for extraction. As the json file does not have any
        # keywords. Set a dummy funcname here.
        yield (lineno,
               "_",
               optiontoken.text,
               [])
    for buttontoken in config.iter('button'):
        lineno += 1
        # "_" is one of the default keywords which marks a string
        # for extraction. As the json file does not have any
        # keywords. Set a dummy funcname here.
        yield (lineno,
               "_",
               buttontoken.text,
               [])
