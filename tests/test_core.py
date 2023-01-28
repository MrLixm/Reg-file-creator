import logging
import unittest
from pathlib import Path

import regcreator.core

logger = logging.getLogger(__name__)


def testcase01() -> regcreator.core.RegFile:
    # Key will appear in the context menu in the order you created them. It is recommanded to always create
    # the parent first then the child.

    reg_file = regcreator.core.RegFile()

    # define the locations of all the key, in this exemple we are going to associate them to the exr file format
    root_key = regcreator.core.RegRootKey(
        Path("HKEY_CLASSES_ROOT\\SystemFileAssociations\\.exr")
    )

    # Create root Key 01
    root_key_baguette = regcreator.core.RegKey(
        "Exemple_baguette",
        "Exemple Baguette",
        icon=Path("./somepath/f.ico"),
        parent=root_key,
    )
    reg_file.add_regkey(root_key_baguette)

    # Create root Key 02
    root_key_fromage = regcreator.core.RegKey(
        "Exemple_fromage",
        "Exemple Fromage",
        icon=Path("./somepath/f.ico"),
        parent=root_key,
    )
    reg_file.add_regkey(root_key_fromage)

    # ----------------------------------------------------------------------------------
    # Create first keys

    fromagebuy_key = regcreator.core.RegKey(
        "fromage_buy",
        "Buy Fromage",
        command=r"\"E:/app/app.exe\"  \"%1\" buy_fromage",
        parent=root_key_fromage,
    )
    reg_file.add_regkey(fromagebuy_key)

    baguette01_key = regcreator.core.RegKey(
        "baguette_01",
        "Baguette 01",
        parent=root_key_baguette,
    )
    reg_file.add_regkey(baguette01_key)

    # ------------------------------------------------------------------------------------------------------------------
    # Create sub-keys

    # Baguette sub-key
    # ------------------------------------------------------------------------------------------------------------------
    eat_baguette = regcreator.core.RegKey(
        "eat_baguette",
        "Eat the baguette",
        command=r"\"E:/app/app.exe\"  \"%1\" baguette_arg",
        parent=baguette01_key,
    )
    reg_file.add_regkey(eat_baguette)

    destroy_baguette = regcreator.core.RegKey(
        "destroy_baguette",
        "Destroy the baguette",
        command=r"\"E:/app/app.exe\"  \"%1\" baguette_destroy",
        parent=baguette01_key,
    )
    reg_file.add_regkey(destroy_baguette)

    return reg_file


class MyTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def _log(self, *args):
        msg = "[{}] ".format(self.id().split(".", 1)[-1])
        args = map(str, args)
        msg += " ".join(args)
        logger.info(msg)
        return

    def test_add_keys(self):

        reg_file = testcase01()
        print(reg_file.content())

        return

    def test_remove_keys(self):

        reg_file = testcase01()
        reg_file.set_removing(True)
        print(reg_file.content())

        return


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="[%(levelname)-7s] %(asctime)s [%(name)s]%(message)s",
    )
    unittest.main()
