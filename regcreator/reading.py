import json
import logging
import os
import re
from contextlib import contextmanager
from pathlib import Path
from typing import Optional
from typing import Union

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


def replace_variable(source: str, variables: dict[str, str]):
    """

    Args:
        source: source string with variabel to replace
        variables: dict of variable name, variable value to replace in source

    Returns:
        source with all variables replaced
    """
    result = source

    for variable_name, variable_value in variables.items():

        pattern = re.compile(f"([^@]?)@{re.escape(variable_name)}")
        replace_by = f"{variable_value}".encode("unicode_escape").decode("ascii")
        replace_by = f"\\g<1>{replace_by}"
        result = pattern.sub(replace_by, result)

    unreplaced_variables = re.search(rf"[^@]?@[^@]", result)
    if unreplaced_variables:
        raise ValueError(
            f"Found variable that was not replaced: "
            f"<{unreplaced_variables.group()}> in <{result}>"
        )

    # "de-escape" escaped variable character
    result = re.sub(rf"([^@])@@([^@])", r"\g<1>@\g<2>", result)
    return result


def resolve_path(source_path: Union[str, Path]) -> Path:
    """
    Resolve all environement variable and make the given path absolute.
    """
    new_path = os.path.expandvars(str(source_path))
    new_path = new_path.lstrip('"').rstrip('"')
    new_path = Path(new_path).resolve()
    return new_path


def get_regkeys(
    regkey_data: dict[str, dict],
    parent: BaseRegKey,
    variables: Optional[dict[str, str]] = None,
) -> list[RegKey]:
    """
    Process recursively the regkey_data passed to extract RegKey instance from it.

    Args:
        regkey_data: dict data extracted from "children" key.
        parent:
        variables: dict of variable to replace in other dict key's values

    Returns:
        ordered list of RegKey
    """
    regkeys = []
    variables = variables or {}

    for top_key_name, top_key_data in regkey_data.items():

        name = top_key_data["name"]
        icon = top_key_data.get("icon")
        command = top_key_data.get("command")
        children = top_key_data.get("children")

        if children and command:
            raise ValueError(
                f"Error while parsing key <{top_key_name}>: "
                f'the key is defining both "children" and "command".'
            )

        if icon:
            icon = replace_variable(icon, variables=variables)
            icon = resolve_path(icon)

        if command:
            command = replace_variable(command, variables=variables)

        top_regkey = RegKey(
            name=top_key_name,
            pretty_name=name,
            parent=parent,
            icon=icon,
            command=command,
        )
        regkeys.append(top_regkey)

        if children:
            regkeys.extend(
                get_regkeys(children, parent=top_regkey, variables=variables)
            )

    return regkeys


def regfile_from_json(json_path: Path) -> RegFile:
    """

    Args:
        json_path: path to an existing json file

    Returns:
        a RegFile instance, ready to write to disk.
    """
    logger.info(f"reading {json_path}")
    json_data = json.loads(json_path.read_text("utf-8"))

    with edit_working_directory(json_path.parent):

        json_key_path: Union[str, list[str]] = json_data["path"]
        json_key_children: dict = json_data["children"]
        json_key_variables: dict = json_data.get("variables", {})
        json_key_variables_str: dict = json_key_variables.get("strings", {})
        json_key_variables_path: dict = json_key_variables.get("paths", {})
        json_key_variables_path = {
            k: str(resolve_path(v)) for k, v in json_key_variables_path.items()
        }

        variables = json_key_variables_str.copy()
        variables.update(json_key_variables_path)

        logger.debug(f"{variables=}")

        if isinstance(json_key_path, str):
            rootkey_list = [RegRootKey(Path(json_key_path))]

        else:
            rootkey_list = [RegRootKey(Path(key_path)) for key_path in json_key_path]

        regkeys = []

        for rootkey in rootkey_list:

            regkeys.extend(
                get_regkeys(
                    json_key_children,
                    parent=rootkey,
                    variables=variables,
                )
            )

    regfile = RegFile()
    for regkey in regkeys:
        regfile.add_regkey(regkey)

    return regfile
