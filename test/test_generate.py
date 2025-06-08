import os
import unittest


class TestGenerate(unittest.TestCase):

    def test_source(self):
        this_dir = os.path.dirname(os.path.realpath(__file__))
        os.path.join(this_dir, "resource", "format", "markdown-format.yaml")
        os.path.join(this_dir, "resource", "format", "markdown-format.yaml")


if __name__ == '__main__':
    unittest.main()