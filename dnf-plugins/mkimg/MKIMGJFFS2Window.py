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
# def MKIMGSetupJFFS2Window()
#
#   Display JFFS2 Setup Window.
#
# Input:
#    insScreen    : instance of snack screen
#    szImgsize    : Image size (string)
#    szPagesize   : Page size (string)
#    szErasebs    : Erase block size (string)
#    iEndian      : Endian (0:Little endian, 1:Big endian, default:0)
#    szFromdir    : Path of From-directory
#    szTodir      : Path of To-directory
# Output:
#    str : pressed button ("n" : OK, "b" : Back, "e" : Exit)
#    str : Image size
#    str : Page size
#    str : Erase block size 
#    0,1 : Endian (0:Little endian, 1:Big endian, default:0)
#    str : fromdir
#    str : todir
#------------------------------------------------------------
def MKIMGSetupJFFS2Window(insScreen, szImgsize="0", szPagesize="4096",\
                          szErasebs="16", iEndian=0, szFromdir="", szTodir="rootfs.jffs2.bin"):
    TAG_SRC_DIR    = "From directory   : "
    TAG_TARGET_DIR = "To directory     : "
    TAG_IMG_NAME   = "Image file name  : "
    TAG_IMG_SIZE   = "Image size       : "
    TAG_PAGE_SIZE  = "Page size        : "
    TAG_ERASE_BS   = "Erase block size : "
    TAG_ENDIAN     = "Endian(Default is little) : "

    LBL_LITTLE = "Little endian"
    LBL_BIG    = "Big endian"

    # Create Button instance
    buttons = (("OK", "ok"), ("Back", "back"))
    bb = snack.ButtonBar(insScreen, buttons)

    # Create Grid instance
    g = snack.GridForm(insScreen, "JFFS2 Parameter", 1, 7)
   
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

    # Image size
    sg[2].setField(snack.Textbox(19, 1, TAG_IMG_SIZE), \
                        0, 0, (-14, 0, 0, 0))
    txt_imgsize = snack.Entry(12, szImgsize, scroll = 0)
    sg[2].setField(txt_imgsize, 1, 0, (0, 0, 0, 0))
    sg[2].setField(snack.Textbox(5, 1, "bytes"), 2, 0, (0, 0, 0, 0))


    # Page size
    sg[3].setField(snack.Textbox(19, 1, TAG_PAGE_SIZE), \
                        0, 0, (-14, 0, 0, 0))
    txt_pagesize = snack.Entry(12, szPagesize, scroll = 0)
    sg[3].setField(txt_pagesize, 1, 0, (0, 0, 0, 0))
    sg[3].setField(snack.Textbox(5, 1, "bytes"), 2, 0, (0, 0, 0, 0))


    # Erase block size
    sg[4].setField(snack.Textbox(19, 1, TAG_ERASE_BS), 0, 0, (-14, 0, 0, 0))
    txt_erasebs = snack.Entry(12, szErasebs, scroll = 0)
    sg[4].setField(txt_erasebs, 1, 0, (0, 0, 0, 0))
    sg[4].setField(snack.Textbox(5, 1, "bytes"), 2, 0, (0, 0, 0, 0))


    # Endian
    sg[5].setField(snack.Textbox(29, 1, TAG_ENDIAN), 0, 0, (-7, 0, 0, 0))

    cb_endian1 = snack.Checkbox(LBL_BIG, isOn = iEndian)
    sg[5].setField(cb_endian1, 2, 0, (0, 0, 0, 0))

    for i in range(0, 6):
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

    # set Image size
    imgsize = txt_imgsize.value()
    imgsize = imgsize.strip()

    # set Page size
    pagesize = txt_pagesize.value()
    pagesize = pagesize.strip()

    # set Erase block size
    erasebs = txt_erasebs.value()
    erasebs = erasebs.strip()

    # set Endian
    if cb_endian1.selected():
        endian = 1  #Big endian
    else:
        endian = 0  #Little endian

    insScreen.popWindow()
    return (rcode, imgsize, pagesize, erasebs, endian, fromdir, todir)

