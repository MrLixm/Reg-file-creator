Python package to create context-menu entries in windows via .reg file.

Usable as a regular python package or as CLI with a .json input.

# Usage

## Python

See [test_core.py](tests/test_core.py) for a full example.

```python
from pathlib import Path
import regcreator.core

root_key = regcreator.core.RegRootKey(
    Path("HKEY_CLASSES_ROOT\\SystemFileAssociations\\.exr")
)

# Create top entry
top_key_fromage = regcreator.core.RegKey(
    "Exemple_fromage",
    "Exemple Fromage",
    icon=Path("./somepath/f.ico"),
    parent=root_key,
)

# Create sub-entry
key_eat_baguette = regcreator.core.RegKey(
    "eat_baguette",
    "Eat the baguette",
    command=r"\"E:/app/app.exe\"  \"%1\" baguette_arg",
    parent=top_key_fromage,
)
```

## CLI

```shell
# open CLI help
cd source/of/the/git/repo
python -m regcreator --help
```

To read the reg structure from a json file and concert it to 2 reg files :

```shell
python -m regcreator "/z/whatever/test_reading_01.json"
```

With the above command,tThere is 2 reg files produced next to the original json:
one add the keys, and the other is to remove them.

## JSON structure

See [test_reading_01.json](tests/data/test_reading_01.json) for example.

2 keys at root :

```json
{
  "path": "path of the root keys to use",
  "children": {}
}
```

Then `children` represent a dict of regkeys, where each can also have children.

```json
{
  "path": "HKEY_CLASSES_ROOT\\SystemFileAssociations\\.exr",
  "children": {
    "test_me": {
      "name": "Test Me",
      "icon": "./somepath/icon.ico",
      "command": "cmd.exe /k echo I work !",
      "children": {}
    }
  }
}
```

The above json will produce a reg file that once executed will led to 
add a new single context menu entry named "Test Me" when right-clicking an .exr file.

You can create sub-menu entry, that are nested, using the `children` key.

Keys available are :

- `name` (mandatory): pretty name to display in the windows interface
- `icon` (optional): absolute or relative file path to an icon image (.ico). 
If relative, the working directory will be the one of the json file.
- `command` (optional): command to execute when clicked. Can only be added if the RegKey doesn't have children.
- `children` (optional): dict of sub-menu entries to add.
