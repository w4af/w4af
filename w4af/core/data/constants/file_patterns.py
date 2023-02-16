"""
file_patterns.py

Copyright 2006 Andres Riancho

This file is part of w4af, https://w4af.net/ .

w4af is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation version 2 of the License.

w4af is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with w4af; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

"""

FILE_PATTERNS = (
        b"root:x:0:0:",
        b"daemon:x:1:1:",
        b":/bin/bash",
        b":/bin/sh",

        # /etc/passwd in AIX
        b"root:!:x:0:0:",
        b"daemon:!:x:1:1:",
        b":usr/bin/ksh",

        # boot.ini
        b"[boot loader]",
        b"default=multi(",
        b"[operating systems]",

        # win.ini
        b"[fonts]",

        # PHP script
        b"<?php",

        # Executable script"
        b"#!/",
    )
