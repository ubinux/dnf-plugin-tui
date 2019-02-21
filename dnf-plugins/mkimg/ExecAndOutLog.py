#
# Copyright (C) Fujitsu Limited 2018  All rights reserved
#

import sys, subprocess

#-----------------------------------------------------------
# def ExecAndOutLog()
#
#   Execuiting command and write out err-log.
#
# Input:
#   sCmd   : command string
#   fdLog  : file descriptor of Log file
# Output:
#   int    : return code for executing command
#-----------------------------------------------------------
def ExecAndOutLog(sCmd, fdLog):
    # Execute Command
    output = subprocess.getstatusoutput(sCmd)

    # Display and Write out Standard-Error, log file
    sys.stdout.write(output[1])
    fdLog.write(output[1])

    return output[0]