#------------------------------------------------------------
# def MKIMGJFFS2WindowCtrl()
#
#   WindowCtrl for making JFFS2 image.
#
# Input:
#    insScreen    : instance of snack screen
#    insMKIMGInfo : instance of class MKIMGInfo
# Output:
#    str : pressed button ("n" : OK, "b" : Back)
#------------------------------------------------------------
def MKIMGJFFS2WindowCtrl(insScreen, insMKIMGInfo):

    ERR_ITEM_IMAGE_SIZE = "Image size"
    ERR_ITEM_PAGE_SIZE  = "Page size"
    ERR_ITEM_ERASE_BS   = "Erase block size"

    while True:
        # Get the default value for JFFS2
        (szimgsize, limgsize, szpagesize, lpagesize, szerasebs, \
         lerasebs, iendian) = insMKIMGInfo.get_jffs2_param()

        szFromdir = insMKIMGInfo.get_from_dir_path()
        szTodir = insMKIMGInfo.get_to_dir_path()

        # Completion the Todir if image_file_name exists
        if insMKIMGInfo.get_image_file_name():
           szTodir = szTodir + "/" + insMKIMGInfo.get_image_file_name()

        (rcode, szimgsize, szpagesize, szerasebs, iendian, szFromdir, szTodir) = \
            MKIMGSetupJFFS2Window(insScreen, szimgsize, szpagesize,\
                                  szerasebs, iendian, szFromdir, szTodir)

        #Change relative path to absolute path
        szFromdir = os.path.abspath(szFromdir);
        szTodir = os.path.abspath(szTodir);

        insMKIMGInfo.set_jffs2_param(szimgsize, szpagesize, szerasebs, iendian)
        insMKIMGInfo.set_from_dir_path(szFromdir)
        insMKIMGInfo.set_to_dir_path(szTodir)

        # Check input paras
        if rcode == "n":
            (err, err_str) = insMKIMGInfo.check_from_dir_path()
            if err != 0:
                item = err_str
                ButtonErrorWindow(insScreen, item)
                continue

            err = insMKIMGInfo.check_jffs2_param()
            if err != 0:
                item = ""
                if err == MKIMG_LABEL_IMG_SIZE:
                    item = ERR_ITEM_IMAGE_SIZE
                elif err == MKIMG_LABEL_PAGE_SIZE:
                    item = ERR_ITEM_PAGE_SIZE
                elif err == MKIMG_LABEL_ERASE_BS:
                    item = ERR_ITEM_ERASE_BS
                ButtonErrorWindow(insScreen, item)
                continue

            else:
                # transfer string to long int
                insMKIMGInfo.set_jffs2_long_param()
                break;

        if rcode == "b":
            # back
            return rcode

#------------------------------------------------------------
# def MKIMGConfirmJFFS2Window()
#
#   Display Confirm Window before making image.
#
# Input:
#    insScreen    : instance of snack screen
#    szFromdir    : Path of From-directory
#    szTodir      : Path of To-directory
#    szImgfile    : Name of Imgfile
#    lImgsize     : Image size (long)
#    lPagesize    : Page size (long)
#    lErasebs     : Erase block size (long)
#    iEndian      : Endian (0:Little endian, 1:Bigendian, default:0)
# Output:
#    str : pressed button ("n" : OK, "b" : Back, "e" : Exit)
#------------------------------------------------------------
def MKIMGConfirmJFFS2Window(insScreen, szFromdir, szTodir, szImgfile, \
                            lImgsize, lPagesize, lErasebs, iEndian):
    TAG_FROM_DIR    = "From directory:"
    TAG_TO_DIR      = "To directory:"
    TAG_IMG_TYP     = "Image type       : "
    TAG_IMG_FILE    = "Image file name  : "
    TAG_IMG_SIZE    = "Image size       : "
    TAG_PAGE_SIZE   = "Page size        : "
    TAG_ERASE_BS    = "Erase block size : "
    TAG_ENDIAN      = "Endian           : "
    TAG_INDENT_SPACE= "                   "

    LBL_LITTLE = "Little endian"
    LBL_BIG    = "Big endian"

    #szTodir, szImgfile = os.path.split(szTodir)

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

    lst_text.append(TAG_IMG_TYP + "JFFS2\n")


    wrapper.initial_indent    = TAG_IMG_FILE
    wrapper.subsequent_indent = TAG_INDENT_SPACE
    lst_text.append(wrapper.fill(szImgfile) + "\n")

    imgsize  = "%d" % lImgsize
    pagesize = "%d" % lPagesize
    erasebs  = "%d" % lErasebs
    lst_text.append(TAG_IMG_SIZE  + imgsize  + " bytes\n")
    lst_text.append(TAG_PAGE_SIZE + pagesize + " bytes\n")
    lst_text.append(TAG_ERASE_BS  + erasebs  + " bytes\n")

    if iEndian == 0:
        endian = LBL_LITTLE
    else:
        endian = LBL_BIG
    lst_text.append(TAG_ENDIAN + endian + "\n")

    # List To Text
    main_text = "".join(lst_text)
    del lst_text

    # Create Button list
    buttons = ["OK", "Back", "Exit"]

    rcode = ButtonInfoWindow(insScreen, "Ready ?", main_text, \
                              main_width, main_height, buttons)

    return rcode

