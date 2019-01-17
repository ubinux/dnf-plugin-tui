#
# Copyright (C) Fujitsu Limited 2018 All rights reserved
#

import os

#import logging, logging.handlers

from ..Define import DEF_DEFAULT_LOOP_DEVICE
from ..Define import DEF_DEFAULT_LOOP_MOUNT_POINT

from .CheckString import *

MKIMG_IMG_TYPE_JFFS2     = 0
MKIMG_IMG_TYPE_INITRAMFS = 1
MKIMG_IMG_TYPE_INITRD    = 2
MKIMG_IMG_TYPE_RAW       = 3
MKIMG_IMG_TYPE_SQUASHFS  = 4
MKIMG_IMG_TYPE_UBIFS     = 5

MKIMG_LABEL_IMG_SIZE     = 1
MKIMG_LABEL_PAGE_SIZE    = 2
MKIMG_LABEL_ERASE_BS     = 3
MKIMG_LABEL_LOOP_DEV     = 4
MKIMG_LABEL_MOUNT_PT     = 5
MKIMG_LABEL_BLK_SIZE     = 6
MKIMG_LABEL_LEB_SIZE     = 7
MKIMG_LABEL_MEB_SIZE     = 8
MKIMG_LABEL_COMPRESS     = 9
MKIMG_LABEL_SEGSHIFT     = 10
MKIMG_LABEL_WRITESHIFT   = 11
MKIMG_LABEL_VOL_ID       = 12

MKIMG_BLOCK_SIZE         = 512  # Block size

