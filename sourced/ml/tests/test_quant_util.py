import os
import unittest

from sourced.ml.transformers import ParquetLoader, UastRow2Document, UastDeserializer
from sourced.ml.extractors import ChildrenBagExtractor
from sourced.ml.models import QuantizationLevels
from sourced.ml.utils.quant import create_or_apply_quant
from sourced.ml.utils import create_spark

import sourced.ml.tests.models as paths


class MyTestCase(unittest.TestCase):
    def test_apply(self):
        extractor = ChildrenBagExtractor()
        create_or_apply_quant(paths.QUANTLEVELS, [extractor])
        self.assertIsNotNone(extractor.levels)
        model_levels = QuantizationLevels().load(source=paths.QUANTLEVELS)._levels["children"]
        for key in model_levels:
            self.assertListEqual(list(model_levels[key]), list(extractor.levels[key]))

    def test_create(self):
        session = create_spark("test_quant_util")
        extractor = ChildrenBagExtractor()
        path = "/tmp/quant.asdf"
        uast_extractor = ParquetLoader(session, paths.PARQUET_DIR) \
            .link(UastRow2Document()) \
            .link(UastDeserializer())
        create_or_apply_quant(path, [extractor], uast_extractor)
        self.assertIsNotNone(extractor.levels)
        self.assertTrue(os.path.exists(path))
        model_levels = QuantizationLevels().load(source=path)._levels["children"]
        for key in model_levels:
            self.assertListEqual(list(model_levels[key]), list(extractor.levels[key]))
        os.remove(path)


if __name__ == '__main__':
    unittest.main()
