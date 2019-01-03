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
# def MKIMGSetupINITRAMFSWindow()
#
#   Display INITRAMFS Setup Window.
#
# Input:
#    insScreen    : instance of snack screen
#    szFromdir    : Path of From-directory
#    szTodir      : Path of To-directory
# Output:
#    str : pressed button ("n" : OK, "b" : Back, "e" : Exit)
#    str : fromdir
#    str : todir
#------------------------------------------------------------
def MKIMGSetupINITRAMFSWindow(insScreen, szFromdir=".rootfs-x86", szTodir="rootfs.initramfs.bin"):
    TAG_SRC_DIR    = "From directory   : "
    TAG_TARGET_DIR = "To directory     : "

    # Create Button instance
    buttons = (("OK", "ok"), ("Back", "back"))
    bb = snack.ButtonBar(insScreen, buttons)

    # Create Grid instance
    g = snack.GridForm(insScreen, "INITRAMFS Parameter", 1, 7)
   
    #init snack.Grid object dict
    sg = {}
    for i in range(0, 2):
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

    for i in range(0, 2):
        g.add(sg[i], 0, i, (0, 0, 0, 0))
    
    #Add buttons
    g.add(bb,  0, 6, (0, 1, 0, -1))

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

    insScreen.popWindow()
    return (rcode, fromdir, todir)

#------------------------------------------------------------
# def MKIMGINITRAMFSWindowCtrl()
#
#   WindowCtrl for making INITRAMFS image.
#
# Input:
#    insScreen    : instance of snack screen
#    insMKIMGInfo : instance of class MKIMGInfo
# Output:
#    str : pressed button ("n" : OK, "b" : Back)
#------------------------------------------------------------
def MKIMGINITRAMFSWindowCtrl(insScreen, insMKIMGInfo):

    while True:
        #Get the default value for INITRAMFS

        szFromdir = insMKIMGInfo.get_from_dir_path()
        szTodir = insMKIMGInfo.get_to_dir_path()

        # Completion the Todir if image_file_name exists
        if insMKIMGInfo.get_image_file_name():
           szTodir = szTodir + "/" + insMKIMGInfo.get_image_file_name()

        (rcode, szFromdir, szTodir) = \
            MKIMGSetupINITRAMFSWindow(insScreen, szFromdir, szTodir)

        #Change relative path to absolute path
        szFromdir = os.path.abspath(szFromdir);
        szTodir = os.path.abspath(szTodir);

        insMKIMGInfo.set_from_dir_path(szFromdir)
        insMKIMGInfo.set_to_dir_path(szTodir)

        # Check input paras
        if rcode == "n":
            (err, err_str) = insMKIMGInfo.check_from_dir_path()
            if err != 0:
                item = err_str
                ButtonErrorWindow(insScreen, item)
                continue

            else:
                break;


        if rcode == "b":
            # back
            return rcode

#------------------------------------------------------------
# def MKIMGConfirmINITRAMFSWindow()
#
#   Display Confirm Window before making image.
#
# Input:
#    insScreen    : instance of snack screen
#    szFromdir    : Path of From-directory
#    szTodir      : Path of To-directory
#    szImgfile    : Name of Image-file
# Output:
#    str : pressed button ("n" : OK, "b" : Back, "e" : Exit)
#------------------------------------------------------------
def MKIMGConfirmINITRAMFSWindow(insScreen, szFromdir, szTodir, szImgfile):
    TAG_FROM_DIR    = "From directory:"
    TAG_TO_DIR      = "To directory:"
    TAG_IMG_TYP     = "Image type       : "
    TAG_IMG_FILE    = "Image file name  : "
    TAG_INDENT_SPACE= "                   "

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

    lst_text.append(TAG_IMG_TYP + "INITRAMFS\n")


    wrapper.initial_indent    = TAG_IMG_FILE
    wrapper.subsequent_indent = TAG_INDENT_SPACE
    lst_text.append(wrapper.fill(szImgfile) + "\n")

    # List To Text
    main_text = "".join(lst_text)
    del lst_text

    # Create Button list
    buttons = ["OK", "Back", "Exit"]

    rcode = ButtonInfoWindow(insScreen, "Ready ?", main_text, \
                              main_width, main_height, buttons)

    return rcode

#------------------------------------------------------------
# def MKIMGConfirmINITRAMFSWindowCtrl()
#
#   Confirm for making INITRAMFS image.
#
# Input:
#    insScreen    : instance of snack screen
#    insMKIMGInfo : instance of class MKIMGInfo
# Output:
#    str : pressed button ("n" : OK, "b" : Back)
#------------------------------------------------------------
def MKIMGConfirmINITRAMFSWindowCtrl(insScreen, insMKIMGInfo):
    # Get Parameters
    fromdir = insMKIMGInfo.get_from_dir_path()
    todir   = insMKIMGInfo.get_to_dir_path()
    imgfile = insMKIMGInfo.get_image_file_name()

    while True:
        rcode = MKIMGConfirmINITRAMFSWindow(insScreen, fromdir, todir, imgfile)

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

                MKIMGCreateINITRAMFS(insMKIMGInfo, fdLog)
                sys.exit(0)

            finally:
                # Log File Close
                fdLog.close()
                sys.exit(0)

        else:
            # back
            return rcode

#-----------------------------------------------------------
# def MKIMGCreateINITRAMFS()
#
#   Create INITRAMFS image.
#
# Input:
#    insMKIMGInfo : instance of class MKIMGInfo
#    fdLog        : file descriptor of Log file
# Output:
#    bool         : success=True, fail=False
#-----------------------------------------------------------
def MKIMGCreateINITRAMFS(insMKIMGInfo, fdLog):

    MSG_START        = "Making the INITRAMFS image start."
    MSG_END_SUCCESS  = "\nMaking the INITRAMFS image succeeded."
    MSG_END_FAILED   = "Making the INITRAMFS image failed."
    MSG_FINISH       = "RootFS Image Maker finish."

    print(MSG_START)
    fdLog.write(MSG_START + "\n")

    rcode = True

    fromdir = insMKIMGInfo.get_from_dir_path()
    todir   = insMKIMGInfo.get_to_dir_path()
    imgname = insMKIMGInfo.get_image_file_name()
    imgpath = todir + "/" + imgname

    # Execute Command
    cmd = "cd \'%s\'; find . -print | cpio -o -H newc > \'%s\'" % \
            (fromdir, imgpath)
    if ExecAndOutLog(cmd, fdLog) != 0:
        rcode = False

    #if rcode == True:
    #    cmd = "gzip -9 \'%s\'" % todir
    #    if ExecAndOutLog(cmd, fdLog) != 0:
    #        rcode = False

    if rcode == True:
        os.chmod(todir, 0o644)
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
