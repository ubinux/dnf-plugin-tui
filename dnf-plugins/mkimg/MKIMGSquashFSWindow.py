#
# Copyright (C) Fujitsu Limited 2018 All rights reserved
#

import os
from ..window import *
from .ExecAndOutLog import *
from .OpenLogFile import *
from .ButtonErrorWindow import *
from .MKIMGInfo import *

#------------------------------------------------------------
# def MKIMGSetupSquashFSWindow()
#
#   Display SquashFS Setup Window.
#
# Input:
#    insScreen    : instance of snack screen
#    szFromdir    : Path of From-directory
#    szTodir      : Path of To-directory
#    szBlksize    : Block size (string)
# Output:
#    str : pressed button ("n" : OK, "b" : Back, "e" : Exit)
#    str : fromdir
#    str : todir
#    str : Block size
#------------------------------------------------------------
def MKIMGSetupSquashFSWindow(insScreen, szFromdir=".rootfs-x86", szTodir="rootfs.SquashFS.bin", \
                        szBlksize="4096"):
    TAG_SRC_DIR     = "From directory  : "
    TAG_TARGET_DIR  = "To directory    : "
    TAG_BLOCK_SIZE  = "Block size"

    # Create Button instance
    buttons = (("OK", "ok"), ("Back", "back"))
    bb = snack.ButtonBar(insScreen, buttons)

    # Create Grid instance
    g = snack.GridForm(insScreen, "SquashFS Parameter", 1, 7)

    #init snack.Grid object dict
    sg = {}
    for i in range(0, 3):
        sg[i] = snack.Grid(3, 1)

    # source directory
    sg[0].setField(snack.Textbox(19, 1, TAG_SRC_DIR), \
                        0, 0, (2, 0, 0, 0))
    txt_fromdir = snack.Entry(29, szFromdir, scroll = 1)
    sg[0].setField(txt_fromdir, 1, 0, (0, 0, 0, 0))
    sg[0].setField(snack.Textbox(5, 1, ""), 2, 0, (0, 0, 0, 0))

    # target directory
    sg[1].setField(snack.Textbox(19, 1, TAG_TARGET_DIR), \
                        0, 0, (2, 0, 0, 0))
    txt_todir = snack.Entry(29, szTodir, scroll = 1)
    sg[1].setField(txt_todir, 1, 0, (0, 0, 0, 0))
    sg[1].setField(snack.Textbox(5, 1, ""), 2, 0, (0, 0, 0, 0))

    # Block size
    sg[2].setField(snack.Textbox(19, 1, TAG_BLOCK_SIZE), \
                        0, 0, (-12, 0, 0, 0))
    txt_blksize = snack.Entry(15, szBlksize, scroll = 0)
    sg[2].setField(txt_blksize, 1, 0, (0, 0, 0, 0))
    sg[2].setField(snack.Textbox(5, 1, "bytes"), 2, 0, (0, 0, 0, 0))

    for i in range(0, 3):
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

    # set Block size
    blksize = txt_blksize.value()
    blksize = blksize.strip()

    insScreen.popWindow()
    return (rcode, fromdir, todir, blksize)


#------------------------------------------------------------
# def MKIMGSquashFSWindowCtrl()
#
#   WindowCtrl for making SquashFS image.
#
# Input:
#    insScreen    : instance of snack screen
#    insMKIMGInfo : instance of class MKIMGInfo
# Output:
#    str : pressed button ("n" : OK, "b" : Back)
#------------------------------------------------------------
def MKIMGSquashFSWindowCtrl(insScreen, insMKIMGInfo):

    ERR_ITEM_BLOCK_SIZE  = "Block size"

    while True:
        # Get the default value for SquashFS
        (szimgsize, limgsize) = insMKIMGInfo.get_squashfs_param()

        szFromdir = insMKIMGInfo.get_from_dir_path()
        szTodir = insMKIMGInfo.get_to_dir_path()

        # Completion the Todir if image_file_name exists
        if insMKIMGInfo.get_image_file_name():
           szTodir = szTodir + "/" + insMKIMGInfo.get_image_file_name()

        (rcode, szFromdir, szTodir, szimgsize) = \
            MKIMGSetupSquashFSWindow(insScreen, szFromdir, szTodir, szimgsize)

        #Change relative path to absolute path
        szFromdir = os.path.abspath(szFromdir);
        szTodir = os.path.abspath(szTodir);

        insMKIMGInfo.set_squashfs_param(szimgsize)
        insMKIMGInfo.set_from_dir_path(szFromdir)
        insMKIMGInfo.set_to_dir_path(szTodir)

        # Check input params
        if rcode == "n":
            (err, err_str) = insMKIMGInfo.check_from_dir_path()
            if err != 0:
                item = err_str
                ButtonErrorWindow(insScreen, item)
                continue

            err = insMKIMGInfo.check_squashfs_param()
            if err != 0:
                item = ""
                if err == MKIMG_LABEL_BLK_SIZE:
                    item = ERR_ITEM_BLOCK_SIZE

                ButtonErrorWindow(insScreen, item)
                continue

            else:
                # transfer string to long int
                insMKIMGInfo.set_squashfs_long_param()
                break;

        if rcode == "b":
            # back
            return rcode

