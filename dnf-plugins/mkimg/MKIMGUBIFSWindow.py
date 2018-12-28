#
# Copyright (C) Fujitsu Limited 2018 All rights reserved
#

import os
from ..window import *
from .ExecAndOutLog import *
from .OpenLogFile import *

#------------------------------------------------------------
# def MKIMGSetupUBIFSWindow()
#
#   Display UBIFS Setup Window.
#
# Input:
#    insScreen    : instance of snack screen
#    szFromdir    : Path of From-directory
#    szTodir      : Path of To-directory
#    szMinSize    : Minimum I/O unit size
#    szLeb        : Logical erase block size
#    szMeb        : Maximum logical erase block count
# Output:
#    str : pressed button ("n" : OK, "b" : Back, "e" : Exit)
#    str : fromdir
#    str : todir
#    str : blksize
#    str : leb
#    str : meb
#------------------------------------------------------------
def MKIMGSetupUBIFSWindow(insScreen, szFromdir=".rootfs-x86", szTodir="rootfs.ubifs.bin", \
                        szMinSize='512', szLeb='131072', szMeb='3000'):

    TAG_SRC_DIR     = "From directory  : "
    TAG_TARGET_DIR  = "To directory    : "
    TAG_MINSIZE     = "Minimum I/O unit size             : "
    TAG_LEB         = "Logical erase block size          : "
    TAG_MEB         = "Maximum logical erase block count : "

    # Create Button instance
    buttons = (("OK", "ok"), ("Back", "back"))
    bb = snack.ButtonBar(insScreen, buttons)

    # Create Grid instance
    g = snack.GridForm(insScreen, "UBIFS Parameter", 1, 7)

    #init snack.Grid object dict
    sg = {}
    for i in range(0, 5):
        sg[i] = snack.Grid(3, 1)

    # source directory
    sg[0].setField(snack.Textbox(19, 1, TAG_SRC_DIR), \
                        0, 0, (2, 0, 0, 0))
    txt_fromdir = snack.Entry(32, szFromdir, scroll = 1)
    sg[0].setField(txt_fromdir, 1, 0, (0, 0, 0, 0))
    sg[0].setField(snack.Textbox(5, 1, ""), 2, 0, (0, 0, 0, 0))

    # target directory
    sg[1].setField(snack.Textbox(19, 1, TAG_TARGET_DIR), \
                        0, 0, (2, 0, 0, 0))
    txt_todir = snack.Entry(32, szTodir, scroll = 1)
    sg[1].setField(txt_todir, 1, 0, (0, 0, 0, 0))
    sg[1].setField(snack.Textbox(5, 1, ""), 2, 0, (0, 0, 0, 0))

    #  Minimam Block Size
    sg[2].setField(snack.Textbox(36, 1, TAG_MINSIZE), \
                        0, 0, (2, 0, 0, 0))
    txt_blksize = snack.Entry(15, szMinSize, scroll = 0)
    sg[2].setField(txt_blksize, 1, 0, (0, 0, 0, 0))
    sg[2].setField(snack.Textbox(5, 1, "bytes"), 2, 0, (0, 0, 0, 0))

    # Logical Erase Block
    sg[3].setField(snack.Textbox(36, 1, TAG_LEB), \
                        0, 0, (2, 0, 0, 0))
    txt_leb = snack.Entry(15, szLeb, scroll = 0)
    sg[3].setField(txt_leb, 1, 0, (0, 0, 0, 0))
    sg[3].setField(snack.Textbox(5, 1, "bytes"), 2, 0, (0, 0, 0, 0))

    # Maximam Erase Block
    sg[4].setField(snack.Textbox(36, 1, TAG_MEB), \
                        0, 0, (2, 0, 0, 0))
    txt_meb = snack.Entry(15, szMeb, scroll = 0)
    sg[4].setField(txt_meb, 1, 0, (0, 0, 0, 0))
    sg[4].setField(snack.Textbox(5, 1, "count"), 2, 0, (0, 0, 0, 0))

    for i in range(0, 5):
        g.add(sg[i], 0, i, (0, 0, 0, 0))

    #Add buttons
    g.add(bb, 0, 6, (0, 1, 0, -1))

    # Display window
    while True:
        result = bb.buttonPressed(g.run())

        if result == "ok":
            rcode = "n"
            break
        elif result == "back":
            rcode = "b"
            break

    # set From Directory
    fromdir = txt_fromdir.value()
    fromdir = fromdir.strip()

    # set To Directory
    todir = txt_todir.value()
    todir = todir.strip()

    # set block size
    blksize = txt_blksize.value()
    blksize = blksize.strip()

    # set logical block size
    leb = txt_leb.value()
    leb = leb.strip()

    # set maximam block size
    meb = txt_meb.value()
    meb = meb.strip()

    insScreen.popWindow()
    return (rcode, fromdir, todir, blksize, leb, meb)


