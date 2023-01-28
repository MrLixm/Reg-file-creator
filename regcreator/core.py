from __future__ import annotations

import abc
import logging
from pathlib import Path

import regcreator

logger = logging.getLogger(__name__)


class BaseRegKey(abc.ABC):
    def __init__(self):
        self._removing = False

    @abc.abstractproperty
    def key_path(self) -> Path:
        pass

    def set_removing(self, removing: bool):
        """
        Configure if the key should be added or removed from the registery.

        Args:
            removing: True so the key is removed of the registery.
        """
        self._removing = removing


class RegRootKey(BaseRegKey):
    def __init__(self, key_path: Path):
        super().__init__()
        self._key_path = key_path

    @property
    def key_path(self) -> Path:
        return self._key_path


class RegKey(BaseRegKey):

    key_index = 0

    def __init__(
        self,
        name: str,
        pretty_name: str,
        parent: BaseRegKey,
        icon: Path | None = None,
        command: str | None = None,
    ):
        r"""
        Utility to define the aspect of a windows registery key

        If key_command is None the key is assumed to be the root for subkeys

        Args:
            name: name of the key in the registery editor
            pretty_name: pretty name to be displayed on the context menu
            parent: parent this key is the child of.
            icon: path to the icons
            command: command to register in the key
        """
        super().__init__()

        if isinstance(parent, RegRootKey):

            RegKey.key_index = 0
            self.key_name = f"{name}"

        else:

            RegKey.key_index += 1
            self.key_name = f"{str(RegKey.key_index).zfill(3)}{name}"

        self.parent = parent
        self.key_muiv = pretty_name
        self.icon_path = icon
        self.key_command = command

    def __str__(self) -> str:
        """
        Get the full key representation as a writable to disk string.
        """
        remove_prefix = "-" if self._removing else ""

        out_str = f"[{remove_prefix}{self.key_path}]\n"

        out_str += f'"MUIVerb"="{self.key_muiv}"\n'
        if self.icon_path:
            out_str += f'"icon"="{repr(str(self.icon_path))[1:][:-1]}"\n'

        if self.key_command:
            out_str += f'[{remove_prefix}{self.key_path / "command"}]\n'
            out_str += f'@="{self.key_command}"\n'

        # if no command it means the key is the root for subkeys
        else:
            out_str += f'"subCommands"=""\n'

        return out_str

    @property
    def key_path(self) -> Path:
        return self.parent.key_path / "shell" / self.key_name


class RegFile:
    """
    A .reg file generated from scracth as a python object.
    """

    def __init__(self):
        self._comments_header: list[str] = []
        self._reg_keys_list: list[BaseRegKey] = []

    def add_regkey(self, reg_key: RegKey):
        self._reg_keys_list.append(reg_key)

    def content(self) -> str:

        content = ""
        content += "Windows Registry Editor Version 5.00\n\n"
        content += f"; File auto generated from regcreator python package v{regcreator.__version__}.\n"
        for comment in self._comments_header:
            content += f"; {comment}\n"
        content += "\n"

        for reg_key in self._reg_keys_list:
            content += str(reg_key) + "\n"

        return content

    def insert_header_comment(self, comment: str):
        """
        Args:
            comment: message to add as comment in the header of the file.
        """
        return self._comments_header.append(comment)

    def set_removing(self, removing: bool):
        """
        Configure if the keys should be added or removed from the registery.

        Args:
            removing: True so the keys are removed of the registery.
        """
        for reg_key in self._reg_keys_list:
            reg_key.set_removing(removing)

    def write_to(self, export_path: Path):
        """
        Args:
            export_path: absolute path to a file to write on disk. Must include .reg extension.
        """
        logger.info(f"About to write <{export_path}> to disk ...")
        export_path.write_text(self.content(), encoding="utf-8")

        if not export_path.exists():
            raise RuntimeError(f"Reg File <{export_path}> not created")
