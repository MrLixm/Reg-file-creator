import logging
import unittest
from pathlib import Path

import regcreator.reading

logger = logging.getLogger(__name__)

DATA_01 = Path(__file__).parent / "data" / "test_reading_01.json"
DATA_02 = Path(__file__).parent / "data" / "test_reading_02.json"


class Test_regfile_from_json(unittest.TestCase):
    def test_data01(self):
        regfile = regcreator.reading.regfile_from_json(json_path=DATA_01)
        print(regfile.content())

    def test_data02(self):
        regfile = regcreator.reading.regfile_from_json(json_path=DATA_02)
        print(regfile.content())


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)-7s] %(asctime)s [%(name)s]%(message)s",
    )
    unittest.main()
