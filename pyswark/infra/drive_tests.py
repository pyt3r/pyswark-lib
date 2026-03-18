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
        'unittests': 'unittests',
        'integration': 'integration',
    }

    def __init__(self, engine):
        ENGINES = Driver.ENGINES
        if engine not in ENGINES:
            raise ValueError(engine, ENGINES.keys())
        self.engine = ENGINES[engine]

    def __call__(self, *args, **kwargs):
        fun = getattr(self, self.engine)
        return fun(*args, **kwargs)

    @classmethod
    def unittests(cls, package):
        return cls._run_test_suite(package, "unittests")

    @classmethod
    def integration(cls, package):
        return cls._run_test_suite(package, "integration")

    @staticmethod
    def _run_test_suite(package, suite_dir_name: str):
        """
        Discover and run a unittest suite with coverage.

        Parameters
        ----------
        package:
            Imported package (used to locate its filesystem path).
        suite_dir_name:
            Either ``unittests`` or ``integration`` (relative to ``<package>/tests``).
        """
        j = os.path.join
        source = os.path.dirname(package.__file__)
        testDir = j(source, "tests")
        suiteDir = j(testDir, suite_dir_name)

        cov = coverage.Coverage(source=[source])
        cov.start()

        suite = unittest.TestLoader().discover(start_dir=suiteDir)
        result = unittest.TextTestRunner().run(suite)

        cov.stop()

        isFailure = True if result.errors or result.failures else False
        report = None

        if not isFailure:
            cov.save()
            include = j(source, "*")
            omit = j(testDir, "*")
            report = cov.report(include=include, omit=omit)
            cov.html_report(include=include, omit=omit)
            cov.xml_report(include=include, omit=omit)

        return isFailure, result, report
