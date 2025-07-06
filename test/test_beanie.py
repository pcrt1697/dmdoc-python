import unittest

from dmdoc.core.source.beanie_source import BeanieSource


class TestBeanie(unittest.TestCase):

    def test_declarative_source(self):
        config_dict = {
            "classes": "source.beanie_model:document_models",
            "id": "sample_schema"
        }
        source = BeanieSource.create(config_dict)
        dm = source.generate_data_model()
        self.assertEqual(dm.id, 'sample_schema')


if __name__ == '__main__':
    unittest.main()
