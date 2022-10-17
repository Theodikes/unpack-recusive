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
from __future__ import print_function

import inspect
import sys
if not hasattr(sys, "version_info") or sys.version_info < (2, 7, 0, "final", 0):
    raise SystemExit("This program requires Python 2.7 or later.")
import os
import shutil
import stat
import importlib
# PEP 396
__all__ = ['extract_archive', 'test_archive',
           'program_supports_compression', 'get_archive_format', 'check_archive_format']


# Supported archive commands
ArchiveCommands = ('list', 'extract', 'test', 'create')

# Supported archive formats
ArchiveFormats = (
    '7z', 'ace', 'adf', 'alzip', 'ape', 'ar', 'arc', 'arj',
    'bzip2', 'cab', 'chm', 'compress', 'cpio', 'deb', 'dms',
    'flac', 'gzip', 'iso', 'lrzip', 'lzh', 'lzip', 'lzma', 'lzop',
    'rar', 'rpm', 'rzip', 'shar', 'shn', 'tar', 'vhd', 'xz',
    'zip', 'zoo', 'zpaq', 'wim')

# Supported compressions (used with tar for example)
# Note that all compressions must also be archive formats
ArchiveCompressions = ('bzip2', 'compress', 'gzip', 'lzip', 'lzma', 'xz')

# Map MIME types to archive format
ArchiveMimetypes = {
    'application/gzip': 'gzip',
    'application/jar': 'zip',  # reported on older systems such as ubuntu 14.04
    'application/java-archive': 'zip',
    'application/rar': 'rar',
    'application/vnd.ms-cab-compressed': 'cab',
    'application/x-7z-compressed': '7z',
    'application/x-ace': 'ace',
    'application/x-adf': 'adf',
    'application/x-alzip': 'alzip',
    'application/x-archive': 'ar',
    'application/x-arc': 'arc',
    'application/x-arj': 'arj',
    'application/x-bzip2': 'bzip2',
    'application/x-cab': 'cab',
    'application/x-chm': 'chm',
    'application/x-compress': 'compress',
    'application/x-cpio': 'cpio',
    'application/x-debian-package': 'deb',
    'application/x-dms': 'dms',
    'application/x-gzip': 'gzip',
    'application/x-iso9660-image': 'iso',
    'application/x-lzop': 'lzop',
    'application/x-lzma': 'lzma',
    'application/x-lzip': 'lzip',
    'application/x-lha': 'lzh',
    'application/x-lrzip': 'lrzip',
    'application/x-lzh': 'lzh',
    'application/x-rar': 'rar',
    'application/x-redhat-package-manager': 'rpm',
    'application/x-rpm': 'rpm',
    'application/x-rzip': 'rzip',
    'application/x-shar': 'shar',
    'application/x-tar': 'tar',
    'application/x-vhd': 'vhd',
    'application/x-ms-wim': 'wim',
    'application/x-xz': 'xz',
    'application/x-zip-compressed': 'zip',
    'application/x-zoo': 'zoo',
    'application/zip': 'zip',
    'application/zpaq': 'zpaq',
    'audio/x-ape': 'ape',
    'audio/x-shn': 'shn',
    'audio/flac': 'flac',
}

try:
    # use Python 3 lzma module if available
    import lzma
    py_lzma = ('py_lzma',)
except ImportError:
    py_lzma = ()

