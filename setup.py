import yaml
from setuptools import setup, find_packages
from os import path
from io import open
import importlib


here = path.abspath(path.dirname(__file__))
meta = yaml.load(open(path.join(here, 'conda-recipe', 'meta.yaml'), 'rb'), Loader=yaml.SafeLoader)
name = meta['package']['name']
package = importlib.import_module(name)
package_data = package.dumpPackageData()


setup(
    name         = name,
    version      = str(meta['package']['version']),
    description  = meta['about']['summary'],
    author       = meta['about']['author'],
    packages     = find_packages(),
    package_data = package_data,
    entry_points = {
        'console_scripts' : meta['build'].get('entry_points', {}),
    }
)
