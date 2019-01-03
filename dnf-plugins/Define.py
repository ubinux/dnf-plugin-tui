#!/usr/bin/python

#
# Copyright (C) Fujitsu Limited 2018  All rights reserved
#

#==================================================
# for tui
#==================================================
_TXT_ROOT_TITLE = "Package Installer"

#Install actions list
#Install_actions[type][0]  :  menu item
#Install_actions[type][1]  :  Help information
#Install_actions[type][2]  :  Title information (optional)
Install_actions = [("Install", "Choose it to install packages.", "About Install"), \
                   ("Remove", "Choose it to remove packages.", "About Remove"), \
                   ("Upgrade", "Choose it to upgrade packages.", "About Upgrade"), \
                   ("Create binary package archive", "To create an archive that includes packages for installed packages."), \
                   ("Create source archive", "To create an archive that includes source packages for installed packages."), \
                   ("Create SPDX archive", "To create an archive that includes SPDX files for installed packages."), \
                   ("Create archive(rpm, src.rpm and spdx files)", "To create an archive that includes packages, source packages and SPDX files for installed packages."), \

                   ("Make filesystem image", "To make different kinds of filesystem image for root filesystem.", "About filesystem image")
                  ]

#When you choose install, list for custom install actions
Custom_actions = [("New", "Install without package list file."), \
                  ("Load package list file", "Load package list file")
                  ]

#Make image type list
#Image_types[type][0]  :  menu item
#Image_types[type][1]  :  Help information
#Image_types[type][2]  :  Title information (optional)
Image_types    = [("JFFS2", "Journalling Flash File System version 2.", "About JFFS2"), \
                  ("INITRAMFS", "Initial ramdisk.", "About INITRAMFS"), \
                  ("INITRD", "Linux initial RAM disk.", "About INITRD"), \
                  ("RAW", "Keep the image file as the original filesystem type.", "About RAW"), \
                  ("SquashFS", "A compressed read-only file system for Linux.", "About SquashFS"), \
                  ("UBIFS", "Unsorted Block Image File System.", "About UBIFS")
#                  ("Cramfs", "Compressed ROM file system.", "About Cramfs")
                  ]

#==================================================
# for Image Maker
#==================================================

### default loop device
DEF_DEFAULT_LOOP_DEVICE       = "/dev/loop0"
DEF_DEFAULT_LOOP_MOUNT_POINT  = "/mnt"
