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
#    szvid        : Id of /dev/ubifs
#    szvname      : Vol Name of /dev/ubifs
# Output:
#    str : pressed button ("n" : OK, "b" : Back, "e" : Exit)
#    str : fromdir
#    str : todir
#    str : blksize
#    str : leb
#    str : meb
#    str : vid
#    str : vname
#------------------------------------------------------------
def MKIMGSetupUBIFSWindow(insScreen, szFromdir, szTodir, \
                        szMinSize, szLeb, szMeb, szVol_id, szVol_name):

    TAG_SRC_DIR     = "From directory  : "
    TAG_TARGET_DIR  = "To directory    : "
    TAG_MINSIZE     = "Minimum I/O unit size             : "
    TAG_LEB         = "Logical erase block size( > 15360): "
    TAG_MEB         = "Maximum logical erase block count : "
    TAG_VID         = "Id of UBIFS device : "
    TAG_VNAME       = "Name of UBIFS Volume : "

    # Create Button instance
    buttons = (("OK", "ok"), ("Back", "back"))
    bb = snack.ButtonBar(insScreen, buttons)

    # Create Grid instance
    g = snack.GridForm(insScreen, "UBIFS Parameter", 1, 8)

    #init snack.Grid object dict
    sg = {}
    for i in range(0, 7):
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

    # Minimam Block Size
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

    # Vol id of ubifs device
    sg[5].setField(snack.Textbox(36, 1, TAG_VID), \
                        0, 0, (2, 0, 0, 0))
    txt_vid = snack.Entry(15, szVol_id, scroll = 0)
    sg[5].setField(txt_vid, 1, 0, (0, 0, 0, 0))
    sg[5].setField(snack.Textbox(5, 1, ""), 2, 0, (0, 0, 0, 0))

    # Vol name of ubifs device
    sg[6].setField(snack.Textbox(36, 1, TAG_VNAME), \
                        0, 0, (2, 0, 0, 0))
    txt_vname = snack.Entry(15, szVol_name, scroll = 0)
    sg[6].setField(txt_vname, 1, 0, (0, 0, 0, 0))
    sg[6].setField(snack.Textbox(5, 1, ""), 2, 0, (0, 0, 0, 0))

    for i in range(0, 7):
        g.add(sg[i], 0, i, (0, 0, 0, 0))

    # Add buttons
    g.add(bb, 0, 7, (0, 1, 0, -1))

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

    # set maximam block size
    vid = txt_vid.value()
    vid = vid.strip()

    # set maximam block size
    vname = txt_vname.value()
    vname = vname.strip()

    insScreen.popWindow()
    return (rcode, fromdir, todir, blksize, leb, meb, vid, vname)

#------------------------------------------------------------
# def MKIMGUBIFSWindowCtrl()
#
#   WindowCtrl for making UBIFS image.
#
# Input:
#    insScreen    : instance of snack screen
#    insMKIMGInfo : instance of class MKIMGInfo
# Output:
#    str : pressed button ("n" : OK, "b" : Back)
#------------------------------------------------------------
def MKIMGUBIFSWindowCtrl(insScreen, insMKIMGInfo):

    ERR_ITEM_MIN = "minimum I/O unit size"
    ERR_ITEM_LEB = "Logical Erase Block"
    ERR_ITEM_MEB = "Maximam Erase Block"
    ERR_ITEM_VID = "Id of UBIFS device"

    while True:
        # Get the default value for UBIFS
        (szblksize, lblksize, szleb, lleb, szmeb, lmeb, szvid, szvname) = \
                insMKIMGInfo.get_ubifs_param()

        szFromdir = insMKIMGInfo.get_from_dir_path()
        szTodir = insMKIMGInfo.get_to_dir_path()

        # Completion the Todir if image_file_name exists
        if insMKIMGInfo.get_image_file_name():
           szTodir = szTodir + "/" + insMKIMGInfo.get_image_file_name()

        (rcode, szFromdir, szTodir, szblksize, szleb, szmeb, szvid, szvname) = \
            MKIMGSetupUBIFSWindow(insScreen, szFromdir, szTodir, szblksize, szleb, szmeb, szvid, szvname)

        #Change relative path to absolute path
        szFromdir = os.path.abspath(szFromdir);
        szTodir = os.path.abspath(szTodir);

        insMKIMGInfo.set_ubifs_param(szblksize, szleb, szmeb, szvid, szvname)
        insMKIMGInfo.set_from_dir_path(szFromdir)
        insMKIMGInfo.set_to_dir_path(szTodir)

        # Check input params
        if rcode == "n":
            (err, err_str) = insMKIMGInfo.check_from_dir_path()
            if err != 0:
                item = err_str
                ButtonErrorWindow(insScreen, item)
                continue

            err = insMKIMGInfo.check_ubifs_param()
            if err != 0:
                item = ""
                if err == MKIMG_LABEL_BLK_SIZE:
                    item = ERR_ITEM_MIN
                elif err == MKIMG_LABEL_LEB_SIZE:
                    item = ERR_ITEM_LEB
                elif err == MKIMG_LABEL_MEB_SIZE:
                    item = ERR_ITEM_MEB
                elif err == MKIMG_LABEL_VOL_ID:
                    item = ERR_ITEM_VID

                ButtonErrorWindow(insScreen, item)
                continue

            else:
                # transfer string to long int
                insMKIMGInfo.set_ubifs_long_param()
                break;

        if rcode == "b":
            # back
            return rcode

