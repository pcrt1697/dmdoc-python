import os
import unittest

from dmdoc.core.formatter.markdown_formatter import MarkdownFormatter
from dmdoc.core.source.beanie_source import BeanieSource


class TestMarkdown(unittest.TestCase):

    def test_source(self):
        config_dict = {
            "classes": "source.beanie_model:document_models",
            "id": "sample_schema"
        }
        source = BeanieSource.create(config_dict)
        dm = source.generate_data_model()
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
