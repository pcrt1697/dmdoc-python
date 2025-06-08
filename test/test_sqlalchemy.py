import unittest

from dmdoc.core.source.sqlalchemy_source import SQLAlchemySource


class TestSQLAlchemy(unittest.TestCase):

    def test_declarative_source(self):
        config_dict = {
            "base": "source.sqlalchemy_model:Base",
            "id": "sample_schema"
        }
        source = SQLAlchemySource.create(config_dict)
        dm = source.process()
        self.assertEqual(dm.id, 'sample_schema')

    def test_imperative_source(self):
        config_dict = {
            "base": "source.sqlalchemy_model:mapper_registry",
            "id": "sample_schema"
        }
        source = SQLAlchemySource.create(config_dict)
        dm = source.process()
        self.assertEqual(dm.id, 'sample_schema')


if __name__ == '__main__':
    unittest.main()