#------------------------------------------------------------
# def MKIMGConfirmUBIFSWindow()
#
#   Display Confirm Window before making image.
#
# Input:
#    insScreen    : instance of snack screen
#    szFromdir    : Path of From-directory
#    szImgfile    : Name of Imgfile
#    szTodir      : Path of To-directory
#    lblksize     : Minimum I/O unit size (long)
#    lleb         : Logical erase block size(long)
#    lmeb         : Maximum logical erase block count(long)
#    szvid        : Id of /dev/ubifs
#    szvname      : Vol Name of /dev/ubifs
# Output:
#    str : pressed button ("n" : OK, "b" : Back, "e" : Exit)
#------------------------------------------------------------
def MKIMGConfirmUBIFSWindow(insScreen, szFromdir, szTodir, szImgfile, \
                          lblksize, lleb, lmeb, szvid, szvname):

    TAG_FROM_DIR    = "From directory:"
    TAG_TO_DIR      = "To directory:"
    TAG_IMG_TYP     = "Image type      : "
    TAG_IMG_FILE    = "Image file name                   : "
    TAG_BLK_SIZE    = "Minimum I/O unit size             : "
    TAG_LEB         = "Logical erase block size          : "
    TAG_MEB         = "Maximum logical erase block count : "
    TAG_VID         = "Id of UBIFS device                  : "
    TAG_VNAME       = "Name of UBIFS Volume                : "
    TAG_INDENT_SPACE= "                                    "

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

    blksize  = "%d" % lblksize
    lst_text.append(TAG_BLK_SIZE + blksize + " bytes\n")

    leb  = "%d" % lleb
    lst_text.append(TAG_LEB + leb + " bytes\n")

    meb = "%d" % lmeb
    lst_text.append(TAG_MEB + meb + " count\n")

    lst_text.append(TAG_VID + "/dev/ubifs" + szvid + "\n")
    lst_text.append(TAG_VNAME + szvname + "\n")

    # List To Text
    main_text = "".join(lst_text)
    del lst_text

    # Create Button list
    buttons = ["OK", "Back", "Exit"]

    rcode = ButtonInfoWindow(insScreen, "Ready ?", main_text, \
                              main_width, main_height, buttons)

    return rcode

#------------------------------------------------------------
# def MKIMGConfirmUBIFSWindowCtrl()
#
#   Confirm for making UBIFSFS image.
#
# Input:
#    insScreen    : instance of snack screen
#    insMKIMGInfo : instance of class MKIMGInfo
# Output:
#    str : pressed button ("n" : OK, "b" : Back)
#------------------------------------------------------------
def MKIMGConfirmUBIFSWindowCtrl(insScreen, insMKIMGInfo):
    # Get Parameters
    fromdir = insMKIMGInfo.get_from_dir_path()
    todir   = insMKIMGInfo.get_to_dir_path()
    imgfile = insMKIMGInfo.get_image_file_name()

    (szblksize, lblksize, szleb, lleb, szmeb, lmeb, szvid, szvname) = \
                               insMKIMGInfo.get_ubifs_param()

    while True:
        rcode = MKIMGConfirmUBIFSWindow(insScreen, fromdir, todir, imgfile,\
                                      lblksize, lleb, lmeb, szvid, szvname)

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

                MKIMGCreateUBIFS(insMKIMGInfo, fdLog)
                sys.exit(0)

            finally:
                # Log File Close
                fdLog.close()
                sys.exit(0)

        else:
            # back
            return rcode

#-----------------------------------------------------------
# def MKIMGCreateUBIFS()
#
#   Create UBIFS image.
#
# Input:
#    insMKIMGInfo : instance of class MKIMGInfo
#    fdLog        : file descriptor of Log file
# Output:
#    bool         : success=True, fail=False
#-----------------------------------------------------------
def MKIMGCreateUBIFS(insMKIMGInfo, fdLog):

    MSG_START        = "Making the UBIFS image start."
    MSG_END_SUCCESS  = "\nMaking the UBIFS image succeeded."
    MSG_END_FAILED   = "\nMaking the UBIFS image failed."
    MSG_FINISH       = "RootFS Image Maker finish."

    print(MSG_START)
    fdLog.write(MSG_START + "\n")

    rcode = True

    fromdir = insMKIMGInfo.get_from_dir_path()
    todir   = insMKIMGInfo.get_to_dir_path()
    imgname = insMKIMGInfo.get_image_file_name()
    imgpath = todir + "/" + "rootfs.ubifs.bin"

    (szblksize, lblksize, szleb, lleb, szmeb, lmeb, szvid, szvname) = insMKIMGInfo.get_ubifs_param()

    # Execute Commands
    #Make ubifsfs image (flash in uboot)
    cmd = "mkfs.ubifs -m %s -e %s -c %s -r %s %s " % \
             (lblksize, lleb, lmeb, fromdir, imgpath)
    if ExecAndOutLog(cmd, fdLog) != 0:
        rcode = False

    if rcode == True:
        os.chmod(imgpath, 0o644)

    # Make ubifs image (flash in linux)
    # Calcaulte vol_size
    Vol_size = os.path.getsize(imgpath) + 1000000

    # Write ubi.ini file
    f = open("ubi.ini", "w")
    f.write('[ubi_rfs]\n'
            'mode=ubi\n'
            'image=%s\n'
            'vol_id=%s\n'
            'vol_size=%d\n'
            'vol_type=dynamic\n'
            'vol_name=%s\n'
            'vol_alignment=1\n'
            'vol_flags=autoresize\n' %("rootfs.ubifs.bin", szvid, Vol_size, szvname))
    f.close()

    Eraseblock_size = lleb + lblksize*2
    cmd = "ubinize -o %s -p %s -m %s -s %s -O %s ubi.ini" % \
              (imgname, Eraseblock_size, lblksize, lblksize, lblksize)
    if ExecAndOutLog(cmd, fdLog) != 0:
        rcode = False

    if rcode == True:
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