#------------------------------------------------------------
# def MKIMGConfirmSquashFSWindow()
#
#   Display Confirm Window before making image.
#
# Input:
#    insScreen    : instance of snack screen
#    szFromdir    : Path of From-directory
#    szTodir      : Path of To-directory
#    szImgfile    : Name of Imgfile
#    lblksize     : Block size(long)
# Output:
#    str : pressed button ("n" : OK, "b" : Back, "e" : Exit)
#------------------------------------------------------------
def MKIMGConfirmSquashFSWindow(insScreen, szFromdir, szTodir, szImgfile, lblksize):

    TAG_FROM_DIR    = "From directory:"
    TAG_TO_DIR      = "To directory:"
    TAG_IMG_TYP     = "Image type      : "
    TAG_IMG_FILE    = "Image file name : "
    TAG_BLK_SIZE    = "block size      : "
    TAG_INDENT_SPACE= "                  "


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

    lst_text.append(TAG_IMG_TYP + "SquashFS\n")

    wrapper.initial_indent    = TAG_IMG_FILE
    wrapper.subsequent_indent = TAG_INDENT_SPACE
    lst_text.append(wrapper.fill(szImgfile) + "\n")

    blksize  = "%d" % lblksize
    lst_text.append(TAG_BLK_SIZE   + blksize + " bytes\n")

    # List To Text
    main_text = "".join(lst_text)
    del lst_text

    # Create Button list
    buttons = ["OK", "Back", "Exit"]

    rcode = ButtonInfoWindow(insScreen, "Ready ?", main_text, \
                              main_width, main_height, buttons)

    return rcode

#------------------------------------------------------------
# def MKIMGConfirmSquashFSWindowCtrl()
#
#   Confirm for making SquashFS image.
#
# Input:
#    insScreen    : instance of snack screen
#    insMKIMGInfo : instance of class MKIMGInfo
# Output:
#    str : pressed button ("n" : OK, "b" : Back)
#------------------------------------------------------------
def MKIMGConfirmSquashFSWindowCtrl(insScreen, insMKIMGInfo):
    # Get Parameters
    fromdir = insMKIMGInfo.get_from_dir_path()
    todir   = insMKIMGInfo.get_to_dir_path()
    imgfile = insMKIMGInfo.get_image_file_name()

    (szblksize, lblksize) = insMKIMGInfo.get_squashfs_param()

    while True:
        rcode = MKIMGConfirmSquashFSWindow(insScreen, fromdir, todir, imgfile, lblksize)

        if rcode == "e":
            # exit
            insScreen.popHelpLine()
            insScreen.popWindow()
            exit_hkey = HotkeyExitWindow(insScreen)
            if exit_hkey == "y":
                if insScreen != None:
                    StopHotkeyScreen(insScreen)
                    insScreen = None
                    sys.exit(0)

        elif rcode == "o":
            logfile = imgfile + ".log"
            try:
                fdLog = OpenLogFile(logfile)
                if insScreen != None:
                    StopHotkeyScreen(insScreen)
                    insScreen = None

                MKIMGCreateSquashFS(insMKIMGInfo, fdLog)
                sys.exit(0)

            finally:
                # Log File Close
                fdLog.close()
                sys.exit(0)

        else:
            # back
            return rcode

#-----------------------------------------------------------
# def MKIMGCreateSquashFS()
#
#   Create SquashFS image.
#
# Input:
#    insMKIMGInfo : instance of class MKIMGInfo
#    fdLog        : file descriptor of Log file
# Output:
#    bool         : success=True, fail=False
#-----------------------------------------------------------
def MKIMGCreateSquashFS(insMKIMGInfo, fdLog):

    MSG_START        = "Making the SquashFS image start."
    MSG_END_SUCCESS  = "\nMaking the SquashFS image succeeded."
    MSG_END_FAILED   = "\nMaking the SquashFS image failed."
    MSG_FINISH       = "RootFS Image Maker finish."

    print(MSG_START)
    fdLog.write(MSG_START + "\n")

    rcode = True

    fromdir = insMKIMGInfo.get_from_dir_path()
    todir   = insMKIMGInfo.get_to_dir_path()
    imgname = insMKIMGInfo.get_image_file_name()
    imgpath = todir + "/" + imgname

    (szblksize, lblksize) = insMKIMGInfo.get_squashfs_param()

    # Execute Commands
    cmd = "mksquashfs %s %s -noappend -b %s " % \
             (fromdir, imgpath, lblksize)

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