# List of programs supporting the given archive format and command.
# If command is None, the program supports all commands (list, extract, ...)
# Programs starting with "py_" are Python modules.
ArchivePrograms = {
    'ace': {
        'extract': ('unace',),
        'test': ('unace',),
        'list': ('unace',),
    },
    'adf': {
        'extract': ('unadf',),
        'test': ('unadf',),
        'list': ('unadf',),
    },
    'alzip': {
        'extract': ('unalz',),
        'test': ('unalz',),
        'list': ('unalz',),
    },
    'ape': {
        'create': ('mac',),
        'extract': ('mac',),
        'list': ('py_echo',),
        'test': ('mac',),
    },
    'ar': {
        None: ('ar',),
    },
    'arc': {
        None: ('arc',),
        'extract': ('nomarch',),
        'test': ('nomarch',),
        'list': ('nomarch',),
    },
    'bzip2': {
        None: ('7z', '7za'),
        'extract': ('pbzip2', 'lbzip2', 'bzip2', 'py_bz2'),
        'test': ('pbzip2', 'lbzip2', 'bzip2'),
        'create': ('pbzip2', 'lbzip2', 'bzip2', 'py_bz2'),
        'list': ('py_echo', ),
    },
    'cab': {
        'extract': ('cabextract', '7z'),
        'create': ('lcab',),
        'list': ('cabextract', '7z'),
        'test': ('cabextract', '7z'),
    },
    'chm': {
        'extract': ('archmage', 'extract_chmLib'),
        'test': ('archmage',),
    },
    'flac': {
        'extract': ('flac',),
        'test': ('flac',),
        'create': ('flac',),
        'list': ('py_echo',),
    },
    'tar': {
        None: ('7z', 'tar', 'star', 'bsdtar', 'py_tarfile'),
    },
    'zip': {
        None: ('7z', '7za', 'py_zipfile'),
        'extract': ('unzip',),
        'list': ('unzip',),
        'test': ('zip', 'unzip',),
        'create': ('zip',),
    },
    'gzip': {
        None: ('7z', '7za', 'pigz', 'gzip'),
        'extract': ('py_gzip',),
        'create': ('zopfli', 'py_gzip'),
    },
    'iso': {
        'extract': ('7z',),
        'list': ('7z', 'isoinfo'),
        'test': ('7z',),
        'create': ('genisoimage',),
    },
    'lzh': {
        None: ('lha',),
        'extract': ('lhasa',),
    },
    'lzip': {
        'extract': ('plzip', 'lzip', 'clzip', 'pdlzip'),
        'list': ('py_echo',),
        'test': ('plzip', 'lzip', 'clzip', 'pdlzip'),
        'create': ('plzip', 'lzip', 'clzip', 'pdlzip'),
    },
    'lrzip': {
        'extract': ('lrzip',),
        'list': ('py_echo',),
        'test': ('lrzip',),
        'create': ('lrzip',),
    },
    'compress': {
        'extract': ('gzip', '7z', '7za', 'uncompress.real'),
        'list': ('7z', '7za', 'py_echo',),
        'test': ('gzip', '7z', '7za'),
        'create': ('compress',),
    },
    '7z': {
        None: ('7z', '7za', '7zr'),
    },
    'rar': {
        None: ('rar',),
        'extract': ('unrar', '7z'),
        'list': ('unrar', '7z'),
        'test': ('unrar', '7z'),
    },
    'arj': {
        None: ('arj',),
        'extract': ('7z',),
        'list': ('7z',),
        'test': ('7z',),
    },
    'cpio': {
        'extract': ('cpio', 'bsdcpio', '7z'),
        'list': ('cpio', 'bsdcpio', '7z'),
        'test': ('cpio', 'bsdcpio', '7z',),
        'create': ('cpio', 'bsdcpio'),
    },
    'rpm': {
        'extract': ('rpm2cpio', '7z'),
        'list': ('rpm', '7z', '7za'),
        'test': ('rpm', '7z'),
    },
    'deb': {
        'extract': ('dpkg-deb', '7z'),
        'list': ('dpkg-deb', '7z'),
        'test': ('dpkg-deb', '7z'),
    },
    'dms': {
        'extract': ('xdms',),
        'list': ('xdms',),
        'test': ('xdms',),
    },
    'lzop': {
        None: ('lzop',),
    },
    'lzma': {
        'extract': ('7z', 'lzma', 'xz') + py_lzma,
        'list': ('7z', 'py_echo'),
        'test': ('7z', 'lzma', 'xz'),
        'create': ('lzma', 'xz') + py_lzma,
    },
    'rzip': {
        'extract': ('rzip',),
        'list': ('py_echo',),
        'create': ('rzip',),
    },
    'shar': {
        'create': ('shar',),
        'extract': ('unshar',),
    },
    'shn': {
        'extract': ('shorten',),
        'list': ('py_echo',),
        'create': ('shorten',),
    },
    'vhd': {
        'extract': ('7z',),
        'list': ('7z',),
        'test': ('7z',),
    },
    'wim': {
        None: ('7z',)
    },
    'xz': {
        None: ('xz', '7z'),
        'extract': py_lzma,
        'create': py_lzma,
    },
    'zoo': {
        None: ('zoo',)
    },
    'zpaq': {
        None: ('zpaq',)
    },
}

