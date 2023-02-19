Python package to create context-menu entries in Windows by using .reg files.

Usable as a regular python package or as CLI with a .json input like below :

```
┌──────────────────────────┐
│ .json                    │
│                          │
│ define the key structure │
└─┬────────────────────────┘
  │
  │     ┌────────────┐
  └─────► regcreator │
        └──┬─────────┘
           │
           │   ┌─────────────────┐
           │   │ .reg            │
           ├───►                 │
           │   │ add the keys    │
           │   └─────────────────┘
           │
           │   ┌─────────────────┐
           │   │ .reg            │
           └───►                 │
               │ delete the keys │
               └─────────────────┘
```

Using a json to define the key structure allow us :
- have a more intuitive way of representing the key structure as nested dicts
- use relative path that are resolved to absolute in the reg file.
- avoid duplicating information by using variables that are replaced


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

3 keys at root :

```json
{
  "path": "path of the root keys to use",
  "children": {},
  "variables": {
    "strings": {},
    "paths": {}
  }
}
```

Where :

- `path` (`str` or `list[str]`): root path for each key in children. Can be a list
in that case all the `children` key will be duplicated for each root.
- `children` (`dict[str, dict]`): representing the structure of keys as dict of dicts
- `variables` (optional)(`dict[str, dict]`): variable to replace int he children keys.

### variable system

To avoid having to duplicate information across key, you can use a variable
system to only have one place where a value is defined.

#### declare

Variable are defined in the json on the root key `variables` that then have
2 sub-keys `strings` and `paths`. Both expects a key/value pair where the key
is the variable name, and the value is the variable valeu to replace.

The difference between `strings` and `paths` is that every value in `paths` will
be resolved to an absolute path. 

#### use

Variables can be used only in a child dict, in the `icon` or `command` dict key.
To use the variable the syntax is `@variableName` that will then be replaced by
the corresponding value.

The way to escape the `@` is to double it like `@@`, in that case `@@whatever`
will be resolved to `@whatever` in the reg file.

Example where I want to use a same file path across similar keys :

```json
{
  "path": "HKEY_CLASSES_ROOT\\SystemFileAssociations\\.exr",
  "children": {
    "programSomething": {
      "name": "Whatever",
      "icon": "./icon.ico",
      "command": "cmd.exe /k @myProgram %1 clientmail@@gmail.com"
    },
    "batSomething": {
      "name": "I still don't know",
      "icon": "./icon2.ico",
      "command": "cmd.exe /k @myBat %1"
    }
  },
  "variables": {
    "paths": {"myProgram":  "C:/tools/myProgram.exe", "myBat":  "./myBat.bat"}
  }
}
```

### children key

`children` represent a dict of regkeys, where each can also have children define
the same way.

the dict key is the name of the reg key, and the value is a dict with a structure
expected like :

```json
{
  "path": "HKEY_CLASSES_ROOT\\SystemFileAssociations\\.exr",
  "children": {
    "name_of_the_key": {
      "name": "name but in GUI",
      "icon": "./somepath/icon.ico",
      "command": "cmd.exe /k echo I work !",
      "children": {}
    }
  }
}
```

You can create sub-menu entry, that are nested, using the `children` key.

Keys available are :

- `name` (mandatory): pretty name to display in the windows interface
- `icon` (optional): absolute or relative file path to an icon image (.ico). 
If relative, the working directory will be the one of the json file. 
(note that environment variable are also supported thanks to `os.path.expandsvars`)
- `command` (optional): command to execute when clicked. Can only be added if the RegKey doesn't have children.
- `children` (optional): dict of sub-menu entries to add.
