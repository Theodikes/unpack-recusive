# -*- coding: utf-8 -*-
# Copyright (C) 2010-2015 Bastian Kleineidam
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
"""Archive commands for the rzip program."""
from .. import util

def extract_rzip (archive, compression, cmd, verbosity, interactive, output_dir):
    """Extract an RZIP archive."""
    cmdlist = [cmd, '-d', '-k']
    if verbosity > 1:
        cmdlist.append('-v')
    outfile = util.get_single_outfile(output_dir, archive)
    cmdlist.extend(["-o", outfile, archive])
    return cmdlist

def create_rzip (archive, compression, cmd, verbosity, interactive, filenames):
    """Create an RZIP archive."""
    cmdlist = [cmd, '-k', '-9', '-o', archive]
    if verbosity > 1:
        cmdlist.append('-v')
    cmdlist.extend(filenames)
    return cmdlist