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
# def MKIMGSetupRAWWindow()
#
#   Display RAW Setup Window.
#
# Input:
#    insScreen    : instance of snack screen
#    szFromdir    : Path of From-directory
#    szTodir      : Path of To-directory
#    szImgsize    : Image size (string)
#    szLoopdev    : Path of Loop device (default:/dev/loop0)
#    szMountpt    : Path of Mount point (default:/mnt)
#    iFilesystem  : Filesystem (The same as host)
# Output:
#    str : pressed button ("n" : OK, "b" : Back, "e" : Exit)
#    str : fromdir
#    str : todir
#    str : Image size
#    str : Path of Loop device
#    str : Path of Mount point
#    str : Filesystem (The same as host)
#------------------------------------------------------------
def MKIMGSetupRAWWindow(insScreen, szFromdir=".rootfs-x86", szTodir="rootfs.raw.bin", \
                        szImgsize="10", szLoopdev="", szMountpt="", iFilesystem="ext4"):
    TAG_SRC_DIR     = "From directory  : "
    TAG_TARGET_DIR  = "To directory    : "
    TAG_FILESYSTEM  = "Filesystem type : "
    TAG_IMG_SIZE    = "Image size      : "
    TAG_LOOP_DEVICE = "Use loop device : "
    TAG_MOUNT_POINT = "Use mount point : "

    # Create Button instance
    buttons = (("OK", "ok"), ("Back", "back"))
    bb = snack.ButtonBar(insScreen, buttons)

    # Create Grid instance
    g = snack.GridForm(insScreen, "RAW Parameter", 1, 7)

    #init snack.Grid object dict
    sg = {}
    for i in range(0, 6):
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

    # Filesystem
    sg[2].setField(snack.Textbox(19, 1, TAG_FILESYSTEM), \
                        0, 0, (-12, 0, 0, 0))
    txt_filesystem = snack.Entry(15, iFilesystem, scroll = 0)
    sg[2].setField(txt_filesystem, 1, 0, (0, 0, 0, 0))
    sg[2].setField(snack.Textbox(5, 1, ""), 2, 0, (0, 0, 0, 0))

    # Image size
    sg[3].setField(snack.Textbox(19, 1, TAG_IMG_SIZE), \
                        0, 0, (-12, 0, 0, 0))
    txt_imgsize = snack.Entry(15, szImgsize, scroll = 0)
    sg[3].setField(txt_imgsize, 1, 0, (0, 0, 0, 0))
    sg[3].setField(snack.Textbox(5, 1, "bytes"), 2, 0, (0, 0, 0, 0))

    # Loop device
    sg[4].setField(snack.Textbox(19, 1, TAG_LOOP_DEVICE), \
                        0, 0, (-12, 0, 0, 0))
    txt_loopdev = snack.Entry(15, szLoopdev, scroll = 0)
    sg[4].setField(txt_loopdev, 1, 0, (0, 0, 0, 0))
    sg[4].setField(snack.Textbox(5, 1, ""), 2, 0, (0, 0, 0, 0))

    # Mount point
    sg[5].setField(snack.Textbox(19, 1, TAG_MOUNT_POINT), \
                        0, 0, (-12, 0, 0, 0))
    txt_mountpt = snack.Entry(15, szMountpt, scroll = 0)
    sg[5].setField(txt_mountpt, 1, 0, (0, 0, 0, 0))
    sg[5].setField(snack.Textbox(5, 1, ""), 2, 0, (0, 0, 0, 0))

    for i in range(0, 6):
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

    # set Filesystem
    filesystem = txt_filesystem.value()
    filesystem = filesystem.strip()

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
    return (rcode, fromdir, todir, imgsize, loopdev, mountpt, filesystem)


