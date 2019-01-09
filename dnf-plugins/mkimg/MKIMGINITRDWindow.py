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
# def MKIMGSetupINITRDWindow()
#
#   Display INITRD Setup Window.
#
# Input:
#    insScreen    : instance of snack screen
#    szFromdir    : Path of From-directory
#    szTodir      : Path of To-directory
#    szImgsize    : Image size (string)
#    szLoopdev    : Path of Loop device (default:/dev/loop0)
# Output:
#    str : pressed button ("n" : OK, "b" : Back, "e" : Exit)
#    str : fromdir
#    str : todir
#    str : Image size
#    str : Path of Loop device
#    str : Path of Mount point
#------------------------------------------------------------
def MKIMGSetupINITRDWindow(insScreen, szFromdir=".rootfs-x86", szTodir="rootfs.initrd.bin", \
                          szImgsize="10", szLoopdev="", szMountpt=""):
    TAG_SRC_DIR     = "From directory  : "
    TAG_TARGET_DIR  = "To directory    : "
    TAG_IMG_SIZE    = "Image size      : "
    TAG_LOOP_DEVICE = "Use loop device : "
    TAG_MOUNT_POINT = "Use mount point : "

    # Create Button instance
    buttons = (("OK", "ok"), ("Back", "back"))
    bb = snack.ButtonBar(insScreen, buttons)

    # Create Grid instance
    g = snack.GridForm(insScreen, "INITRD Parameter", 1, 7)
   
    #init snack.Grid object dict
    sg = {}
    for i in range(0, 5):
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

    # Image size
    sg[2].setField(snack.Textbox(19, 1, TAG_IMG_SIZE), \
                        0, 0, (-12, 0, 0, 0))
    txt_imgsize = snack.Entry(15, szImgsize, scroll = 0)
    sg[2].setField(txt_imgsize, 1, 0, (0, 0, 0, 0))
    sg[2].setField(snack.Textbox(5, 1, "bytes"), 2, 0, (0, 0, 0, 0))

    # Loop device
    sg[3].setField(snack.Textbox(19, 1, TAG_LOOP_DEVICE), \
                        0, 0, (-12, 0, 0, 0))
    txt_loopdev = snack.Entry(15, szLoopdev, scroll = 1)
    sg[3].setField(txt_loopdev, 1, 0, (0, 0, 0, 0))
    sg[3].setField(snack.Textbox(5, 1, ""), 2, 0, (0, 0, 0, 0))

    # Mount point
    sg[4].setField(snack.Textbox(19, 1, TAG_MOUNT_POINT), \
                        0, 0, (-12, 0, 0, 0))
    txt_mountpt = snack.Entry(15, szMountpt, scroll = 1)
    sg[4].setField(txt_mountpt, 1, 0, (0, 0, 0, 0))
    sg[4].setField(snack.Textbox(5, 1, ""), 2, 0, (0, 0, 0, 0))

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

    # set Image size
    imgsize = txt_imgsize.value()
    imgsize = imgsize.strip()

    # set Loop device
    loopdev = txt_loopdev.value()
    loopdev = loopdev.strip()

    # set Mount point
    mountpt = txt_mountpt.value()
    mountpt = mountpt.strip()
    insScreen.popWindow()
    return (rcode, fromdir, todir, imgsize, loopdev, mountpt)

