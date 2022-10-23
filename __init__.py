from os import listdir, remove, rmdir
from os.path import isdir, isfile, splitext, basename, join, dirname, exists
from patool_unpack import get_archive_format, check_archive_format, test_archive, extract_archive, ArchiveFormats
from patool_unpack.util import PatoolError
from typing import Optional, Tuple


def is_encrypted(path_to_archive: str, verbosity_level: int = 0) -> bool:
    """returns bool value - is archive password-protected or not - by path fi archive file"""
    # To find out if the archive is encrypted, we will try to open the archive with the wrong password,
    # if there is no password - it will open, if there is a password - it will give an error
    try:
        # To find out if the archive is encrypted, we check it with a guaranteed wrong password
        test_archive(path_to_archive, interactive=False, password='FakePwd', verbosity=verbosity_level)
        return False
    except PatoolError as e:
        # for some types of archives, the password is not supported in principle,
        # so the error does not mean that the file is password-protected
        if "no support for password" in str(e) or "password is not supported" in str(e):
            return False
        if verbosity_level >= 0:
            print(e)
        return True


def get_filename_from_path(path: str) -> str:
    """returns filename without extension and dot from absolute or relative path to file"""
    return splitext(basename(path))[0]


def get_extension_without_dot_from_path(path: str) -> Optional[str]:
    """returns the file extension without a dot from file path, if the file has no extension - returns None"""
    return splitext(basename(path))[1][1:] if splitext(basename(path))[1] else None


def is_archive(file_path: str) -> bool:
    """returns true if file by specified path is supported (unpackable with patool) archive, false otherwise"""
    try:
        file_extension = get_extension_without_dot_from_path(file_path)
        # first carry out a basic check of the file extension to immediately discard unsuitable files
        if file_extension and (file_extension in ArchiveFormats or file_extension in ['gz', 'bz2', 'lz', 'xz']):
            # if the simple check is passed, we call patool, which will fully check if the file is an archive
            check_archive_format(*get_archive_format(file_path))
            return True
        return False
    # since Patool throws an error with a negative result, if it fell out, file is definitely not an archive
    except PatoolError:
        return False


def get_result_extract_dir_renamed_path(archive_extract_dir: str) -> str:
    """
    creates a unique path to the resulting directory so that it does not match other folder or file paths

    :param str archive_extract_dir: already occupied path, on the basis of which a new one is generated
    :return: final (generated by adding ordinal numbers to original path) guaranteed free path
             where the folder can be created
    :rtype: str
    """
    dir_number = 1
    # generate names by incrementing the number at the end, e.g. 'folder_1', 'folder_2' and so on
    archive_extract_dir_renamed = archive_extract_dir + "_" + str(dir_number)
    while isdir(archive_extract_dir_renamed):
        dir_number += 1
        archive_extract_dir_renamed = archive_extract_dir + "_" + str(dir_number)

    return archive_extract_dir_renamed


