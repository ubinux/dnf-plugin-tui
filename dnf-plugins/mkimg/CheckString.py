#
# Copyright (C) Fujitsu Limited 2018 All rights reserved
#

import string

#-----------------------------------------------------------
# def CheckString()
#
#   Check characters in string
#
# Input:
#   sValue : string
# Output:
#   int    : 0 = success, -1 = fail
#-----------------------------------------------------------
def CheckString(sValue):
    tmp = sValue

    # No input
    if len(tmp) == 0:
        return -1

    # Number typ Check
    typ = CheckDigitHex(tmp)
    tmp = tmp.lower()

    # digit check
    if typ == 10:
        # check character exist (!kb,mb,k,m,b)
        chara = Check10Chara(tmp)
        if chara != 0:
            return -1

        # size check
        pos = len(tmp)
        if tmp[-1:] == "k" or tmp[-1:] == "m":
            pos = -1

        if int(tmp[:pos], 10) == 0:
            return -1

    # hex digit check
    if typ == 16:
        # check character exist (!a-f)
        chara = Check16Chara(tmp)
        if chara != 0:
            return -1

        # size check
        if int(tmp, 16) == 0:
            return -1

    return 0


#-----------------------------------------------------------
# def Check10Chara()
#
#   Check characters other than the decimal number
#
# Input:
#   sValue : string
# Output:
#   int    : 0 = success, -1 = fail
#-----------------------------------------------------------
def Check10Chara(sValue):
    rcode = 0

    pos = len(sValue)
    if sValue[-1:] == "k" or sValue[-1:] == "m":
        pos = -1

    #if sValue include srting
    if not sValue[:pos].isdigit():
        rcode = -1

    return rcode


#-----------------------------------------------------------
# def Check16Chara()
#
#   Check characters other than the hexadecimal number
#
# Input:
#   sValue : string
# Output:
#   int    : 0 = success, -1 = fail
#-----------------------------------------------------------
def Check16Chara(sValue):
    rcode = 0

    try:
        int(sValue, 16)
    except:
        rcode = -1

    return rcode


#-----------------------------------------------------------
# def CheckDigitHex()
#
#   Check string which is decimal or hexadecimal number
#
# Input:
#   sValue : string
# Output:
#   int    : 10: decimal, 16: hexadecimal
#-----------------------------------------------------------
def CheckDigitHex(sValue):
    rcode = 10

    if len(sValue) > 2:
      if sValue[:2] == "0x" or sValue[:2] == "0X":
        rcode = 16

    return rcode