#------------------------------------------------------------
# def MKIMGUBIFSWindowCtrl()
#
#   WindowCtrl for making UBIFS image.
#
# Input:
#    insScreen    : instance of snack screen
# Output:
#    str : pressed button ("n" : OK, "b" : Back)
#------------------------------------------------------------
def MKIMGUBIFSWindowCtrl(insScreen):

    First_time = True
    while True:
        # Check if MKIMGSetupUBIFSWindow is first time to be called
        if First_time:
            (rcode, fromdir, todir, blksize, leb, meb) = MKIMGSetupUBIFSWindow(insScreen)
            First_time = False
        else:
            (rcode, fromdir, todir, blksize, leb, meb) = MKIMGSetupUBIFSWindow(insScreen, fromdir, todir, blksize, leb, meb)

        if rcode == "b":
            # back
            return rcode

        elif rcode == "n":
            # Call Confirm Function
            rcode = MKIMGConfirmUBIFSWindow(insScreen, fromdir, todir, blksize, leb, meb)

            if rcode == "b":
                continue

            elif rcode == "e":
                # exit
                exit_hkey = HotkeyExitWindow(insScreen)
                if exit_hkey == "y":
                    if insScreen != None:
                        StopHotkeyScreen(insScreen)
                        insScreen = None
                        sys.exit(0)

            else:
                # Log File Open
                imgfile = os.path.split(todir)[1]
                logfile = imgfile + ".log"
                try:
                    fdLog = OpenLogFile(logfile)
                    if insScreen != None:
                        StopHotkeyScreen(insScreen)
                        insScreen = None

                    MKIMGCreateUBIFS(fromdir, todir, blksize, leb, meb, fdLog)
                    sys.exit(0)

                finally:
                    # Log File Close
                    fdLog.close()
                    sys.exit(0)
                break

    return rcode

#------------------------------------------------------------
# def MKIMGConfirmUBIFSWindow()
#
#   Display Confirm Window before making image.
#
# Input:
#    insScreen    : instance of snack screen
#    szFromdir    : Path of From-directory
#    szTodir      : Path of To-directory
#    blksize      : Minimum I/O unit size
#    leb          : Logical erase block size
#    meb          : Maximum logical erase block count
# Output:
#    str : pressed button ("n" : OK, "b" : Back, "e" : Exit)
#------------------------------------------------------------
def MKIMGConfirmUBIFSWindow(insScreen, szFromdir, szTodir,  \
                          blksize, leb, meb):

    TAG_FROM_DIR    = "From directory:"
    TAG_TO_DIR      = "To directory:"
    TAG_IMG_TYP     = "Image type      : "
    TAG_IMG_FILE    = "Image file name                   : "
    TAG_BLK_SIZE    = "Minimum I/O unit size             : "
    TAG_LEB         = "Logical erase block size          : "
    TAG_MEB         = "Maximum logical erase block count : "
    TAG_INDENT_SPACE= "                                    "

    szTodir, szImgfile = os.path.split(szTodir)
    #Change relative path to absolute path
    if not szFromdir.startswith("/"):
        szFromdir = os.getcwd() + '/' +szFromdir
    if not szTodir.startswith("/"):
       szTodir = os.getcwd() + szTodir

    # Create Main Text
    (main_width, main_height) = GetButtonMainSize(insScreen)

    wrapper = textwrap.TextWrapper(width = main_width - 2)

    wrapper.initial_indent    = "  "
    wrapper.subsequent_indent = "  "

    lst_text = []

    lst_text.append("Are you sure to start making filesystem image ?\n\n")

    lst_text.append(TAG_FROM_DIR + "\n")
    lst_text.append(wrapper.fill(szFromdir) + "\n\n")

    lst_text.append(TAG_TO_DIR + "\n")
    lst_text.append(wrapper.fill(szTodir) + "\n\n")

    lst_text.append(TAG_IMG_TYP + "UBIFS\n")

    wrapper.initial_indent    = TAG_IMG_FILE
    wrapper.subsequent_indent = TAG_INDENT_SPACE
    lst_text.append(wrapper.fill(szImgfile) + "\n")

    lst_text.append(TAG_BLK_SIZE + blksize + " bytes\n")

    lst_text.append(TAG_LEB + leb + " bytes\n")

    lst_text.append(TAG_MEB + meb + " count\n")

    # List To Text
    main_text = "".join(lst_text)
    del lst_text

    # Create Button list
    buttons = ["OK", "Back", "Exit"]

    rcode = ButtonInfoWindow(insScreen, "Ready ?", main_text, \
                              main_width, main_height, buttons)

    return rcode

#-----------------------------------------------------------
# def MKIMGCreateUBIFS()
#
#   Create UBIFS image.
#
# Input:
#    fromdir      : Path of From-directory
#    imgpath      : Path of image file
#    lImgsize     : Image size (long)
#    blksize      : Minimum I/O unit size
#    leb          : Logical erase block size
#    meb          : Maximum logical erase block count
#    fdLog        : File Description of log
# Output:
#    bool         : success=True, fail=False
#-----------------------------------------------------------
def MKIMGCreateUBIFS(fromdir, imgpath, blksize, leb, meb, fdLog):

    MSG_START        = "Making the UBIFS image start."
    MSG_END_SUCCESS  = "\nMaking the UBIFS image succeeded."
    MSG_END_FAILED   = "\nMaking the UBIFS image failed."
    MSG_FINISH       = "RootFS Image Maker finish."
    ERR_MSG_CREATE_SIZE = "WARNING: The image file size is larger than the specified size !!"

    print(MSG_START)
    fdLog.write(MSG_START + "\n")

    rcode = True

    # Execute Commands
    cmd = "mkfs.ubifs -m %s -e %s -c %s -r %s %s " % \
             (blksize, leb, meb, fromdir, imgpath)
    if ExecAndOutLog(cmd, fdLog) != 0:
        rcode = False

    if rcode == True:
        os.chmod(imgpath, 0o644)
        print(MSG_END_SUCCESS)
        fdLog.write(MSG_END_SUCCESS + "\n")
    else:
        print(MSG_END_FAILED)
        fdLog.write(MSG_END_FAILED + "\n")

    print(MSG_FINISH)
    fdLog.write(MSG_FINISH + "\n")

    if rcode == True:
        rcode = 0
    else:
        rcode = -1

    return rcode
