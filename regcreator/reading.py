import json
import logging
import os
from contextlib import contextmanager
from pathlib import Path

from regcreator.core import BaseRegKey
from regcreator.core import RegKey
from regcreator.core import RegFile
from regcreator.core import RegRootKey

logger = logging.getLogger(__name__)


@contextmanager
def edit_working_directory(new_cwd: Path):
    """
    Context to change the cwd to the given one and restore to the previous one once finished.
    """
    previous = Path.cwd()
    os.chdir(new_cwd)
    try:
        yield
    finally:
        os.chdir(previous)


def get_regkeys(regkey_data: dict[str, dict], parent: BaseRegKey) -> list[RegKey]:
    """
    Process recursively the regkey_data passed to extract RegKey instance from it.

    Args:
        regkey_data: dict data extracted from "children" key.
        parent:

    Returns:
        ordered list of RegKey
    """
    regkeys = []

    for top_key_name, top_key_data in regkey_data.items():

        icon = top_key_data.get("icon")
        if icon:
            icon = Path(icon).resolve().absolute()

        command = top_key_data.get("command")

        top_regkey = RegKey(
            name=top_key_name,
            pretty_name=top_key_data["name"],
            parent=parent,
            icon=icon,
            command=command,
        )
        regkeys.append(top_regkey)
        children = top_key_data.get("children")
        if children and command:
            raise ValueError(
                f"Error while parsing key <{top_key_name}>: "
                f'the key is defining both "children" and "command".'
            )
        elif children:
            regkeys.extend(get_regkeys(children, parent=top_regkey))

    return regkeys


def regfile_from_json(json_path: Path) -> RegFile:
    """

    Args:
        json_path: path to an existing json file

    Returns:
        a RegFile instance, ready to write to disk.
    """

    json_data = json.loads(json_path.read_text("utf-8"))

    with edit_working_directory(json_path.parent):

        root_regkey = RegRootKey(Path(json_data["path"]))
        regkeys = get_regkeys(json_data["children"], parent=root_regkey)

        regfile = RegFile()
        for regkey in regkeys:
            regfile.add_regkey(regkey)

    return regfile
