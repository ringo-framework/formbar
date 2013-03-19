import os


def get_css():
    """Returns the content of the formbar CSS file
    :returns: String with css
    """
    basepath = os.path.join(os.path.dirname(os.path.abspath(__file__)))
    csspath = os.path.join(basepath, 'templates', 'formbar.css')
    with open(csspath, 'r') as f:
        return f.read()
