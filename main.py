from os import listdir, remove, rmdir
from os.path import isdir, isfile, splitext, basename, join, dirname, exists
from patool_renewed import get_archive_format, check_archive_format, test_archive, extract_archive
from patool_renewed.util import PatoolError
from typing import Optional


def is_encrypted(path_to_archive: str, verbosity_level: int = 0) -> bool:
    try:
        test_archive(path_to_archive, interactive=False, password='FakePwd', verbosity=verbosity_level)
        return False
    except PatoolError as e:
        if "no support for password" in str(e) or "password is not supported" in str(e):
            return False
        if verbosity_level >= 0:
            print(e)
        return True


def get_filename_from_path(path: str) -> str:
    return splitext(basename(path))[0]


def is_archive(file_path) -> bool:
    try:
        check_archive_format(*get_archive_format(file_path))
        return True
    except PatoolError:
        return False


def get_result_extract_dir_renamed_path(archive_extract_dir: str) -> str:
    dir_number = 1
    archive_extract_dir_renamed = archive_extract_dir + "_" + str(dir_number)
    while isdir(archive_extract_dir_renamed):
        dir_number += 1
        archive_extract_dir_renamed = archive_extract_dir + "_" + str(dir_number)

    return archive_extract_dir_renamed


def unpack_recursive(path: str, password: Optional[str] = None, encrypted_files_action: str = "skip",
                     remove_after_unpacking: bool = False, result_directory_exists_action: str = "rename",
                     verbosity_level: int = 0) -> None:

    if isdir(path):
        for sub_path in listdir(path):
            unpack_recursive(join(path, sub_path), password, encrypted_files_action, remove_after_unpacking,
                             result_directory_exists_action, verbosity_level)

    elif isfile(path) and is_archive(path):
        archive_directory: str = dirname(path)
        archive_filename_without_extension: str = get_filename_from_path(path)
        archive_extract_dir: str = join(archive_directory, archive_filename_without_extension)
        if isdir(archive_extract_dir):
            if verbosity_level > 0:
                print("dir exists " + archive_extract_dir)
            if result_directory_exists_action == "skip":
                return
            if result_directory_exists_action == "rename":
                archive_extract_dir = get_result_extract_dir_renamed_path(archive_extract_dir)

        try:
            is_archive_encrypted: bool = is_encrypted(path, verbosity_level)
            if is_archive_encrypted:
                if encrypted_files_action == "skip":
                    return
                if encrypted_files_action == "manually":
                    password = input(f"Enter [{path}] password: ")

            if result_directory_exists_action == "overwrite":
                rmdir(archive_extract_dir)

            extract_archive(path, output_dir=archive_extract_dir, password=password if is_archive_encrypted else None,
                            verbosity=verbosity_level)
            if remove_after_unpacking:
                remove(path)
        except (PatoolError, RuntimeError) as e:
            if exists(archive_extract_dir):
                rmdir(archive_extract_dir)
            if verbosity_level >= 0:
                print(f"\033[91mCannot unzip file: {path}\033[0m")
                print(f"\033[91m{e}\033[0m")
            return

        unpack_recursive(archive_extract_dir, password, encrypted_files_action, remove_after_unpacking,
                         result_directory_exists_action, verbosity_level)


__all__ = [unpack_recursive]

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=str, help="Path to file or folder to unzip")
    parser.add_argument("-r", "--remove", help="remove archives after unpacking", action="store_true", default=False)
    parser.add_argument("-pa", "--password-protected-action", type=str, default="skip",
                        choices=["skip", "default", "manually"],
                        help="What to do with password-encrypted files: skip, try to use one password provided by user"
                             " or write password manually for any encrypted file (default - 'skip')")
    parser.add_argument("-pwd", "--default-password", type=str, help="default password for encrypted archives",
                        default=None, metavar="DEFAULT PASSWORD")
    parser.add_argument("-e", "--existing-directory-action", type=str,
                        choices=["rename", "overwrite", "skip"], default="rename",
                        help="Action, if destination directory after unpacking already exists (default - 'rename')")
    parser.add_argument("-l", "--log-level", type=int, choices=[-1, 0, 1], default=0,
                        help="Logging level: -1 - completely absent, 0 - only errors, "
                             "1 - all important information (default - 0)", )
    args = parser.parse_args()

    start_path: str = args.path
    if not (isdir(start_path) or is_archive(start_path)):
        raise Exception("Input path must be a folder or an archive")

    unpack_recursive(start_path, remove_after_unpacking=args.remove, password=args.default_password,
                     verbosity_level=args.log_level, encrypted_files_action=args.password_protected_action,
                     result_directory_exists_action=args.existing_directory_action)
