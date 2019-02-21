#
# Copyright (C) Fujitsu Limited 2018  All rights reserved
#

import sys, os

#-----------------------------------------------------------
# def OpenLogFile()
#
#   Open Log file and return file descriptor
#
# Input:
#   sLogpath : path of Log file
# Output:
#   fd       : file descriptor of Log file
#-----------------------------------------------------------
def OpenLogFile(sLogpath):

    # Log file open
    try:
        fd = open(sLogpath, "w")
    except Exception as e:
        print("%s: Can not open log file: %s",sys.stderr %(sys.argv[0], sLogpath, e))
        fd = open("/dev/null", "w")

    return fd