def unpack_recursive(path: str, encrypted_files_action: str = "skip",  default_passwords: Tuple[str] = (),
                     remove_after_unpacking: bool = False, result_directory_exists_action: str = "rename",
                     verbosity_level: int = 0) -> Optional[str]:
    """
    Unpacks the specified archive or all archives in the specified folder and their subfolders

    :param str path: Path (relative or absolute) to archive or folder with archives and subfolders
    :param str encrypted_files_action: What to do with encrypted archives - skip, try to open with the default password
                                       or prompt the user for each archive ("skip", "default" or "manually")
    :param Tuple[str] default_passwords: List of default passwords for encrypted archives, if empty list, all
                                        password-protected archives will be skipped
    :param bool remove_after_unpacking: Delete archive files after unpacking or not
    :param str result_directory_exists_action: What to do if the final directory after unpacking the archive already
                                               exists or there are duplicates among the file names in the archive:
                                               skip existing, overwrite existing or rename new files/folders.
                                               Allowed values - 'skip', 'overwrite', 'rename'. Default - 'rename'
    :param int verbosity_level: Logging to user in console: -1 - completely absent, 0 - only errors,
                            1 - all important information (default - 0)
    :returns: path to the folder where the archive was unpacked, or to the root folder
              where the archives were located or 'None', if unpacking fails
    :rtype: Optional[string]
    :raise: Nothing, return None if anything goes wrong
    """

    try:
        # If the path is a directory, recursively call the same function for all subfolders
        if isdir(path):
            for sub_path in listdir(path):
                unpack_recursive(join(path, sub_path), encrypted_files_action, default_passwords,
                                 remove_after_unpacking, result_directory_exists_action, verbosity_level)
            # Return the path to the source (input) directory, since all the archives in it will be unpacked inside it
            return path

        # If the file is an archive, try to unpack it
        elif isfile(path) and is_archive(path):
            # The final folder where the archive is unpacked - root folder + name of the archive without extension
            # For example, for a 'test.tar' archive, all unpacked files will be in the '/test' folder
            # in the same directory as the archive
            archive_directory: str = dirname(path)
            archive_filename_without_extension: str = get_filename_from_path(path)
            archive_extract_dir: str = join(archive_directory, archive_filename_without_extension)

            # If archive is encrypted, check what action the user chose, if not 'skip' - try to decrypt
            # archive for verification, if an error occurs - exit
            is_archive_encrypted: bool = is_encrypted(path, verbosity_level)
            default_password: Optional[str] = None
            if is_archive_encrypted:
                if encrypted_files_action == "skip":
                    return None
                if encrypted_files_action == "manually":
                    default_password = input(f"Enter [{path}] password: ")
                # try to open the archive using all standard passwords provided by the user
                if encrypted_files_action == "default":
                    for password in default_passwords:
                        try:
                            test_archive(path, -1, password=password)
                            # if no error was thrown, the password is suitable, you can save it and abort the checks
                            default_password = password
                            break
                        except PatoolError:
                            pass
                    # If all passwords were checked, but no suitable one was found,
                    # there is no point in trying to unpack the archive again - stop function execution
                    else:
                        return None
                # check if the archive is opened with the password specified by the user, if not, exit the function
                try:
                    test_archive(path, -1, password=default_password)
                except PatoolError:
                    return None

            # Handle the situation if the directory with the archive name already exists
            if isdir(archive_extract_dir):
                if verbosity_level > 0:
                    print("dir already exists " + archive_extract_dir)
                if result_directory_exists_action == "rename":
                    archive_extract_dir = get_result_extract_dir_renamed_path(archive_extract_dir)
                elif result_directory_exists_action == "overwrite":
                    rmdir(archive_extract_dir)
                else:
                    return None

            try:
                extract_archive(path, output_dir=archive_extract_dir, existing_action=result_directory_exists_action,
                                password=default_password if is_archive_encrypted else None, verbosity=verbosity_level)
                if remove_after_unpacking:
                    remove(path)

            # If the archive was not unpacked for any reason and the error was thrown,
            # delete the directory created for the archive (because it`s empty) and return 'None' from function
            except (PatoolError, RuntimeError) as e:
                if exists(archive_extract_dir):
                    rmdir(archive_extract_dir)
                if verbosity_level >= 0:
                    print(f"Cannot unzip file: {path}")
                    print(e)
                return None

            # start searching for archives in the folder with the elements of the just unpacked archive
            unpack_recursive(archive_extract_dir, encrypted_files_action, default_passwords, remove_after_unpacking,
                             result_directory_exists_action, verbosity_level)

            return archive_extract_dir

    except FileNotFoundError as e:
        if verbosity_level >= 0:
            print(e)


# If the project is installed as a module, only the 'unpack_recursive' function is available for external use.
__all__ = [unpack_recursive]

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-paths", type=str, help="Paths to files or folders to unzip (at least one)",
                        nargs="+")
    parser.add_argument("-r", "--remove", help="remove archives after unpacking", action="store_true", default=False)
    parser.add_argument("-pa", "--password-protected-action", type=str, default="skip",
                        choices=["skip", "default", "manually"],
                        help="What to do with password-encrypted files: skip, try to use one password provided by user"
                             " or write password manually for any encrypted file (default - 'skip')")
    parser.add_argument("-pwds", "--default-passwords", type=str, default=None, metavar="DEFAULT PASSWORD",
                        help="list of default passwords for encrypted archives"
                             "(if password-protected action set as 'default)", nargs="*", action="store")
    parser.add_argument("-e", "--existing-directory-action", type=str,
                        choices=["rename", "overwrite", "skip"], default="rename",
                        help="Action, if destination directory after unpacking already exists (default - 'rename')")
    parser.add_argument("-l", "--log-level", type=int, choices=[-1, 0, 1], default=0,
                        help="Logging level: -1 - completely absent, 0 - only errors, "
                             "1 - all important information (default - 0)", )
    args = parser.parse_args()

    for start_path in args.input_paths:
        if not (isdir(start_path) or is_archive(start_path)):
            raise Exception("Input path must be a folder or an archive, but got: " + start_path)

        result_dir = unpack_recursive(start_path, remove_after_unpacking=args.remove,
                                      default_passwords=args.default_passwords, verbosity_level=args.log_level,
                                      encrypted_files_action=args.password_protected_action,
                                      result_directory_exists_action=args.existing_directory_action)
        if args.log_level > 0:
            if not result_dir:
                print(f"Unpacking of [{start_path} failed")
                continue
            if isdir(start_path):
                print(f"All archives in folder [{start_path}] unpacked")
            else:
                print(f"Archive [{start_path} unpacked into directory {result_dir}")