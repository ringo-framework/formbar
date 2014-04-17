import os
from formbar import static_dir

def get_css_files():
    files = ['css/datepicker3.css', 'css/formbar.css']
    css = []
    values = {}
    for filename in files:
        filepath = os.path.join(static_dir, filename)
        with open(filepath, 'r') as f:
            content = f.read()
        css.append((filename, content))
    return css

def get_js_files():
    files = ['js/bootstrap-datepicker.js', 'js/formbar.js', 'js/ace/ace.js', 
             'js/ace/ext-language_tools.js', 'js/ace/mode-xml.js', 
             'js/ace/snippets/xml.js', 'js/ace/snippets/text.js']
    js = []
    for filename in files:
        filepath = os.path.join(static_dir, filename)
        with open(filepath, 'r') as f:
            content = f.read()
        js.append((filename, content))
    return js

def get_css():
    """Returns the content of the formbar CSS file
    :returns: String with css
    """
    out = []
    for filename, content in get_css_files():
        out.append(content)
    return "".join(out)

def get_js():
    """Returns the content of the formbar JS file
    :returns: String with js
    """
    out = []
    for filename, content in get_js_files():
        out.append(content)
    return "".join(out)