#------------------------------------------------------------
# def MKIMGRAWWindowCtrl()
#
#   WindowCtrl for making RAW image.
#
# Input:
#    insScreen    : instance of snack screen
#    insMKIMGInfo : instance of class MKIMGInfo
# Output:
#    str : pressed button ("n" : OK, "b" : Back)
#------------------------------------------------------------
def MKIMGRAWWindowCtrl(insScreen, insMKIMGInfo):

    ERR_ITEM_IMAGE_SIZE  = "Image size"
    ERR_ITEM_LOOP_DEVICE = "Use loop device"
    ERR_ITEM_MOUNT_POINT = "Use mount point"

    while True:
        # Get the default value for RAW
        (szimgsize, limgsize, szloopdev, szmountpt, ifilesystem) = \
                insMKIMGInfo.get_raw_param()

        szFromdir = insMKIMGInfo.get_from_dir_path()
        szTodir = insMKIMGInfo.get_to_dir_path()

        # Completion the Todir if image_file_name exists
        if insMKIMGInfo.get_image_file_name():
           szTodir = szTodir + "/" + insMKIMGInfo.get_image_file_name()

        (rcode, szFromdir, szTodir, szimgsize, szloopdev, szmountpt, ifilesystem) =\
            MKIMGSetupRAWWindow(insScreen, szFromdir, szTodir, szimgsize,\
                                   szloopdev, szmountpt, ifilesystem)

        # Change relative path to absolute path
        szFromdir = os.path.abspath(szFromdir);
        szTodir = os.path.abspath(szTodir);

        # Set values for insMKIMGInfo
        insMKIMGInfo.set_raw_param(szimgsize, szloopdev, szmountpt, ifilesystem)
        insMKIMGInfo.set_from_dir_path(szFromdir)
        insMKIMGInfo.set_to_dir_path(szTodir)

        # Check input paras
        if rcode == "n":
            (err, err_str) = insMKIMGInfo.check_from_dir_path()
            if err != 0:
                item = err_str
                ButtonErrorWindow(insScreen, item)
                continue

            err = insMKIMGInfo.check_raw_param()
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
                insMKIMGInfo.set_raw_long_param()
                break;

        if rcode == "b":
            # back
            return rcode

#------------------------------------------------------------
# def MKIMGConfirmRAWWindow()
#
#   Display Confirm Window before making image.
#
# Input:
#    insScreen    : instance of snack screen
#    szFromdir    : Path of From-directory
#    szTodir      : Path of To-directory
#    szImgfile    : Name of img file
#    lImgsize     : Image size (long)
#    szLoopdev    : Path of Loop device (default:/dev/loop0)
#    szMountpt    : Path of Mount point (default:/mnt)
#    iFilesystem  : Filesystem (the same as host)
# Output:
#    str : pressed button ("n" : OK, "b" : Back, "e" : Exit)
#------------------------------------------------------------
def MKIMGConfirmRAWWindow(insScreen, szFromdir, szTodir, szImgfile, \
                          lImgsize, szLoopdev, szMountpt, iFilesystem):

    TAG_FROM_DIR    = "From directory:"
    TAG_TO_DIR      = "To directory:"
    TAG_IMG_TYP     = "Image type      : "
    TAG_IMG_FILE    = "Image file name : "
    TAG_IMG_SIZE    = "Image size      : "
    TAG_FILESYSTEM  = "Filesystem type : "
    TAG_LOOP_DEVICE = "Use loop device : "
    TAG_MOUNT_POINT = "Use mount point : "
    TAG_INDENT_SPACE= "  "

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

    lst_text.append(TAG_IMG_TYP + "RAW\n")

    wrapper.initial_indent    = TAG_IMG_FILE
    wrapper.subsequent_indent = TAG_INDENT_SPACE
    lst_text.append(wrapper.fill(szImgfile) + "\n")

    imgsize  = "%d" % lImgsize
    lst_text.append(TAG_IMG_SIZE   + imgsize + " bytes\n")
    lst_text.append(TAG_FILESYSTEM + iFilesystem + "\n")
    lst_text.append(TAG_LOOP_DEVICE + szLoopdev + "\n")
    lst_text.append(TAG_MOUNT_POINT + szMountpt + "\n")

    # List To Text
    main_text = "".join(lst_text)
    del lst_text

    # Create Button list
    buttons = ["OK", "Back", "Exit"]

    rcode = ButtonInfoWindow(insScreen, "Ready ?", main_text, \
                              main_width, main_height, buttons)

    return rcode

