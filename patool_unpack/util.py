# -*- coding: utf-8 -*-
# Copyright (C) 2010-2016 Bastian Kleineidam
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Utility functions."""
from __future__ import print_function
import os
import sys
import subprocess
import mimetypes
import tempfile
from . import ArchiveMimetypes, ArchiveCompressions, program_supports_compression
try:
    from shutil import which
except ImportError:
    # from Python 3.3
    def which(cmd, mode=os.F_OK | os.X_OK, path=None):
        """Given a command, mode, and a PATH string, return the path which
        conforms to the given mode on the PATH, or None if there is no such
        file.
        `mode` defaults to os.F_OK | os.X_OK. `path` defaults to the result
        of os.environ.get("PATH"), or can be overridden with a custom search
        path.
        """
        def _access_check(fn, mode):
            """Check that a given file can be accessed with the correct mode.
            Additionally check that `fn` is not a directory, as on Windows
            directories pass the os.access check."""
            return (os.path.exists(fn) and os.access(fn, mode)
                    and not os.path.isdir(fn))
        # If we're given a path with a directory part, look it up directly rather
        # than referring to PATH directories. This includes checking relative to the
        # current directory, e.g. ./script
        if os.path.dirname(cmd):
            if _access_check(cmd, mode):
                return cmd
            return None
        path = (path or os.environ.get("PATH", os.defpath)).split(os.pathsep)
        if sys.platform == "win32":
            # The current directory takes precedence on Windows.
            if os.curdir not in path:
                path.insert(0, os.curdir)
            # PATHEXT is necessary to check on Windows.
            pathext = os.environ.get("PATHEXT", "").split(os.pathsep)
            # See if the given file matches any of the expected path extensions.
            # This will allow us to short circuit when given "python.exe".
            # If it does match, only test that one, otherwise we have to try
            # others.
            if any(cmd.lower().endswith(ext.lower()) for ext in pathext):
                files = [cmd]
            else:
                files = [cmd + ext for ext in pathext]
        else:
            # On other platforms you don't have things like PATHEXT to tell you
            # what file suffixes are executable, so just pass on cmd as-is.
            files = [cmd]
        seen = set()
        for dir in path:
            normdir = os.path.normcase(dir)
            if normdir not in seen:
                seen.add(normdir)
                for thefile in files:
                    name = os.path.join(dir, thefile)
                    if _access_check(name, mode):
                        return name
        return None


def system_search_path():
    """Get the list of directories on a system to search for executable programs.
    It is either the PATH environment variable or if PATH is undefined the value
    of os.defpath.
    """
    return os.environ.get("PATH", os.defpath)


# internal MIME database
mimedb = None


def init_mimedb():
    """Initialize the internal MIME database."""
    global mimedb
    try:
        mimedb = mimetypes.MimeTypes(strict=False)
    except Exception as msg:
        log_error("could not initialize MIME database: %s" % msg)
        return
    add_mimedb_data(mimedb)


def add_mimedb_data(mimedb):
    """Add missing encodings and mimetypes to MIME database."""
    mimedb.encodings_map['.bz2'] = 'bzip2'
    mimedb.encodings_map['.lzma'] = 'lzma'
    mimedb.encodings_map['.xz'] = 'xz'
    mimedb.encodings_map['.lz'] = 'lzip'
    mimedb.suffix_map['.tbz2'] = '.tar.bz2'
    add_mimetype(mimedb, 'application/x-lzop', '.lzo')
    add_mimetype(mimedb, 'application/x-adf', '.adf')
    add_mimetype(mimedb, 'application/x-arj', '.arj')
    add_mimetype(mimedb, 'application/x-lzma', '.lzma')
    add_mimetype(mimedb, 'application/x-xz', '.xz')
    add_mimetype(mimedb, 'application/java-archive', '.jar')
    add_mimetype(mimedb, 'application/x-rar', '.rar')
    add_mimetype(mimedb, 'application/x-rar', '.cbr')
    add_mimetype(mimedb, 'application/x-7z-compressed', '.7z')
    add_mimetype(mimedb, 'application/x-7z-compressed', '.cb7')
    add_mimetype(mimedb, 'application/x-cab', '.cab')
    add_mimetype(mimedb, 'application/x-rpm', '.rpm')
    add_mimetype(mimedb, 'application/x-debian-package', '.deb')
    add_mimetype(mimedb, 'application/x-ace', '.ace')
    add_mimetype(mimedb, 'application/x-ace', '.cba')
    add_mimetype(mimedb, 'application/x-archive', '.a')
    add_mimetype(mimedb, 'application/x-alzip', '.alz')
    add_mimetype(mimedb, 'application/x-arc', '.arc')
    add_mimetype(mimedb, 'application/x-lrzip', '.lrz')
    add_mimetype(mimedb, 'application/x-lha', '.lha')
    add_mimetype(mimedb, 'application/x-lzh', '.lzh')
    add_mimetype(mimedb, 'application/x-rzip', '.rz')
    add_mimetype(mimedb, 'application/x-zoo', '.zoo')
    add_mimetype(mimedb, 'application/x-dms', '.dms')
    add_mimetype(mimedb, 'application/x-zip-compressed', '.crx')
    add_mimetype(mimedb, 'application/x-shar', '.shar')
    add_mimetype(mimedb, 'application/x-tar', '.cbt')
    add_mimetype(mimedb, 'application/x-vhd', '.vhd')
    add_mimetype(mimedb, 'audio/x-ape', '.ape')
    add_mimetype(mimedb, 'audio/x-shn', '.shn')
    add_mimetype(mimedb, 'audio/flac', '.flac')
    add_mimetype(mimedb, 'application/x-chm', '.chm')
    add_mimetype(mimedb, 'application/x-iso9660-image', '.iso')
    add_mimetype(mimedb, 'application/zip', '.cbz')
    add_mimetype(mimedb, 'application/zip', '.epub')
    add_mimetype(mimedb, 'application/zip', '.apk')
    add_mimetype(mimedb, 'application/zpaq', '.zpaq')


def add_mimetype(mimedb, mimetype, extension):
    """Add or replace a mimetype to be used with the given extension."""
    # If extension is already a common type, strict=True must be used.
    strict = extension in mimedb.types_map[True]
    mimedb.add_type(mimetype, extension, strict=strict)


class PatoolError (Exception):
    """Raised when errors occur."""
    pass


class memoized(object):
    """Decorator that caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned, and
    not re-evaluated."""

    def __init__(self, func):
        """Set func and init cache."""
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        """Try to find result for function arguments in local cache or
        execute the function and fill the cache with the result."""
        try:
            return self.cache[args]
        except KeyError:
            self.cache[args] = value = self.func(*args)
            return value
        except TypeError:
            # uncachable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.func(*args)

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__


def backtick(cmd, encoding='utf-8'):
    """Return decoded output from command."""
    data = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]
    return data.decode(encoding)


def run(cmd, verbosity=0, **kwargs):
    """Run command without error checking.
    @return: command return code"""
    # Note that shell_quote_nt() result is not suitable for copy-paste
    # (especially on Unix systems), but it looks nicer than shell_quote().
    if verbosity >= 0:
        log_info("running %s" % " ".join(map(shell_quote_nt, cmd)))
    if kwargs:
        if verbosity >= 0:
            log_info("    with %s" % ", ".join("%s=%s" % (k, shell_quote(str(v))) for k, v in kwargs.items()))
        if kwargs.get("shell"):
            # for shell calls the command must be a string
            cmd = " ".join(cmd)
    if verbosity < 0:
        res = subprocess.call(cmd, **kwargs, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    elif verbosity < 1:
        res = subprocess.call(cmd, **kwargs, stdout=subprocess.DEVNULL)
    else:
        res = subprocess.call(cmd, **kwargs)
    return res


def run_checked(cmd, ret_ok=(0,), **kwargs):
    """Run command and raise PatoolError on error."""
    return_code = run(cmd, **kwargs)
    if return_code not in ret_ok:
        msg = "Command `%s' returned non-zero exit status %d" % (cmd, return_code)
        raise PatoolError(msg)
    return return_code


@memoized
def guess_mime(filename):
    """Guess the MIME type of given filename using file(1) and if that
    fails by looking at the filename extension with the Python mimetypes
    module.

    The result of this function is cached.
    """
    mime, encoding = guess_mime_file(filename)
    if mime is None:
        mime, encoding = guess_mime_mimedb(filename)
    assert mime is not None or encoding is None
    return mime, encoding


Encoding2Mime = {
    'gzip': "application/gzip",
    'bzip2': "application/x-bzip2",
    'compress': "application/x-compress",
    'lzma': "application/x-lzma",
    'lzip': "application/x-lzip",
    'xz': "application/x-xz",
}
Mime2Encoding = dict([(_val, _key) for _key, _val in Encoding2Mime.items()])
# libmagic before version 5.14 identified .gz files as application/x-gzip
Mime2Encoding['application/x-gzip'] = 'gzip'


def guess_mime_mimedb(filename):
    """Guess MIME type from given filename.
    @return: tuple (mime, encoding)
    """
    mime, encoding = None, None
    if mimedb is not None:
        mime, encoding = mimedb.guess_type(filename, strict=False)
    if mime not in ArchiveMimetypes and encoding in ArchiveCompressions:
        # Files like 't.txt.gz' are recognized with encoding as format, and
        # an unsupported mime-type like 'text/plain'. Fix this.
        mime = Encoding2Mime[encoding]
        encoding = None
    return mime, encoding


def guess_mime_file(filename):
    """Determine MIME type of filename with file(1):
     (a) using `file --mime`
     (b) using `file` and look the result string
    @return: tuple (mime, encoding)
    """
    mime, encoding = None, None
    base, ext = os.path.splitext(filename)
    if ext.lower() in ('.alz',):
        # let mimedb recognize these extensions
        return mime, encoding
    if os.path.isfile(filename):
        file_prog = find_program("file")
        if file_prog:
            mime, encoding = guess_mime_file_mime(file_prog, filename)
            if mime is None:
                mime = guess_mime_file_text(file_prog, filename)
                encoding = None
    if mime in Mime2Encoding:
        # try to look inside compressed archives
        cmd = [file_prog, "--brief", "--mime", "--uncompress", filename]
        try:
            outparts = backtick(cmd).strip().split(";")
            mime2 = outparts[0].split(" ", 1)[0]
        except OSError:
            mime2 = None
        # Some file(1) implementations return an empty or unknown mime type
        # when the uncompressor program is not installed, other
        # implementation return the original file type.
        # The following detects both cases.
        if (mime2 in ('application/x-empty', 'application/octet-stream') or
                mime2 in Mime2Encoding or not mime2):
            # The uncompressor program file(1) uses is not installed
            # or is not able to uncompress.
            # Try to get mime information from the file extension.
            mime2, encoding2 = guess_mime_mimedb(filename)
            if mime2 in ArchiveMimetypes:
                mime = mime2
                encoding = encoding2
        elif mime2 in ArchiveMimetypes:
            mime = mime2
            encoding = get_file_mime_encoding(outparts)
    # Only return mime and encoding if the given mime can natively support the encoding.
    if program_supports_compression(ArchiveMimetypes.get(mime), encoding):
        return mime, encoding
    else:
        # If encoding is None, default back to `mime`.
        return Encoding2Mime.get(encoding, mime), None


def guess_mime_file_mime(file_prog, filename):
    """Determine MIME type of filename with file(1) and --mime option.
    @return: tuple (mime, encoding)
    """
    mime, encoding = None, None
    cmd = [file_prog, "--brief", "--mime-type", filename]
    try:
        mime = backtick(cmd).strip()
    except OSError:
        # ignore errors, as file(1) is only a fallback
        pass
    if mime not in ArchiveMimetypes:
        mime, encoding = None, None
    return mime, encoding


def get_file_mime_encoding(parts):
    """Get encoding value from splitted output of file --mime --uncompress."""
    for part in parts:
        for subpart in part.split(" "):
            if subpart.startswith("compressed-encoding="):
                mime = subpart.split("=")[1].strip()
                return Mime2Encoding.get(mime)
    return None


# Match file(1) output text to mime types
FileText2Mime = {
    "7-zip archive data": "application/x-7z-compressed",
    "ACE archive data": "application/x-ace",
    "Amiga DOS disk": "application/x-adf",
    "ARJ archive data": "application/x-arj",
    "bzip2 compressed data": "application/x-bzip2",
    "cpio archive": "application/x-cpio",
    "ASCII cpio archive": "application/x-cpio",
    "Debian binary package": "application/x-debian-package",
    "gzip compressed data": "application/x-gzip",
    "LZMA compressed data": "application/x-lzma",
    "LRZIP compressed data": "application/x-lrzip",
    "lzop compressed data": "application/x-lzop",
    "Microsoft Cabinet archive data": "application/vnd.ms-cab-compressed",
    "RAR archive data": "application/x-rar",
    "RPM ": "application/x-redhat-package-manager",
    "POSIX tar archive": "application/x-tar",
    "xz compressed data": "application/x-xz",
    "Zip archive data": "application/zip",
    "compress'd data": "application/x-compress",
    "lzip compressed data": "application/x-lzip",
    "rzip compressed data": "application/x-rzip",
    "current ar archive": "application/x-archive",
    "LHa ": "application/x-lha",
    "ARC archive data": "application/x-arc",
    "Zoo archive data": "application/x-zoo",
    "DMS archive data": "application/x-dms",
    "Monkey's Audio": "audio/x-ape",
    "FLAC audio bitstream data": "audio/flac",
    "MS Windows HtmlHelp Data": "application/x-chm",
    "ZPAQ stream": "application/zpaq",
}


def guess_mime_file_text(file_prog, filename):
    """Determine MIME type of filename with file(1)."""
    cmd = [file_prog, "--brief", filename]
    try:
        output = backtick(cmd).strip()
    except OSError:
        # ignore errors, as file(1) is only a fallback
        return None
    # match output against known strings
    for matcher, mime in FileText2Mime.items():
        if output.startswith(matcher) and mime in ArchiveMimetypes:
            return mime
    return None


def check_existing_filename(filename, only_files=True):
    """Ensure that given filename is a valid, existing file."""
    if not os.path.exists(filename):
        raise PatoolError("file `%s' was not found" % filename)
    if not os.access(filename, os.R_OK):
        raise PatoolError("file `%s' is not readable" % filename)
    if only_files and not os.path.isfile(filename):
        raise PatoolError("`%s' is not a file" % filename)


def set_mode(filename, flags):
    """Set mode flags for given filename if not already set."""
    try:
        mode = os.lstat(filename).st_mode
    except OSError:
        # ignore
        return
    if not (mode & flags):
        try:
            os.chmod(filename, flags | mode)
        except OSError as msg:
            log_error("could not set mode flags for `%s': %s" % (filename, msg))


def get_filesize(filename):
    """Return file size in Bytes, or -1 on error."""
    return os.path.getsize(filename)


def create_temporary_directory(dir=None):
    """Return a temporary directory for extraction."""
    return tempfile.mkdtemp(suffix='', prefix='Unpack_', dir=dir)


def shell_quote(value):
    """Quote all shell metacharacters in given string value with strong
    (i.e. single) quotes, handling the single quote especially."""
    if os.name == 'nt':
        return shell_quote_nt(value)
    return "'%s'" % value.replace("'", r"'\''")


def shell_quote_nt(value):
    """Quote argument for Windows system. Modeled after distutils
    _nt_quote_args() function."""
    if " " in value:
        return '"%s"' % value
    return value


def strip_file_extension(filename):
    """Return the basename without extension of given filename."""
    basename, _ = os.path.splitext(os.path.basename(filename))
    if basename.endswith(".tar"):
        basename, _ = os.path.splitext(basename)
    return basename


def get_single_outfile(directory, archive, extension=""):
    """Get output filename if archive is in a single file format like gzip."""
    outfile = os.path.join(directory, strip_file_extension(archive))
    if os.path.exists(outfile + extension):
        # prevent overwriting existing files
        i = 1
        newfile = "%s%d" % (outfile, i)
        while os.path.exists(newfile + extension):
            newfile = "%s%d" % (outfile, i)
            i += 1
        outfile = newfile
    return outfile + extension


def log_error(msg, out=sys.stderr):
    """Print error message to stderr (or any other given output)."""
    print("patool error:", msg, file=out)


def log_info(msg, out=sys.stdout):
    """Print info message to stdout (or any other given output)."""
    print("patool:", msg, file=out)


def p7zip_supports_rar():
    """Determine if the RAR codec is installed for 7z program."""
    if os.name == 'nt':
        # Assume RAR support is compiled into the binary.
        return True
    # the subdirectory and codec name
    codec_name = 'p7zip/Codecs/Rar29.so'
    # search canonical user library dirs
    for library_dir in ('/usr/lib', '/usr/local/lib', '/usr/lib64', '/usr/local/lib64', '/usr/lib/i386-linux-gnu',
                        '/usr/lib/x86_64-linux-gnu'):
        filename = os.path.join(library_dir, codec_name)
        if os.path.exists(filename):
            return True
    return False


@memoized
def find_program(program):
    """Look for program in environment PATH variable."""
    if os.name == 'nt':
        # Add some well-known archiver programs to the search path
        path = os.environ['PATH']
        path = append_to_path(path, get_nt_7z_dir())
        path = append_to_path(path, get_nt_mac_dir())
        path = append_to_path(path, get_nt_winrar_dir())
    else:
        # use default path
        path = None
    return which(program, path=path)


def append_to_path(path, directory):
    """Add a directory to the PATH environment variable, if it is a valid
    directory."""
    if not os.path.isdir(directory) or directory in path:
        return path
    if not path.endswith(os.pathsep):
        path += os.pathsep
    return path + directory


def get_nt_7z_dir():
    """Return 7-Zip directory from registry, or an empty string."""
    # Python 3.x renamed the _winreg module to winreg
    try:
        import _winreg as winreg
    except ImportError:
        import winreg
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\7-Zip")
        try:
            return winreg.QueryValueEx(key, "Path")[0]
        finally:
            winreg.CloseKey(key)
    except WindowsError:
        return ""


def get_nt_program_dir():
    """Return the Windows program files directory."""
    progvar = "%ProgramFiles%"
    return os.path.expandvars(progvar)


def get_nt_mac_dir():
    """Return Monkey Audio Compressor (MAC) directory."""
    return os.path.join(get_nt_program_dir(), "Monkey's Audio")


def get_nt_winrar_dir():
    """Return WinRAR directory."""
    return os.path.join(get_nt_program_dir(), "WinRAR")


init_mimedb()
