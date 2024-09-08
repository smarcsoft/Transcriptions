import unittest
import sys
sys.path.append('.')
from summarization import summarize

class TestSummarization(unittest.TestCase):

    def test_summarize_text(self):
        summarize("tests/testfiles/story.txt", None)

if __name__ == '__main__':
    print(sys.path)
    unittest.main()