import unittest
import sys
sys.path.append('.')
from summarize import summarize_text

class TestSummarization(unittest.TestCase):

    def test_summarize_text(self):
        print(summarize_text("tests/testfiles/story.txt"))

if __name__ == '__main__':
    unittest.main()