import pkg_resources
import os

base_dir = pkg_resources.get_distribution("formbar").location
template_dir = os.path.join(base_dir, 'templates')
test_dir = os.path.join(base_dir, 'tests')