# List of programs by archive type, which don't support password use
NoPasswordSupportArchivePrograms = {
    'bzip2': {
        None: ('7z', )
    },
    'wim': {
        None: ('7z',)
    },
    'cab': {
        None: ('7z', )
    },
    'zip': {
        'create': ('py_zipfile', ),
    },
    'arj': {
        None: ('7z',)
        },
    'gzip': {
        None: ('7z',)
    },
    'iso': {
        None: ('7z',)
    },
    'cpio': {
        None: ('7z', )
    },
    'rpm': {
        None: ('7z', )
    },
    'deb': {
        None: ('7z', )
    },
    'lzma': {
        None: ('7z', )
    },
    'vhd': {
        None: ('7z', )
    },
    'xz': {
        None: ('7z',)
    },
}

# List those programs that have different python module names because of
# Python module naming restrictions.
ProgramModules = {
    '7z': 'p7zip',
    '7za': 'p7azip',
    '7zr': 'p7rzip',
    'uncompress.real': 'uncompress',
    'dpkg-deb': 'dpkg',
    'extract_chmlib': 'chmlib',
}


def program_supports_compression(program, compression):
    """Decide if the given program supports the compression natively.
    @return: True iff the program supports the given compression format
      natively, else False.
    """
    if program in ('tar', ):
        return compression in ('gzip', 'bzip2', 'xz', 'lzip', 'compress', 'lzma') + py_lzma
    elif program in ('star', 'bsdtar', 'py_tarfile'):
        return compression in ('gzip', 'bzip2') + py_lzma
    return False


from . import util


def get_archive_format(filename):
    """Detect filename archive format and optional compression."""
    mime, compression = util.guess_mime(filename)
    if not (mime or compression):
        raise util.PatoolError("unknown archive format for file `%s'" % filename)
    if mime in ArchiveMimetypes:
        archive_file_format = ArchiveMimetypes[mime]
    else:
        raise util.PatoolError("unknown archive format for file `%s' (mime-type is `%s')" % (filename, mime))
    if archive_file_format == compression:
        # file cannot be in same format compressed
        compression = None
    return archive_file_format, compression


def check_archive_format(format, compression):
    """Make sure format and compression is known."""
    if format not in ArchiveFormats:
        raise util.PatoolError("unknown archive format `%s'" % format)
    if compression is not None and compression not in ArchiveCompressions:
        raise util.PatoolError("unknown archive compression `%s'" % compression)


def find_archive_program(archive_file_format, command, program=None, password=None):
    """Find suitable archive program for given format and mode."""
    commands = ArchivePrograms[archive_file_format]
    programs = []
    if program is not None:
        # try a specific program first
        programs.append(program)
    # first try the universal programs with key None
    for key in (None, command):
        if key in commands:
            programs.extend(commands[key])
    if password is not None:
        programs = _remove_command_without_password_support(programs, archive_file_format, command)
    if not programs:
        raise util.PatoolError("%s archive format `%s' is not supported" % (command, archive_file_format))
    # return the first existing program
    for program in programs:
        if program.startswith('py_'):
            # it's a Python module and therefore always supported
            return program
        exe = util.find_program(program)
        if exe:
            if program == '7z' and archive_file_format == 'rar' and not util.p7zip_supports_rar():
                continue
            return exe
    # no programs found
    raise util.PatoolError("could not find an executable program to %s format %s; candidates are (%s),"
                           % (command, archive_file_format, ",".join(programs)))


