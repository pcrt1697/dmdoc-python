import unittest

from dmdoc.core.source.sqlalchemy_source import SQLAlchemySource


class TestSQLAlchemy(unittest.TestCase):
    # todo: check what happens when table models are defined in different modules

    def test_declarative_source(self):
        config_dict = {
            "base": "source.sqlalchemy_model:Base",
            "id": "sample_schema"
        }
        source = SQLAlchemySource.create(config_dict)
        dm = source.generate_data_model()
        self.assertEqual(dm.id, 'sample_schema')

    def test_imperative_source(self):
        config_dict = {
            "base": "source.sqlalchemy_model:mapper_registry",
            "id": "sample_schema"
        }
        source = SQLAlchemySource.create(config_dict)
        dm = source.generate_data_model()
        self.assertEqual(dm.id, 'sample_schema')


if __name__ == '__main__':
    unittest.main()
