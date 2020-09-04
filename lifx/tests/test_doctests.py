import unittest
import doctest
import lifx


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(lifx.lan.header))
    tests.addTests(doctest.DocTestSuite(lifx.lan.light))
    tests.addTests(doctest.DocTestSuite(lifx.lan.msg))

    return tests