def _remove_command_without_password_support(programs, format, command):
    """Remove programs if they don't support work with password for current
    format and command."""
    if format not in NoPasswordSupportArchivePrograms:
        return programs
    no_password_support_commands = NoPasswordSupportArchivePrograms[format]
    no_password_support_programs = set()
    for key in (None, command):
        if key in no_password_support_commands:
            for program in no_password_support_commands[key]:
                no_password_support_programs.add(program)
    programs_with_support = []
    for program in programs:
        if program not in no_password_support_programs:
            programs_with_support.append(program)
    if not programs_with_support and programs:
        raise util.PatoolError("%s archive format `%s' with password is not supported" % (command, format))
    return programs_with_support


def check_program_compression(archive, command, program, compression):
    """Check if a program supports the given compression."""
    program = os.path.basename(program)
    if compression:
        # check if compression is supported
        if not program_supports_compression(program, compression):
            if command == 'create':
                comp_command = command
            else:
                comp_command = 'extract'
            comp_prog = find_archive_program(compression, comp_command)
            if not comp_prog:
                msg = "cannot %s archive `%s': compression `%s' not supported"
                raise util.PatoolError(msg % (command, archive, compression))


def move_output_dir_orphan(output_dir):
    """Move a single file or directory inside output_dir a level up.
    Never overwrite files.
    Return (True, outfile) if successful, (False, reason) if not."""
    entries = os.listdir(output_dir)
    if len(entries) == 1:
        src = os.path.join(output_dir, entries[0])
        dst = os.path.join(os.path.dirname(output_dir), entries[0])
        if os.path.exists(dst) or os.path.islink(dst):
            return False, "local file exists"
        shutil.move(src, dst)
        os.rmdir(output_dir)
        return True, entries[0]
    return False, "multiple files in root"


def run_archive_cmdlist(archive_cmdlist, verbosity=0):
    """Run archive command."""
    # archive_cmdlist is a command list with optional keyword arguments
    if isinstance(archive_cmdlist, tuple):
        cmdlist, run_kwargs = archive_cmdlist
    else:
        cmdlist, run_kwargs = archive_cmdlist, {}
    return util.run_checked(cmdlist, verbosity=verbosity, **run_kwargs)


def make_file_readable(filename):
    """Make file user readable if it is not a link."""
    if not os.path.islink(filename):
        util.set_mode(filename, stat.S_IRUSR)


def make_dir_readable(filename):
    """Make directory user readable and executable."""
    util.set_mode(filename, stat.S_IRUSR | stat.S_IXUSR)


def make_user_readable(directory):
    """Make all files in given directory user readable. Also recurse into
    subdirectories."""
    for root, dirs, files in os.walk(directory, onerror=util.log_error):
        for filename in files:
            make_file_readable(os.path.join(root, filename))
        for dirname in dirs:
            make_dir_readable(os.path.join(root, dirname))


def cleanup_output_dir(output_dir, archive):
    """Cleanup output_dir after extraction and return target file name and
    result string."""
    make_user_readable(output_dir)
    # move single directory or file in output_dir
    (success, msg) = move_output_dir_orphan(output_dir)
    if success:
        # msg is a single directory or filename
        return msg, "`%s'" % msg
    # output_dir remains unchanged
    # rename it to something more user-friendly (basically the archive
    # name without extension)
    output_dir2 = util.get_single_outfile("", archive)
    os.rename(output_dir, output_dir2)
    return output_dir2, "`%s' (%s)" % (output_dir2, msg)


