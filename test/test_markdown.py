import os
import unittest

from dmdoc.core.formatter.markdown_formatter import MarkdownFormatter
from dmdoc.core.source.sqlalchemy_source import SQLAlchemySource


class TestMarkdown(unittest.TestCase):

    def test_source(self):
        source = SQLAlchemySource.create(
            {
                "base": "source.sqlalchemy_model:Base",
                "id": "sample_schema"
            }
        )
        dm = source.process()
        this_dir = os.path.dirname(os.path.realpath(__file__))
        formatter = MarkdownFormatter.create(
            dm,
            {
                "output_path": os.path.join(this_dir, "resource", "test_markdown.md"),
                "overwrite": True
            }
        )
        formatter.generate()


if __name__ == '__main__':
    unittest.main()
