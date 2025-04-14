def _get_version():
    import template.infra.init as init
    return init.get_version(__file__)


__version__ = _get_version()


def test(engine='unittests'):
    """
    Runs the tests specified by the engine, i.e. ::

        import template
        template.test(engine='unittests')

    Parameters
    ----------
    engine: str
        *'unittests': runs all unittests

    Returns
    -------
    None: None
      None if successful else sys.exit(1)
    """
    import template
    from template.infra.drive_tests import drive_tests
    return drive_tests(engine, template)


def dumpPackageData():
    """
    Dumps the PackageData yaml to a dictionary form

    Returns
    -------
    packageData object : dict
        object with the following structure:
          package_data:
              [path]: [filename1, filename2, ...]
          unpackage_data:
              [path]: [filename1, filename2, ...]
    """
    import template.infra.init as init
    return init.dumpPackageData(__file__)
