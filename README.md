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
python -m regcreator "/z/whatever/test_reading_01.json" "./test.reg"
```

There is 2 reg files produced because one add the keys, and the other is to remove them.

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
    "Example_baguette": {
      "name": "Example Baguette",
      "icon": "./somepath/icon.ico",
      "children": {...}
    }
  }
}
```

The key of each item in the `children` dict is the unique name to represent
the regkey stored in the regitestry. Its value is a dict describing its configuration.

All the keys available for the "value dict" are :

```json
{
  "name": "pretty name to display in the windows interface",
  "icon": "path/to/an/icon",
  "command": "command to use when entry is executed by user",
  "children": {}
}
```