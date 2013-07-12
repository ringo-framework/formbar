import os


def get_css():
    """Returns the content of the formbar CSS file
    :returns: String with css
    """
    basepath = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    csspath = os.path.join(basepath, 'templates', 'formbar.css')
    with open(csspath, 'r') as f:
        return f.read()

def get_js():
    """Returns the content of the formbar JS file
    :returns: String with js 
    """
    files = ['bootstrap-datepicker.js', 'formbar.js']
    basepath = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    js = []
    for filename in files:
        jspath = os.path.join(basepath, 'templates', filename)
        with open(jspath, 'r') as f:
            js.append(f.read())
    return "".join(js)
