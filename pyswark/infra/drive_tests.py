import sys
import os
import coverage
import unittest


def drive_tests(engine, package):
    drive = Driver(engine)
    err, result, cov = drive(package)
    code = 1 if err else 0
    sys.exit(code)


class Driver:
    ENGINES = {
        'unittests': 'unittests', }

    def __init__(self, engine):
        ENGINES = Driver.ENGINES
        if engine not in ENGINES:
            raise ValueError(engine, ENGINES.keys())
        self.engine = ENGINES[engine]

    def __call__(self, *args, **kwargs):
        fun = getattr(self, self.engine)
        return fun(*args, **kwargs)

    @staticmethod
    def unittests(package):
        j = os.path.join
        source = os.path.dirname(package.__file__)
        testDir = j(source, 'tests')
        unittestsDir = j(testDir, 'unittests')

        cov = coverage.Coverage(source=[source])
        cov.start()
        suite = unittest.TestLoader().discover(start_dir=unittestsDir)
        result = unittest.TextTestRunner().run(suite)
        cov.stop()

        isFailure = True if result.errors or result.failures else False
        report = None
        if not isFailure:
            cov.save()
            include = j(source, '*')
            omit = j(testDir, '*')
            report = cov.report(include=include, omit=omit)
            cov.html_report(include=include, omit=omit)
            cov.xml_report(include=include, omit=omit)
        return isFailure, result, report