#------------------------------------------------------------
# def MKIMGINITRDWindowCtrl()
#
#   WindowCtrl for making INITRD image.
#
# Input:
#    insScreen    : instance of snack screen
#    insMKIMGInfo : instance of class MKIMGInfo
# Output:
#    str : pressed button ("n" : OK, "b" : Back)
#------------------------------------------------------------
def MKIMGINITRDWindowCtrl(insScreen, insMKIMGInfo):

    ERR_ITEM_IMAGE_SIZE  = "Image size"
    ERR_ITEM_LOOP_DEVICE = "Use loop device"
    ERR_ITEM_MOUNT_POINT = "Use mount point"

    while True:
        # Get the default value for INITRD
        (szimgsize, limgsize, szloopdev, szmountpt) = \
                               insMKIMGInfo.get_initrd_param()


        szFromdir = insMKIMGInfo.get_from_dir_path()
        szTodir = insMKIMGInfo.get_to_dir_path()

        # Completion the Todir if image_file_name exists
        if insMKIMGInfo.get_image_file_name():
           szTodir = szTodir + "/" + insMKIMGInfo.get_image_file_name()

        (rcode, szFromdir, szTodir, szimgsize, szloopdev, szmountpt) =\
            MKIMGSetupINITRDWindow(insScreen, szFromdir, szTodir, szimgsize,\
                                   szloopdev, szmountpt)

        #Change relative path to absolute path
        szFromdir = os.path.abspath(szFromdir);
        szTodir = os.path.abspath(szTodir);

        #set values for insMKIMGInfo
        insMKIMGInfo.set_initrd_param(szimgsize, szloopdev, szmountpt)
        insMKIMGInfo.set_from_dir_path(szFromdir)
        insMKIMGInfo.set_to_dir_path(szTodir)

        # Check input paras
        if rcode == "n":
            (err, err_str) = insMKIMGInfo.check_from_dir_path()
            if err != 0:
                item = err_str
                ButtonErrorWindow(insScreen, item)
                continue

            err = insMKIMGInfo.check_initrd_param()
            if err != 0:
                item = ""
                if err == MKIMG_LABEL_IMG_SIZE:
                    item = ERR_ITEM_IMAGE_SIZE
                elif err == MKIMG_LABEL_LOOP_DEV:
                    item = ERR_ITEM_LOOP_DEVICE
                elif err == MKIMG_LABEL_MOUNT_PT:
                    item = ERR_ITEM_MOUNT_POINT
                ButtonErrorWindow(insScreen, item)
                continue

            else:
                # transfer string to long int
                insMKIMGInfo.set_initrd_long_param()
                break;

        if rcode == "b":
            # back
            return rcode

#------------------------------------------------------------
# def MKIMGConfirmINITRDWindow()
#
#   Display Confirm Window before making image.
#
# Input:
#    insScreen    : instance of snack screen
#    szFromdir    : Path of From-directory
#    szTodir      : Path of To-directory
#    szImgfile    : Name of Imgfile
#    lImgsize     : Image size (long)
#    szLoopdev    : Path of Loop device
#    szMountpt    : Path of mount point
# Output:
#    str : pressed button ("n" : OK, "b" : Back, "e" : Exit)
#------------------------------------------------------------
def MKIMGConfirmINITRDWindow(insScreen, szFromdir, szTodir, szImgfile, \
                             lImgsize, szLoopdev, szMountpt):
    TAG_FROM_DIR    = "From directory:"
    TAG_TO_DIR      = "To directory:"
    TAG_IMG_TYP     = "Image type      : "
    TAG_IMG_FILE    = "Image file name : "
    TAG_IMG_SIZE    = "Image size      : "
    TAG_FILESYSTEM  = "Filesystem type : "
    TAG_LOOP_DEVICE = "Use loop device : "
    TAG_MOUNT_POINT = "Use mount point : "
    TAG_INDENT_SPACE= "                  "

    LBL_EXT2 = "ext2"

    # Create Main Text
    (main_width, main_height) = GetButtonMainSize(insScreen)

    wrapper = textwrap.TextWrapper(width = main_width - 2)

    wrapper.initial_indent    = "  "
    wrapper.subsequent_indent = "  "

    lst_text = []

    lst_text.append("Are you sure to start making filesystem image ?\n\n")

    if not szFromdir.startswith("/"):
        szFromdir = os.getcwd() + '/' +szFromdir

    lst_text.append(TAG_FROM_DIR + "\n")
    lst_text.append(wrapper.fill(szFromdir) + "\n\n")

    lst_text.append(TAG_TO_DIR + "\n")
    lst_text.append(wrapper.fill(szTodir) + "\n\n")

    lst_text.append(TAG_IMG_TYP + "INITRD\n")


    wrapper.initial_indent    = TAG_IMG_FILE
    wrapper.subsequent_indent = TAG_INDENT_SPACE
    lst_text.append(wrapper.fill(szImgfile) + "\n")

    imgsize  = "%d" % lImgsize
    lst_text.append(TAG_IMG_SIZE   + imgsize + " bytes\n")
    lst_text.append(TAG_FILESYSTEM + LBL_EXT2  + "\n")

    wrapper.initial_indent    = TAG_LOOP_DEVICE
    wrapper.subsequent_indent = TAG_INDENT_SPACE
    lst_text.append(wrapper.fill(szLoopdev) + "\n")

    wrapper.initial_indent    = TAG_MOUNT_POINT
    wrapper.subsequent_indent = TAG_INDENT_SPACE
    lst_text.append(wrapper.fill(szMountpt) + "\n")
    # List To Text
    main_text = "".join(lst_text)
    del lst_text

    # Create Button list
    buttons = ["OK", "Back", "Exit"]

    rcode = ButtonInfoWindow(insScreen, "Ready ?", main_text, \
                              main_width, main_height, buttons)

    return rcode

