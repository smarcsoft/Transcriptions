import unittest

if __name__ == "__main__":
    test_suite = unittest.defaultTestLoader.discover('tests', pattern='test_*.py')
    unittest.TextTestRunner().run(test_suite)