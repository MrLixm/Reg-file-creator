import os
import logging


class RegKey:

    key_index = 0

    def __init__(
        self, key_name, key_muiv, key_icon=None, key_command=None, parent=None
    ):
        r""" Utility to define the aspect of a windows registery key

        If key_command is None the key is assumed to be the root for subkeys

        Args:
            key_name(str): name of the key in the registery editor
            key_muiv(str): pretty name to be displayed on the context menu
            key_icon(str): path to the icons, think to escape \ to \\
            key_command(str): command to register in the key
            parent(RegKey, optional): parent this key is the child of.
        """
        self.parent = parent
        if parent:
            RegKey.key_index += 1
            self.key_name = f"{str(RegKey.key_index).zfill(3)}{key_name}"
        else:
            RegKey.key_index = 0
            self.key_name = f"{key_name}"
        self.key_muiv = key_muiv
        self.key_icon = key_icon
        self.key_command = key_command

    def write(self, reg_str, key_path):
        r"""

        Args:
            reg_str(str): string holding the current reg data and to add the keys data to
            key_path(str): root path of the key in the registery editor
                ex: HKEY_CLASSES_ROOT\SystemFileAssociations\.exr

        Returns:

        """
        if self.parent:
            if self.parent.parent:
                key_end = r"{}\shell\{}\shell\{}".format(
                    self.parent.parent.key_name, self.parent.key_name, self.key_name
                )
            else:
                key_end = r"{}\shell\{}".format(self.parent.key_name, self.key_name)
        else:  # Means this is a root key
            key_end = r"{}".format(self.key_name)

        data_base = rf"""[{key_path}\shell\{key_end}]
"MUIVerb" = "{self.key_muiv}" """

        if self.key_icon:
            data_base += rf"""
"icon" = "{self.key_icon}" 
            """

        if (
            not self.key_command
        ):  # if no command it means the key is the root for subkeys
            data_base += rf"""
"subCommands"=""
"""
        else:
            data_base += (
                "\n"
                + rf"""[{key_path}\shell\{key_end}\command]
@="{self.key_command}"
            """
            )

        reg_str += data_base + "\n"
        return reg_str


def create_reg(reg_file_path, delete_keys=False):
    """Create the reg file at the given location

    Args:
        delete_keys(bool): True to delete the keys instead of creating them (will add - in front of the keys in the reg file)
        reg_file_path(str): path where the .reg file should be created

    Returns:
        str: path to the created reg file

    """
    if delete_keys:
        keys_remove = "-"
    else:
        keys_remove = ""

    """ //Variables for the reg file """
    icon_logo_path01 = "./somepath/f.ico"
    icon_logo_path02 = "./somepath/f.ico"

    """ --------------------------------------------------------------------------------------------------------------
    Create the keys

    Key will appears in the context menu in the order you created them. It is recommanded to always create
    the parent first then the child. 
    """

    # define the locations of all the key, in this exemple we are going to associate them to the exr file format
    key_base_path = rf"{keys_remove}HKEY_CLASSES_ROOT\SystemFileAssociations\.exr"

    # this is the string will all the keys that is going to be exectued at the end
    reg_final_data = "Windows Registry Editor Version 5.00 \n"

    # Create root Key
    root_key_baguette = RegKey("Exemple_baguette", "Exemple Baguette", icon_logo_path01)
    reg_final_data = root_key_baguette.write(reg_final_data, key_base_path)

    # Create root Key 02
    root_key_fromage = RegKey("Exemple_fromage", "Exemple Fromage", icon_logo_path02)
    reg_final_data = root_key_fromage.write(reg_final_data, key_base_path)

    # ------------------------------------------------------------------------------------------------------------------
    # Create first keys
    fromagebuy_key = RegKey(
        "fromage_buy",
        "Buy Fromage",
        key_command=r"\"E:/app/app.exe\"  \"%1\" buy_fromage",
        parent=root_key_fromage,
    )
    reg_final_data = fromagebuy_key.write(reg_final_data, key_base_path)

    baguette01_key = RegKey("baguette_01", "Baguette 01", parent=root_key_baguette)
    reg_final_data = baguette01_key.write(reg_final_data, key_base_path)

    # ------------------------------------------------------------------------------------------------------------------
    # Create sub-keys

    # Baguette sub-key
    # ------------------------------------------------------------------------------------------------------------------
    eat_baguette = RegKey(
        "eat_baguette",
        "Eat the baguette",
        key_command=r"\"E:/app/app.exe\"  \"%1\" baguette_arg",
        parent=baguette01_key,
    )
    reg_final_data = eat_baguette.write(reg_final_data, key_base_path)

    destroy_baguette = RegKey(
        "destroy_baguette",
        "Destroy the baguette",
        key_command=r"\"E:/app/app.exe\"  \"%1\" baguette_destroy",
        parent=baguette01_key,
    )
    reg_final_data = destroy_baguette.write(reg_final_data, key_base_path)

    """ Write the .reg file"""

    with open(reg_file_path, "w+") as reg:
        reg.write(reg_final_data)

    if os.path.exists(reg_file_path):
        logging.info(f"Reg file created at: {reg_file_path}")
        return reg_file_path
    else:
        raise RuntimeError("Reg file not created")