#------------------------------------------------------------
# def MKIMGConfirmJFFS2WindowCtrl()
#
#   Confirm for making JFFS2 image.
#
# Input:
#    insScreen    : instance of snack screen
#    insMKIMGInfo : instance of class MKIMGInfo
# Output:
#    str : pressed button ("n" : OK, "b" : Back)
#------------------------------------------------------------
def MKIMGConfirmJFFS2WindowCtrl(insScreen, insMKIMGInfo):
    # Get Parameters
    fromdir = insMKIMGInfo.get_from_dir_path()
    todir   = insMKIMGInfo.get_to_dir_path()
    imgfile = insMKIMGInfo.get_image_file_name()

    (szimgsize, limgsize, szpagesize, lpagesize, szerasebs, \
     lerasebs, iendian) = insMKIMGInfo.get_jffs2_param()

    while True:
        rcode = MKIMGConfirmJFFS2Window(insScreen, fromdir, todir, imgfile, \
                                        limgsize, lpagesize, lerasebs, iendian)

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

                MKIMGCreateJFFS2(insMKIMGInfo, fdLog)
                sys.exit(0)

            finally:
                # Log File Close
                fdLog.close()
                sys.exit(0)

        else:
            # back
            return rcode

#-----------------------------------------------------------
# def MKIMGCreateJFFS2()
#
#   Create JFFS2 image.
#
# Input:
#    insMKIMGInfo : instance of class MKIMGInfo
#    fdLog        : file descriptor of Log file
# Output:
#    bool         : success=True, fail=False
#-----------------------------------------------------------
def MKIMGCreateJFFS2(insMKIMGInfo, fdLog):

    MSG_START        = "Making the JFFS2 image start."
    MSG_END_SUCCESS  = "Making the JFFS2 image succeeded."
    MSG_END_FAILED   = "Making the JFFS2 image failed."
    MSG_FINISH       = "RootFS Image Maker finish."
    ERR_MSG_CREATE_SIZE = "WARNING: The image file size is larger than the specified size !!"

    print(MSG_START)
    fdLog.write(MSG_START + "\n")

    fromdir = insMKIMGInfo.get_from_dir_path()
    todir   = insMKIMGInfo.get_to_dir_path()
    imgname = insMKIMGInfo.get_image_file_name()
    imgpath = todir + "/" + imgname

    (szimgsize, limgsize, szpagesize, lpagesize, szerasebs, \
     lerasebs, endian) = insMKIMGInfo.get_jffs2_param()

    rcode = True

    if endian == 0:
        endian_op = "l"
    else:
        endian_op = "b"

    # Execute Command
    cmd = "mkfs.jffs2 -d '%s' -s %d -o \'%s\' -p %d -e %d -n -%s" % \
         (fromdir, \
          lpagesize, \
          imgpath, \
          limgsize, \
          lerasebs, \
          endian_op)

    if ExecAndOutLog(cmd, fdLog) != 0:
        rcode = False

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
