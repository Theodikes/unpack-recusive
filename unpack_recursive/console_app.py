from .__init__ import unpack_recursive, is_archive
from os.path import isdir


def main():
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


if __name__ == "__main__":
    main()