def _extract_archive(archive, verbosity=0, interactive=True, output_dir=None,
                     program=None, format=None, compression=None, password=None):
    """Extract an archive.
    @return: output directory if command is 'extract', else None
    """
    if format is None:
        format, compression = get_archive_format(archive)
    check_archive_format(format, compression)
    program = find_archive_program(format, 'extract', program=program, password=password)
    check_program_compression(archive, 'extract', program, compression)
    get_archive_cmdlist = get_archive_cmdlist_func(program, 'extract', format)
    if output_dir is None:
        output_dir = util.create_temporary_directory(dir=".")
        do_cleanup_output_dir = True
    else:
        do_cleanup_output_dir = False
    try:
        cmdlist = get_archive_cmdlist(archive, compression, program, verbosity, interactive, output_dir,
                                      password=password)
        if cmdlist:
            # an empty command list means the get_archive_cmdlist() function
            # already handled the command (e.g. when it's a builtin Python
            # function)
            run_archive_cmdlist(cmdlist, verbosity=verbosity)
        if do_cleanup_output_dir:
            target, msg = cleanup_output_dir(output_dir, archive)
        else:
            target, msg = output_dir, "`%s'" % output_dir
        if verbosity >= 0:
            util.log_info("... %s extracted to %s." % (archive, msg))
        return target
    finally:
        # try to remove an empty temporary output directory
        if do_cleanup_output_dir:
            try:
                os.rmdir(output_dir)
            except OSError:
                pass


def _handle_archive(archive, command, verbosity=0, interactive=True,
                    program=None, archive_file_format=None, compression=None, password=None):
    """Test and list archives."""
    if archive_file_format is None:
        archive_file_format, compression = get_archive_format(archive)
    check_archive_format(archive_file_format, compression)
    if command not in ('list', 'test'):
        raise util.PatoolError("invalid archive command `%s'" % command)
    program = find_archive_program(archive_file_format, command, program=program, password=password)
    check_program_compression(archive, command, program, compression)
    get_archive_cmdlist = get_archive_cmdlist_func(program, command, archive_file_format)
    # prepare keyword arguments for command list
    cmdlist = get_archive_cmdlist(archive, compression, program, verbosity, interactive, password=password)
    if cmdlist:
        # an empty command list means the get_archive_cmdlist() function
        # already handled the command (e.g. when it's a builtin Python
        # function)
        run_archive_cmdlist(cmdlist, verbosity=verbosity)


def get_archive_cmdlist_func(program, command, archive_file_format):
    """Get the Python function that executes the given program."""
    # get python module for given archive program
    key = util.strip_file_extension(os.path.basename(program).lower())
    modulename = ".programs." + ProgramModules.get(key, key)
    # import the module
    try:
        module = importlib.import_module(modulename, __name__)
    except ImportError as msg:
        raise util.PatoolError(msg)
    # get archive handler function (e.g. patoolib.programs.star.extract_tar)
    try:
        archive_cmdlist_func = getattr(module, '%s_%s' % (command, archive_file_format))

        def check_for_password_before_cmdlist_func_call(*args, **kwargs):
            """ If password is None, or not set, run command as usual.
            If password is set, but can't be accepted raise appropriate
            message.
            """
            if 'password' in kwargs and kwargs['password'] is None:
                kwargs.pop('password')
            if 'password' not in kwargs:
                return archive_cmdlist_func(*args, **kwargs)
            else:
                if 'password' in inspect.signature(archive_cmdlist_func).parameters:
                    return archive_cmdlist_func(*args, **kwargs)
                raise util.PatoolError('There is no support for password in %s' % program)
        return check_for_password_before_cmdlist_func_call

    except AttributeError as msg:
        raise util.PatoolError(msg)


def rmtree_log_error(func, path, exc):
    """Error function for shutil.rmtree(). Raises a PatoolError."""
    msg = "Error in %s(%s): %s" % (func.__name__, path, str(exc[1]))
    util.log_error(msg)


def extract_archive(archive, verbosity=0, output_dir=None, program=None, interactive=True, password=None):
    """Extract given archive."""
    util.check_existing_filename(archive)
    if verbosity >= 0:
        util.log_info("Extracting %s ..." % archive)
    return _extract_archive(archive, verbosity=verbosity, interactive=interactive, output_dir=output_dir,
                            program=program, password=password)


def test_archive(archive, verbosity=0, program=None, interactive=True, password=None):
    """Test given archive."""
    util.check_existing_filename(archive)
    if verbosity >= 0:
        util.log_info("Testing %s ..." % archive)
    res = _handle_archive(archive, 'test', verbosity=verbosity, interactive=interactive,
                          program=program, password=password)
    if verbosity >= 0:
        util.log_info("... tested ok.")
    return res
