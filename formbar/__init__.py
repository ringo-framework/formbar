import pkg_resources
import os
import logging

# @XXX: How to set the log level from within the application which uses
# formbar?
logging.basicConfig()

base_dir = pkg_resources.get_distribution("formbar").location
template_dir = os.path.join(base_dir, 'formbar', 'templates')
static_dir = os.path.join(base_dir, 'formbar', 'static')
test_dir = os.path.join(base_dir, 'test')
example_dir = os.path.join(base_dir, 'examples')
