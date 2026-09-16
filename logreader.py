#!/usr/bin/env python3
# ---------------------------------------------------------------------
# Source File: logreader.py
# Create Date: 09/19/2026 09:15
# Last Updated: 09/19/2026 09:15
# Author: Neal T. Bailey <nealbailey@hotmail.com>
#
# ----------------------------------------------------------------------
# GNU GENERAL PUBLIC LICENSE
# ----------------------------------------------------------------------
# Version 2, June 1991 
# Copyright (C) 1989, 1991 Free Software Foundation, Inc.  
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
#
# Everyone is permitted to copy and distribute verbatim copies
# of this license document, but changing it is not allowed.
#
# https://www.gnu.org/licenses/gpl-2.0.html
#-----------------------------------------------------------------------
# Copyright (c) 2010-2015 Baileysoft Solutions
#-----------------------------------------------------------------------
import os

def read_log(path: str) -> str:
    """
    Read a configured log file and return its contents as a string.

    The file is read as UTF-8. Invalid UTF-8 bytes are replaced rather
    than causing the request to fail.
    """

    if not os.path.isfile(path):
        raise FileNotFoundError(path)

    with open(path, "r", encoding="utf-8", errors="replace") as logfile:
        return logfile.read()