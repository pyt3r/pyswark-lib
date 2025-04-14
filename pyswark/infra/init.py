from io import open
import os
import yaml
import re


def get_version(dunder_file):
    from pkg_resources import get_distribution, DistributionNotFound
    here = os.path.dirname(dunder_file)
    package = os.path.basename(here)

    try:
        version = get_distribution(package).version
    except DistributionNotFound:
        version = here
    return version


def dumpPackageData(dunder_file, filename='package.data.yaml'):
    """
    Dumps the PackageData yaml to a dictionary form

    Returns
    -------
    manifest object : dict
        manifest object with the following structure:
          package_data:
              [path]: [filename1, filename2, ...]
          unpackage_data:
              [path]: [filename1, filename2, ...]
    """
    basename, filename, manifest = getPackageData(dunder_file, filename)

    basedir = os.path.dirname(dunder_file)
    package_data = {basename: [filename], }
    for package_name, body in manifest['package_data'].items():
        arr = []
        for filepath, filenames in body.items():
            handler = PackageDataHanler(filenames)
            arr.extend(handler(basedir, filepath))
        package_data[package_name] = package_data.get(package_name, []) + arr
    return package_data


class PackageDataHanler:
    def __init__(self, filenames):
        self.nested = [f for f in filenames if '*' in f]
        self.flat = [f for f in filenames if '*' not in f]

    def __call__(self, basedir, filepath):
        arr = []
        arr.extend(self.runNested(basedir, filepath, self.nested))
        arr.extend(self.runFlat(filepath, self.flat))
        return arr

    @staticmethod
    def runNested(basedir, filepath, nested):
        walkDir = os.path.join(basedir, filepath)

        bad = ['__pycache__']
        def filt(tup): return all([b not in tup[0] for b in bad])

        arr = []
        for subdir, _, _ in filter(filt, os.walk(walkDir)):
            string = ''.join(subdir.split(basedir)[1:])
            parts = re.split(r'[\\/]', string)
            arr.extend([os.path.join(*parts, n) for n in nested])
        return arr

    @staticmethod
    def runFlat(filepath, filenames):
        arr = []
        parts = re.split(r'[\\/]', filepath)
        arr.extend([os.path.join(*parts, f) for f in filenames])
        return arr


def getPackageData(dunder_file, filename):
    """
    Reads the PackageData yaml

    Returns
    -------
    basename: str
    filename: str
    manifest: dict
    """
    here = os.path.abspath(os.path.dirname(dunder_file))
    basename = os.path.basename(here)
    manifest = yaml.load(
        open(
            os.path.join(
                here,
                filename),
            'rb'),
        Loader=yaml.SafeLoader)
    return basename, filename, manifest