#-----------------------------------------------------------------------------
# class MKIMGInfo()
#
#   Input data information class.
#
# Class variable:
#
#   Parameters from Command line Options
#      sFrom_dir     : Path of From-directory
#      sTo_dir       : Path of To-directory
#      sImg_file     : Name of Image-file
#      iType         : Image type (0:JFFS2, 1:INITRAMFS, 2:INITRD, 3:RAW)
#
#   Parameters for Making JFFS2 image
#      sJFFS2_Img_size  : Image size (string)
#      lJFFS2_Img_size  : Image size (long)
#      sJFFS2_Page_size : Page size (string, default:4K)
#      lJFFS2_Page_size : Page size (long)
#      sJFFS2_Erase_bs  : Erase block size (string)
#      lJFFS2_Erase_bs  : Erase block size (long)
#      iJFFS2_Endian    : Endian (0:Little endian, 1:Bigendian, default:0)
#
#   Parameters for Making INITRD image
#      sINITRD_Img_size : Image size (string)
#      lINITRD_Img_size : Image size (long)
#      sINITRD_Loop_dev : Path of Loop device (default:/dev/loop0)
#      sINITRD_Mount_pt : Path of Mount point (default:/mnt)
#
#   Parameters for Making RAW image
#      sRAW_Img_size    : Image size (string)
#      lRAW_Img_size    : Image size (long)
#      sRAW_Loop_dev    : Path of Loop device (default:/dev/loop0)
#      sRAW_Mount_pt    : Path of Mount point (default:/mnt)
#      iRAW_Filesystem  : Filesystem (0:ext2, 1:ext3, 2:ext4, default:0)
#
#   Parameters for Making UBI image
#      sRAW_Img_size    : Image size (string)
#      lRAW_Img_size    : Image size (long)
#      sRAW_Loop_dev    : Path of Loop device (default:/dev/loop0)
#      sRAW_Mount_pt    : Path of Mount point (default:/mnt)
#      iRAW_Filesystem  : Filesystem (0:ext2, 1:ext3, 2:ext4, default:0)
#
#      sUBIFS_MIN_size  : Page size (string)
#      sUBIFS_LEB_size  : Logical erase block size (string)
#      sUBIFS_MEB_size  : Maximum logical erase block count (string)
#      lUBIFS_MIN_size  : Page size (number)
#      lUBIFS_LEB_size  : Logical erase block size (number)
#      lUBIFS_MEB_size  : Maximum logical erase block count (number)
#      sUBIVOL_ID       : Id of /dev/ubi, for example /dev/ubi0
#      sUBIVOL_NAME     : Vol Name of /dev/ubi
#-----------------------------------------------------------------------------
class MKIMGInfo:

    #------------------------------------------------------------------
    # def __init__()
    #
    #   MKIMGInfo class initialize.
    #
    # Input:
    #   self   : my instance
    #   sFrom  : path of From-directory
    #   sTo    : path of To-directory
    #   sImg   : name of Image-file
    # Output:
    #   None
    #------------------------------------------------------------------
    def __init__(self, iType):
        # Common Parameters for each image
        self.sFrom_dir = ""
        self.sTo_dir   = os.getcwd()
        self.sImg_file = ""
        self.iType      = iType

        # Parameters for Making JFFS2 image
        self.sJFFS2_Img_size  = "10M"
        self.lJFFS2_Img_size  = 0
        self.sJFFS2_Page_size = "4K"
        self.lJFFS2_Page_size = 4096
        self.sJFFS2_Erase_bs  = "64K"
        self.lJFFS2_Erase_bs  = 0
        self.iJFFS2_Endian    = 0

        # Parameters for Making INITRD image
        self.sINITRD_Img_size = ""
        self.lINITRD_Img_size = 0
        self.sINITRD_Loop_dev = DEF_DEFAULT_LOOP_DEVICE
        self.sINITRD_Mount_pt = DEF_DEFAULT_LOOP_MOUNT_POINT

        # Parameters for Making RAW image
        self.sRAW_Img_size = ""
        self.lRAW_Img_size = 0
        self.sRAW_Loop_dev = DEF_DEFAULT_LOOP_DEVICE
        self.sRAW_Mount_pt = DEF_DEFAULT_LOOP_MOUNT_POINT
        self.iRAW_Filesystem = "ext4"

        # Parameters for Squash FS Image
        self.sSquash_Blk_size = "4K"
        self.lSquash_Blk_size = 0

        # Parameters for UBIFS Image
        self.sUBIFS_MIN_size = ""
        self.sUBIFS_LEB_size = ""
        self.sUBIFS_MEB_size = ""
        self.lUBIFS_MIN_size = 0
        self.lUBIFS_LEB_size = 0
        self.lUBIFS_MEB_size = 0
        self.sUBIVOL_ID = "0"
        self.sUBIVOL_NAME = "rootfs"

    #=================================================================
    # SquashFS image
    #=================================================================

    #------------------------------------------------------------------
    # def set_squashfs_param()
    #
    #   Set Parameters for Making SquashFS image.
    #
    # Input:
    #   self       : my instance
    #   sSize      : block size
    # Output:
    #   None
    #------------------------------------------------------------------
    def set_squashfs_param(self, sSize):
        self.sSquash_Blk_size = sSize        # Block size

    #------------------------------------------------------------------
    # def set_squashfs_long_param()
    #
    #   Set Long Type Parameters for Making SquashFS image.
    #
    # Input:
    #   self       : my instance
    # Output:
    #   None
    #------------------------------------------------------------------
    def set_squashfs_long_param(self):
        self.lSquash_Blk_size  = self.change_string_to_decimal(self.sSquash_Blk_size)

    #------------------------------------------------------------------
    # def get_squashfs_param()
    #
    #   Get Parameters for Making SquashFS image.
    #
    # Input:
    #   self       : my instance
    # Output:
    #   str        : block size
    #   long       : block size
    #------------------------------------------------------------------
    def get_squashfs_param(self):
        return (self.sSquash_Blk_size, self.lSquash_Blk_size)

    #------------------------------------------------------------------
    # def check_squashfs_param()
    #
    #   Check Parameters for Making SquashFS image.
    #
    # Input:
    #   self       : my instance
    # Output:
    #   int        : index of error parameter
    #                (success=0, fail=MKIMG_LABEL_BLK_SIZE)
    #------------------------------------------------------------------
    def check_squashfs_param(self):

        # Check Block size (Character and Size)
        err = CheckString(self.sSquash_Blk_size)
        if err != 0:
            return MKIMG_LABEL_BLK_SIZE

        tmp = self.sSquash_Blk_size.lower()
        rcode = CheckDigitHex(tmp)

        if rcode == 10:
            if tmp[-1:] != "k" and tmp[-1:] != "m":
                r = int(tmp, 10) % MKIMG_BLOCK_SIZE
                if r != 0:
                    return MKIMG_LABEL_BLK_SIZE
        elif rcode == 16:
            r = int(tmp, 16) % MKIMG_BLOCK_SIZE
            if r != 0:
                return MKIMG_LABEL_BLK_SIZE

        return 0

    #=================================================================
    # UBIFS image
    #=================================================================

    #------------------------------------------------------------------
    # def set_ubifs_param()
    #
    #   Set Parameters for Making UBIFS image.
    #
    # Input:
    #   self       : my instance
    #   sMin_size  : min size
    #   sLEB_size  : logical erase block size
    #   sMEB_size  : maximam erase block size
    # Output:
    #   None
    #------------------------------------------------------------------
    def set_ubifs_param(self, sMin_size, sLEB_size, sMEB_size, sVOL_ID, sVOL_NAME):
        self.sUBIFS_MIN_size = sMin_size
        self.sUBIFS_LEB_size = sLEB_size
        self.sUBIFS_MEB_size = sMEB_size
        self.sUBIVOL_ID = sVOL_ID
        self.sUBIVOL_NAME = sVOL_NAME

    #------------------------------------------------------------------
    # def set_ubifs_long_param()
    #
    #   Set Long Type Parameters for Making UBIFS image.
    #
    # Input:
    #   self       : my instance
    # Output:
    #   None
    #------------------------------------------------------------------
    def set_ubifs_long_param(self):
        self.lUBIFS_MIN_size = self.change_string_to_decimal(self.sUBIFS_MIN_size)
        self.lUBIFS_LEB_size = self.change_string_to_decimal(self.sUBIFS_LEB_size)
        self.lUBIFS_MEB_size = self.change_string_to_decimal(self.sUBIFS_MEB_size)

    #------------------------------------------------------------------
    # def get_ubifs_param()
    #
    #   Get Parameters for Making UBIFS image.
    #
    # Input:
    #   self       : my instance
    # Output:
    #   str        : min size
    #   long       : min size
    #   str        : logical erase block size
    #   long       : logical erase block size
    #   str        : maximam erase block size
    #   long       : maximam erase block size
    #------------------------------------------------------------------
    def get_ubifs_param(self):
        return (self.sUBIFS_MIN_size, self.lUBIFS_MIN_size, \
                self.sUBIFS_LEB_size, self.lUBIFS_LEB_size, \
                self.sUBIFS_MEB_size, self.lUBIFS_MEB_size, \
                self.sUBIVOL_ID, self.sUBIVOL_NAME)

    #------------------------------------------------------------------
    # def check_ubifs_param()
    #
    #   Check Parameters for Making UBIFS image.
    #
    # Input:
    #   self       : my instance
    # Output:
    #   int        : index of error parameter
    #                (success=0, fail=MKIMG_LABEL_BLK_SIZE)
    #------------------------------------------------------------------
    def check_ubifs_param(self):

        # Check Block size (Character and Size)
        err = CheckString(self.sUBIFS_MIN_size)
        if err != 0:
            return MKIMG_LABEL_BLK_SIZE

        # Check LEB size (Character and Size)
        err = CheckString(self.sUBIFS_LEB_size)
        if err != 0:
            return MKIMG_LABEL_LEB_SIZE

        # Check MEB size (Character and Size)
        err = CheckString(self.sUBIFS_MEB_size)
        if err != 0:
            return MKIMG_LABEL_MEB_SIZE

        # Check vol id (Character and Size)
        err = Check10Chara(self.sUBIVOL_ID)
        if err != 0:
            return MKIMG_LABEL_VOL_ID

        return 0

    #=================================================================
    # Common Parameters
    #=================================================================

    #------------------------------------------------------------------
    # def set_from_dir_path()
    #
    #   Set path of From-directory.
    #
    # Input:
    #   self       : my instance
    #   sFrom_dir  : path of From-directory
    # Output:
    #   None
    #------------------------------------------------------------------
    def set_from_dir_path(self, sFrom_dir):
        self.sFrom_dir = sFrom_dir


    #------------------------------------------------------------------
    # def get_from_dir_path()
    #
    #   Get path of From-directory.
    #
    # Input:
    #   self       : my instance
    # Output:
    #   str        : path of From-directory
    #------------------------------------------------------------------
    def get_from_dir_path(self):
        return self.sFrom_dir


    #------------------------------------------------------------------
    # def get_from_dir_path()
    #
    #   Get path of From-directory.
    #
    # Input:
    #   self       : my instance
    # Output:
    #   int        : err code
    #   str        : err message of From-directory
    #------------------------------------------------------------------
    def check_from_dir_path(self):
        # Check From Directory
        # From-directory path does not exist ?
        if not os.path.exists(self.sFrom_dir):
            err_str = "%s: From-directory does not exist" % self.sFrom_dir
            return (-1, err_str)

        # From-directory path is not directory ?
        if not os.path.isdir(self.sFrom_dir):
            err_str = "%s: From-directory path is not directory" % self.sFrom_dir
            return (-1, err_str)

        # From-directory is empty ?
        list = os.listdir(self.sFrom_dir)
        if len(list) == 0:
            err_str = "%s: From-directory is empty" % self.sFrom_dir
            return (-1, err_str)
        del list

        return (0, "")

    #------------------------------------------------------------------
    # def set_to_dir_path()
    #
    #   Set path of To-directory.
    #
    # Input:
    #   self       : my instance
    #   sTo_dir    : path of To-directory
    # Output:
    #   None
    #------------------------------------------------------------------
    def set_to_dir_path(self, sTo_dir):
        self.sTo_dir = sTo_dir


    #------------------------------------------------------------------
    # def get_to_dir_path()
    #
    #   Get path of To-directory.
    #
    # Input:
    #   self       : my instance
    # Output:
    #   str        : path of To-directory
    #------------------------------------------------------------------
    def get_to_dir_path(self):
        return self.sTo_dir


    #------------------------------------------------------------------
    # def set_image_file_name()
    #
    #   Set name of Image-file.
    #
    # Input:
    #   self       : my instance
    #   sImg_file  : name of Image-file
    # Output:
    #   None
    #------------------------------------------------------------------
    def set_image_file_name(self, sImg_file):
        self.sImg_file = sImg_file


    #------------------------------------------------------------------
    # def get_to_dir_path()
    #
    #   Get name of Image-file.
    #
    # Input:
    #   self       : my instance
    # Output:
    #   str        : name of Image-file
    #------------------------------------------------------------------
    def get_image_file_name(self):
        return self.sImg_file


    #------------------------------------------------------------------
    # def set_image_type()
    #
    #   Set Image type.
    #
    # Input:
    #   self       : my instance
    #   iType      : image type number
    #                (0:JFFS2, 1:INITRAMFS, 2:INITRD, 3:RAW)
    # Output:
    #   None
    #------------------------------------------------------------------
    def set_image_type(self, iType):
        self.iType = iType


    #------------------------------------------------------------------
    # def get_image_type()
    #
    #   Get Image type.
    #
    # Input:
    #   self       : my instance
    # Output:
    #   int        : image type number
    #                (0:JFFS2, 1:INITRAMFS, 2:INITRD, 3:RAW)
    #------------------------------------------------------------------
    def get_image_type(self):
        return self.iType


    #=================================================================
    # JFFS2 image
    #=================================================================

    #------------------------------------------------------------------
    # def set_jffs2_param()
    #
    #   Set Parameters for Making JFF2 image.
    #
    # Input:
    #   self       : my instance
    #   sSize      : image size
    #   sPage      : page size
    #   sErase     : erase block size
    #   iEndian    : endian
    #                (0:Little endian, 1:Bigendian)
    # Output:
    #   None
    #------------------------------------------------------------------
    def set_jffs2_param(self, sSize, sPage, sErase, iEndian):
        self.sJFFS2_Img_size  = sSize    # Image size
        self.sJFFS2_Page_size = sPage    # Page size (default:4K)
        self.sJFFS2_Erase_bs  = sErase   # Erase block size
        self.iJFFS2_Endian    = iEndian  # Endian (0:Little, 1:Big)

    #------------------------------------------------------------------
    # def set_jffs2_long_param()
    #
    #   Set Long Type Parameters for Making JFF2 image.
    #
    # Input:
    #   self       : my instance
    # Output:
    #   None
    #------------------------------------------------------------------
    def set_jffs2_long_param(self):
        self.lJFFS2_Img_size  = self.change_string_to_decimal(self.sJFFS2_Img_size)
        self.lJFFS2_Page_size = self.change_string_to_decimal(self.sJFFS2_Page_size)
        self.lJFFS2_Erase_bs  = self.change_string_to_decimal(self.sJFFS2_Erase_bs)

    #------------------------------------------------------------------
    # def get_jffs2_param()
    #
    #   Get Parameters for Making JFF2 image.
    #
    # Input:
    #   self       : my instance
    # Output:
    #   str        : image size
    #   long       : image size
    #   str        : page size
    #   long       : page size
    #   str        : erase block size
    #   long       : erase block size
    #   int        : endian
    #                (0:Little endian, 1:Bigendian)
    #------------------------------------------------------------------
    def get_jffs2_param(self):
        return (self.sJFFS2_Img_size,  self.lJFFS2_Img_size, \
                self.sJFFS2_Page_size, self.lJFFS2_Page_size, \
                self.sJFFS2_Erase_bs,  self.lJFFS2_Erase_bs, \
                self.iJFFS2_Endian)


    #------------------------------------------------------------------
    # def check_jffs2_param()
    #
    #   Check Parameters for Making JFF2 image.
    #
    # Input:
    #   self       : my instance
    # Output:
    #   int        : index of error parameter
    #                (success=0, fail=MKIMG_LABEL_IMG_SIZE,
    #                                 MKIMG_LABEL_PAGE_SIZE,
    #                                 MKIMG_LABEL_ERASE_BS)
    #------------------------------------------------------------------
    def check_jffs2_param(self):

        # Check Image size (Character and Size)
        err = CheckString(self.sJFFS2_Img_size)
        if err != 0:
            return MKIMG_LABEL_IMG_SIZE

        tmp = self.sJFFS2_Img_size.lower()
        rcode = CheckDigitHex(tmp)

        if rcode == 10:
            if tmp[-1:] != "k" and tmp[-1:] != "m":
                r = int(tmp, 10) % MKIMG_BLOCK_SIZE
                if r != 0:
                    return MKIMG_LABEL_IMG_SIZE
        elif rcode == 16:
            r = int(tmp, 16) % MKIMG_BLOCK_SIZE
            if r != 0:
                return MKIMG_LABEL_IMG_SIZE

        # Check Page size (Character)
        err = CheckString(self.sJFFS2_Page_size)
        if err != 0:
            return MKIMG_LABEL_PAGE_SIZE

        # Check Erase block size (Character)
        err = CheckString(self.sJFFS2_Erase_bs)
        if err != 0:
            return MKIMG_LABEL_ERASE_BS

        return 0


    #=================================================================
    # INITRD image
    #=================================================================

    #------------------------------------------------------------------
    # def set_initrd_param()
    #
    #   Set Parameters for Making INITRD image.
    #
    # Input:
    #   self       : my instance
    #   sSize      : image size
    #   sLoop      : path of loop device
    #   sMount     : path of mount point
    # Output:
    #   None
    #------------------------------------------------------------------
    def set_initrd_param(self, sSize, sLoop, sMount):
        self.sINITRD_Img_size = sSize   # Image size
        self.sINITRD_Loop_dev = sLoop   # Path of Loop device
        self.sINITRD_Mount_pt = sMount  # Path of Mount point


    #------------------------------------------------------------------
    # def set_initrd_long_param()
    #
    #   Set Long Type Parameters for Making INITRD image.
    #
    # Input:
    #   self       : my instance
    # Output:
    #   None
    #------------------------------------------------------------------
    def set_initrd_long_param(self):
        self.lINITRD_Img_size  = self.change_string_to_decimal(self.sINITRD_Img_size)


    #------------------------------------------------------------------
    # def get_initrd_param()
    #
    #   Get Parameters for Making INITRD image.
    #
    # Input:
    #   self       : my instance
    # Output:
    #   str        : image size
    #   long       : image size
    #   str        : path of loop device
    #   str        : path of mount point
    #------------------------------------------------------------------
    def get_initrd_param(self):
        return (self.sINITRD_Img_size, self.lINITRD_Img_size, \
                self.sINITRD_Loop_dev, self.sINITRD_Mount_pt)


    #------------------------------------------------------------------
    # def check_initrd_param()
    #
    #   Check Parameters for Making INITRD image.
    #
    # Input:
    #   self       : my instance
    # Output:
    #   int        : index of error parameter
    #                (success=0, fail=MKIMG_LABEL_IMG_SIZE,
    #                                 MKIMG_LABEL_LOOP_DEV,
    #                                 MKIMG_LABEL_MOUNT_PT)
    #------------------------------------------------------------------
    def check_initrd_param(self):

        # Check Image size (Character and Size)
        err = CheckString(self.sINITRD_Img_size)
        if err != 0:
            return MKIMG_LABEL_IMG_SIZE

        tmp = self.sINITRD_Img_size.lower()
        rcode = CheckDigitHex(tmp)

        if rcode == 10:
            if tmp[-1:] != "k" and tmp[-1:] != "m":
                r = int(tmp, 10) % MKIMG_BLOCK_SIZE
                if r != 0:
                    return MKIMG_LABEL_IMG_SIZE
        elif rcode == 16:
            r = int(tmp, 16) % MKIMG_BLOCK_SIZE
            if r != 0:
                return MKIMG_LABEL_IMG_SIZE

        # Check Loop device (exist)
        if not os.path.exists(self.sINITRD_Loop_dev):
            return MKIMG_LABEL_LOOP_DEV

        # Check Mount point (dir)
        if not os.path.isdir(self.sINITRD_Mount_pt):
            return MKIMG_LABEL_MOUNT_PT

        return 0


    #=================================================================
    # RAW image
    #=================================================================

    #------------------------------------------------------------------
    # def set_raw_param()
    #
    #   Set Parameters for Making RAW image.
    #
    # Input:
    #   self       : my instance
    #   sSize      : image size
    #   sLoop      : path of loop device
    #   sMount     : path of mount point
    #   iFilesystem: filesystem
    #                (0:ext2, 1:ext3, 2:ext4)
    # Output:
    #   None
    #------------------------------------------------------------------
    def set_raw_param(self, sSize, sLoop, sMount, iFilesystem):
        self.sRAW_Img_size = sSize           # Image size
        self.sRAW_Loop_dev = sLoop           # Path of Loop device
        self.sRAW_Mount_pt = sMount          # Path of Mount point
        self.iRAW_Filesystem  = iFilesystem  # Filesystem (0:ext2, 1:ext3, 2:ext4)


    #------------------------------------------------------------------
    # def set_raw_long_param()
    #
    #   Set Long Type Parameters for Making RAW image.
    #
    # Input:
    #   self       : my instance
    # Output:
    #   None
    #------------------------------------------------------------------
    def set_raw_long_param(self):
        self.lRAW_Img_size  = self.change_string_to_decimal(self.sRAW_Img_size)


    #------------------------------------------------------------------
    # def get_raw_param()
    #
    #   Get Parameters for Making RAW image.
    #
    # Input:
    #   self       : my instance
    # Output:
    #   str        : image size
    #   long       : image size
    #   str        : path of loop device
    #   str        : path of mount point
    #   int        : filesystem
    #                (0:ext2, 1:ext3, 2:ext4)
    #------------------------------------------------------------------
    def get_raw_param(self):
        return (self.sRAW_Img_size, self.lRAW_Img_size, \
                self.sRAW_Loop_dev, self.sRAW_Mount_pt, self.iRAW_Filesystem)


    #------------------------------------------------------------------
    # def check_raw_param()
    #
    #   Check Parameters for Making RAW image.
    #
    # Input:
    #   self       : my instance
    # Output:
    #   int        : index of error parameter
    #                (success=0, fail=MKIMG_LABEL_IMG_SIZE,
    #                                 MKIMG_LABEL_LOOP_DEV,
    #                                 MKIMG_LABEL_MOUNT_PT)
    #------------------------------------------------------------------
    def check_raw_param(self):

        # Check Image size (Character and Size)
        err = CheckString(self.sRAW_Img_size)
        if err != 0:
            return MKIMG_LABEL_IMG_SIZE

        tmp = self.sRAW_Img_size.lower()
        rcode = CheckDigitHex(tmp)

        if rcode == 10:
            if tmp[-1:] != "k" and tmp[-1:] != "m":
                r = int(tmp, 10) % MKIMG_BLOCK_SIZE
                if r != 0:
                    return MKIMG_LABEL_IMG_SIZE
        elif rcode == 16:
            r = int(tmp, 16) % MKIMG_BLOCK_SIZE
            if r != 0:
                return MKIMG_LABEL_IMG_SIZE

        # Check Loop device (exist)
        if not os.path.exists(self.sRAW_Loop_dev):
            return MKIMG_LABEL_LOOP_DEV

        # Check Mount point (dir)
        if not os.path.isdir(self.sRAW_Mount_pt):
            return MKIMG_LABEL_MOUNT_PT

        return 0

    #=================================================================
    # Common Module
    #=================================================================

    #------------------------------------------------------------------
    # def change_string_to_decimal()
    #
    #   Change String Parameter to decimal.
    #
    # Input:
    #   self       : my instance
    #   sSize      : string
    # Output:
    #   long       : decimal number
    #------------------------------------------------------------------
    def change_string_to_decimal(self, sSize):
        tmp = sSize.lower()

        code = CheckDigitHex(tmp)

        if code == 10:
            if tmp[-1:] == "m":
                size = int(tmp[:-1]) * 1024 * 1024
            elif tmp[-1:] == "k":
                size = int(tmp[:-1]) * 1024
            else:
                size = int(tmp, 10)
        elif code == 16:
            size = int(tmp, 16)

        return size