#------------------------------------------------------------
# def MKIMGConfirmINITRDWindowCtrl()
#
#   Confirm for making INITRD image.
#
# Input:
#    insScreen    : instance of snack screen
#    insMKIMGInfo : instance of class MKIMGInfo
# Output:
#    str : pressed button ("n" : OK, "b" : Back)
#------------------------------------------------------------
def MKIMGConfirmINITRDWindowCtrl(insScreen, insMKIMGInfo):
    # Get Parameters
    fromdir = insMKIMGInfo.get_from_dir_path()
    todir   = insMKIMGInfo.get_to_dir_path()
    imgfile = insMKIMGInfo.get_image_file_name()

    (szimgsize, limgsize, szloopdev, szmountpt) = \
                               insMKIMGInfo.get_initrd_param()

    szloopdev = os.path.abspath(szloopdev)
    szmountpt = os.path.abspath(szmountpt)

    while True:
        rcode = MKIMGConfirmINITRDWindow(insScreen, fromdir, todir, imgfile,\
                                         limgsize, szloopdev, szmountpt)

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

                MKIMGCreateINITRD(insMKIMGInfo, fdLog)
                sys.exit(0)

            finally:
                # Log File Close
                fdLog.close()
                sys.exit(0)

        else:
            # back
            return rcode

#-----------------------------------------------------------
# def MKIMGCreateINITRD()
#

#   Create INITRD image.
#
# Input:
#    insMKIMGInfo : instance of class MKIMGInfo
#    fdLog        : file descriptor of Log file
# Output:
#    bool         : success=True, fail=False
#-----------------------------------------------------------
def MKIMGCreateINITRD(insMKIMGInfo, fdLog):

    MSG_START        = "Making the INITRD image start."
    MSG_END_SUCCESS  = "\nMaking the INITRD image succeeded."
    MSG_END_FAILED   = "\nMaking the INITRD image failed."
    MSG_FINISH       = "RootFS Image Maker finish."

    print(MSG_START)
    fdLog.write(MSG_START + "\n")

    rcode = True

    fromdir = insMKIMGInfo.get_from_dir_path()
    todir   = insMKIMGInfo.get_to_dir_path()
    imgname = insMKIMGInfo.get_image_file_name()
    imgpath = todir + "/" + imgname

    (szimgsize, limgsize, szloop, szmountpt) = insMKIMGInfo.get_initrd_param()

    szloop    = os.path.abspath(szloop)
    szmountpt = os.path.abspath(szmountpt)

    # calculate count
    count = int(limgsize/MKIMG_BLOCK_SIZE)
    
    # Init all cmd steps
    cmd_steps = { 0: "dd if=/dev/zero of=\'%s\' bs=%s count=%s" %(imgpath, MKIMG_BLOCK_SIZE, count), \
                  1: "/sbin/losetup \'%s\' \'%s\'" %(szloop, imgpath), \
                  2: "/sbin/mkfs.ext2 \'%s\'" %szloop, \
                  3: "mount -t ext2 \'%s\' \'%s\'" %(szloop, szmountpt), \
                  4: "cd \'%s\'; find . -print | cpio -p \'%s\'" %(fromdir, szmountpt), \
                  5: "umount \'%s\'" %szmountpt, \
                  6: "/sbin/losetup -d \'%s\'" %szloop, \
                  7: "gzip -9 -f \'%s\'" %imgpath \
                   }

    # Execute Commands
    step = 0
    while step < 8:
        cmd = cmd_steps[step]
        if ExecAndOutLog(cmd, fdLog) != 0:
            rcode = False
            if step == 2 or step == 3:
                step = 6
                continue
            if step == 4 or step == 5:
                step = step + 1
                continue
            else:
                break

        step = step + 1

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
