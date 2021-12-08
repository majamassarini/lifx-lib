import unittest
import doctest
import lifx


tests = list()
tests.append(doctest.DocTestSuite(lifx.lan.header))
tests.append(doctest.DocTestSuite(lifx.lan.light))
tests.append(doctest.DocTestSuite(lifx.lan.msg))

tests.append(doctest.DocFileSuite("../docs/source/example.rst", package=lifx))


def load_tests(loader, suite, ignore):
    for test in tests:
        suite.addTests(test)
    return suite


suite = unittest.TestSuite()
[suite.addTests(test) for test in tests]
runner = unittest.TextTestRunner(verbosity=2)
runner.run(suite)