#------------------------------------------------------------
# def MKIMGConfirmRAWWindowCtrl()
#
#   Confirm for making RAW image.
#
# Input:
#    insScreen    : instance of snack screen
#    insMKIMGInfo : instance of class MKIMGInfo
# Output:
#    str : pressed button ("n" : OK, "b" : Back)
#------------------------------------------------------------
def MKIMGConfirmRAWWindowCtrl(insScreen, insMKIMGInfo):
    # Get Parameters
    fromdir = insMKIMGInfo.get_from_dir_path()
    todir   = insMKIMGInfo.get_to_dir_path()
    imgfile = insMKIMGInfo.get_image_file_name()

    (szimgsize, limgsize, szloopdev, szmountpt, ifilesystem) = \
                               insMKIMGInfo.get_raw_param()

    szloopdev = os.path.abspath(szloopdev)
    szmountpt = os.path.abspath(szmountpt)

    while True:
        rcode = MKIMGConfirmRAWWindow(insScreen, fromdir, todir, imgfile,\
                                         limgsize, szloopdev, szmountpt, ifilesystem)

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

                MKIMGCreateRAW(insMKIMGInfo, fdLog)
                sys.exit(0)

            finally:
                # Log File Close
                fdLog.close()
                sys.exit(0)

        else:
            # back
            return rcode

#-----------------------------------------------------------
# def MKIMGCreateRAW()
#
#   Create RAW image.
#
# Input:
#    insMKIMGInfo : instance of class MKIMGInfo
#    fdLog        : file descriptor of Log file
# Output:
#    bool         : success=True, fail=False
#-----------------------------------------------------------
def MKIMGCreateRAW(insMKIMGInfo, fdLog):

    MSG_START        = "Making the RAW image start."
    MSG_END_SUCCESS  = "\nMaking the RAW image succeeded."
    MSG_END_FAILED   = "\nMaking the RAW image failed."
    MSG_FINISH       = "RootFS Image Maker finish."
    ERR_MSG_CREATE_SIZE = "WARNING: The image file size is larger than the specified size !!"

    print(MSG_START)
    fdLog.write(MSG_START + "\n")

    rcode = True

    fromdir = insMKIMGInfo.get_from_dir_path()
    todir   = insMKIMGInfo.get_to_dir_path()
    imgname = insMKIMGInfo.get_image_file_name()
    imgpath = todir + "/" + imgname

    (szimgsize, limgsize, szloop, szmountpt, filesystem) = insMKIMGInfo.get_raw_param()

    szloop    = os.path.abspath(szloop)
    szmountpt = os.path.abspath(szmountpt)

    # utils for mkfs command
    mkfscmd = "mkfs.%s" % filesystem

    # calculate count
    count = int(limgsize/MKIMG_BLOCK_SIZE)

    # Init all cmd steps
    cmd_steps = { 0: "dd if=/dev/zero of=\'%s\' bs=%s count=%s" %(imgpath, MKIMG_BLOCK_SIZE, count), \
                  1: "/sbin/losetup \'%s\' \'%s\'" %(szloop, imgpath), \
                  2: "/sbin/%s \'%s\'" %(mkfscmd, szloop),
                  3: "mount -t %s \'%s\' \'%s\'" %(filesystem, szloop, szmountpt), \
                  4: "cd \'%s\'; find . -print | cpio -p \'%s\'" %(fromdir, szmountpt), \
                  5: "umount \'%s\'" %szmountpt, \
                  6: "/sbin/losetup -d \'%s\'" %szloop \
                   }

    # Execute Commands
    step = 0
    while step < 7:
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
