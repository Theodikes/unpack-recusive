## Unpack-recusive

Recursive unpacking of archives of almost all popular extensions with different settings. Can be used both as a function in your code and as a standalone console program.

**NB!** This is a wrapper, that is, to unpack archives, you must have a program on your working machine that correctly processes archives of selected type. For example, on Windows, [7z](https://www.7-zip.org/) is suitable for almost all archive extensions.



## Usage as pip package

The module provides a single function `unpack_recursive`, that can be imported like this: `from unpack_recusive import unpack_recursive`

```python
def unpack_recursive(path: str, encrypted_files_action: Literal["skip", "default", "manually"] = "skip", default_passwords: Tuple[str] = (), remove_after_unpacking: bool = False, result_directory_exists_action: Literal["skip", "rename", "overwrite"] = "rename", verbosity_level: int = 0) -> Optional[str]
```

Unpacks an archive (or all archives in specified folder) recursively, i.e. the archive itself, all archives located in it, and all archives in folders and subfolders located in the archive and its subarchives.

##### Parameters:  

- **path:   string**

  Valid system path (absolute or relative) to the archive to be unpacked recursively, or to the directory where the archives are located

- **encrypted_files_action:  string, Literal["skip", "default", "manually"], default "skip"**

  What to do if the archive is encrypted. Three options: skip archive without decompressing ('skip' value), enter the password for each encrypted archive manually via stdin ('manually' value) or try to open the archive by sorting out passwords for it from a predefined array of default passwords ('default' value),  array of password is passed to function in next parameter

- **default_passwords: tuple of strings, default empty tuple - ()**
  Default password list used to open encrypted archives if 'encrypted_files_action' is set to 'default'
  **NB!** Don't pass too many passwords and don't use this to brute-force an archive - it's quite slow

- **remove_after_unpacking: bool, default 'False'**
  Delete successfully opened archives after full unpacking or not

- **result_directory_exists_action: Literal["skip", "rename", "overwrite"], default "rename"**

  What to do if final directory (archive name without extension) already exists. Three options: don't unpack current archive and do nothing with existing directory ('skip' value), delete existing directory and unpack archive into a new one ('overwrite' value) or do nothing with existing directory and unpack archive into renamed destination folder (if archive has name 'test.7z', and directory 'test' exists, unpack to directory 'test_1')

- **verbosity_level: integer, default 0**
  Console logging level: with verbosity level is '0', only errors are displayed, if less than zero, no information is displayed at all, if one or more, all debugging information is displayed

##### Returns: string or None, Optional[str]

​	Path to the final directory, where the archive was unpacked, or, if unpacking fails, None



## Usage as standalone console program

After installing the package via command `pip install unpack-recursive`, using console (from anywhere) you can call the program via `unpack-recursive` command.

Description of all parameters and in what format they need to be passed can be viewed using the `unpack-recursive -h` command in console.



## License

[GNU General Public License](https://www.gnu.org/licenses/gpl-3.0.en.html)