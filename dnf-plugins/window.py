#encoding=utf-8 
#
# Copyright (C) 2016 FUJITSU LIMITED
#
import sys, os, copy, textwrap, snack, string, time, re
from snack import * 
from dnf.cli.format import *

ACTION_INSTALL    = 0
ACTION_REMOVE     = 1
ACTION_UPGRADE    = 2
ACTION_GET_PKG    = 3
ACTION_GET_SOURCE = 4
ACTION_GET_SPDX   = 5
ACTION_GET_SPDX   = 6


Confirm_type_list = [("Exit","\n Do you really want to terminate it?\n\n"), \
                     ("Confirm install","\n Do you want to begin installation?\n\n"), \
                     ("License","\n Do you want to display GPLv3 packages?\n\n"), \
                     ("Confirm remove","\n Do you want to begin removing?\n\n"), \
                     ("Confirm upgrade","\n Do you want to begin upgrading?\n\n"), \
                     ("Confirm get package","\n Begin getting package archive?\n\n"), \
                     ("Confirm get source","\n Begin getting source archive?\n\n"), \
                     ("Confirm get SPDX","\n Begin getting SPDX archive?\n\n"), \
                     ("Confirm get ALL","\n Begin getting all archive?\n\n") \
                     ]

Attention_type_list=[("Attention!","\n You must installed some packages first!\n\n"), \
                     ("Attention!","Have some advanced version packages.\nShow installed only!\n\
You can enter 'upgrade' scene to upgrade \ninstalled packages.\n"), \
                     ("Attention!","\n There is no package to be upgraded!\n\n") \
                     ]

SIGN_SELECT=["*", "-", "U", "R", "S", "S", "A"]

class pkgType:
    name = None
    status = None
    description = None

    def __init__(self, type, status, desc):
        self.name = type
        self.status = False
        self.description = desc

#------------------------------------------------------------
# def GetWindowSize()
#
#   Get Window size.
#
# Input:
#   insScreen : screen instance
# Output:
#   int       : window height
#   int       : window width
#------------------------------------------------------------
def GetWindowSize(insScreen):
    return (insScreen.width, insScreen.height)

#------------------------------------------------------------
# def GetHotkeyMainSize()
#
#   Get best full screen main object size for HotKey mode
#
# Input:
#   insScreen : screen instance
# Output:
#   int       : width
#   int       : height
#------------------------------------------------------------
def GetHotKeyMainSize(insScreen):
    (width, height) = GetWindowSize(insScreen)

    width -= 8

    # It is not centered well only by doing -9 when the Height is an Odd.
    # In addition, it is necessary to do 1.
    height -= (9 - (height % 2))

    return (width, height)
#------------------------------------------------------------
# def _StatusToggle(insLi, sHkey, iIdx, selected_packages, packages, install_type)
#
#   package select window, "selection" function.
#
# Input:
#    insLi              : instance of Listbox
#    sHkey              : hotkey selected
#    iIdx               : index selected
#    selected_packages  : selected_package
#    packages           : display packages
#    install_type       :INSTALL or REMOVE or UPDATE
# Output:
#    packages : showed packages
#------------------------------------------------------------

def _StatusToggle(insLi, sHkey, iIdx, selected_packages, packages, install_type):
    pkg = packages[iIdx]
    #print "select package : %s " % pkg.name
    if sHkey == " " or sHkey == "ENTER":
        if install_type == ACTION_INSTALL and (not pkg.installed):
            if pkg in selected_packages:
                selected_packages.remove(pkg)
                newsign = " "
            else:
                selected_packages.append(pkg)
                newsign = SIGN_SELECT[install_type]
        elif not install_type == ACTION_INSTALL:
            if pkg in selected_packages:
                selected_packages.remove(pkg)
                newsign = " "
            else:
                selected_packages.append(pkg)
                newsign = SIGN_SELECT[install_type]
        else:
            return insLi
    item = "[%s] %s" % (newsign, pkg.name)
    insLi.replace(item, iIdx)
    return insLi
#------------------------------------------------------------
# def _SelectAll(insLi, sHkey,numPackage,selected_packages, packages, install_type))
#
#   package select window, "select all" function.
#
# Input:
#    insLi             : instance of Listbox
#    sHkey             : hotkey selected
#    numPackage        : number of showed packages
#    selected_packages : selected_package
#    packages          : showed packages
#    install_type      : INSTALL or REMOVE or UPDATE
# Output:
#    insLi :changed instance of Listbox
#------------------------------------------------------------
def _SelectAll(insLi, sHkey, numPackage, selected_packages, packages, \
                                                       install_type):
    haveSelected=False      
    for pkg in packages:
        if (not pkg in selected_packages) and ((install_type==ACTION_INSTALL and (not pkg.installed))or \
                                                                    not install_type==ACTION_INSTALL):
            haveSelected=True
            break

#replace sign in list

    if install_type == ACTION_INSTALL:
        if haveSelected :
            for iIdx in range(0,numPackage):
                pkg=packages[iIdx]
                if (not pkg in selected_packages) and (not pkg.installed):
                    selected_packages.append(pkg)
                    item = "[%s] %s" % (SIGN_SELECT[install_type], pkg.name)
                    insLi.replace(item,iIdx)
        else:
            for iIdx in range(0,numPackage):
                pkg=packages[iIdx]
                if (pkg in selected_packages) and (not pkg.installed):
                    selected_packages.remove(pkg)
                    item = "[%s] %s" % (" ", pkg.name)
                    insLi.replace(item,iIdx)

    else:
        if haveSelected :
            for iIdx in range(0,numPackage):
                pkg=packages[iIdx]
                if not pkg in selected_packages:
                    selected_packages.append(pkg)
                    item = "[%s] %s" % (SIGN_SELECT[install_type], pkg.name)
                    insLi.replace(item,iIdx)
        else:
            for iIdx in range(0,numPackage):
                pkg=packages[iIdx]
                if pkg in selected_packages:
                    selected_packages.remove(pkg)
                    item = "[%s] %s" % (" ", pkg.name)
                    insLi.replace(item,iIdx)

    return insLi

#_SelectAll


#------------------------------------------------------------
# def StartHotkeyScreen()
#
#   Setup snack's screen and hotkey dict for Hotkey mode.
#
# Input:
#   sText : root text
# Output:
#   ins   : screen instance
#------------------------------------------------------------
def StartHotkeyScreen(sText):

    # Set screen mode
    os.environ['NEWT_MONO'] = "1"
    env_term = os.getenv("TERM").upper()
    if env_term == "VT100":
        print ("\x1b[?25l")  # cursor off

    # Setup hotkey dictionary
    for x in string.ascii_letters:
        snack.hotkeys[x] = ord(x)
        snack.hotkeys[ord(x)] = x
    snack.hotkeys["ENTER"] = 0x0d
    snack.hotkeys[0x0d] = "ENTER"
    snack.hotkeys["PD"] = 0x800c
    snack.hotkeys[0x800c] = "PD"


    # Start snack's screen
    screen = snack.SnackScreen()

    #obtain the width  of screen to calculate the left value for drawRootText=
    (width, height) = GetWindowSize(screen)
    Left_Length = (width - len(sText))/2

    screen.drawRootText(int(Left_Length), 0, sText)
    screen.pushHelpLine(" ")
      
    # Window size check
    if width < 80 or height < 24:
        StopHotkeyScreen(screen)
        screen = None
        print ("Your screen is too small! It must be at least 24 lines by 80 columns!")

    return screen

#------------------------------------------------------------
# def HotkeyExitWindow(insScreen, confirm_install=False)
#
#   Display "Exit" window and exit for Hotkey mode.
#
# Input:
#   insScreen : screen instance
#   confirm_install=False : just exit without install
#   confirm_install=False : just exit and begin to install
# Output:
#   int       : "y" or "n"
#------------------------------------------------------------
def HotkeyExitWindow(insScreen, confirm_type=0):

    # Display Exit Window
    myhotkeys = {"Y" : "y", \
                 "y" : "y", \
                 "N" : "n", \
                 "n" : "n"}
    
    result = HotkeyInfoButtonWindow(insScreen, Confirm_type_list[confirm_type][0], \
                 Confirm_type_list[confirm_type][1], \
                 40, 4, myhotkeys, "Y:yes  N:no")

    return result


# ------------------------------------------------------------
# def HotkeyAttentionWindow(insScreen, confirm_install=False)
#
#   Display "Attention" window .
#
# Input:
#   insScreen : screen instance
#   attention_type: index of  attention text list
# Output:
#   int       : "ok"
# ------------------------------------------------------------
def HotkeyAttentionWindow(insScreen, attention_type):
    # Display Exit Window
    myhotkeys = {"ENTER": "y", \
                 " ": "y" \
                }

    result = HotkeyInfoWindow(insScreen, Attention_type_list[attention_type][0], \
                              Attention_type_list[attention_type][1], \
                              40, 4, myhotkeys, "Enter/Space:OK")

    return result


#------------------------------------------------------------
# def StopHotkeyScreen()
#
#   Finish snack's screen
#
# Input:
#   insScreen : screen instance
# Output:
#   None
#------------------------------------------------------------
def StopHotkeyScreen(insScreen):

    # Finish Snack's screen
    insScreen.finish()

    # Resume screen mode
    env_term = os.getenv("TERM").upper()
    if env_term == "VT100":
        print ("\x1b[?25h")  # cursor on

#------------------------------------------------------------
# def HotkeyInfoWindow()
#
#   Display information window for Hotkey mode.
#
# Input:
#   insScreen             : screen instance
#   sTitle                : title string
#   sText                 : main text
#   iWidth                : width of main text
#   iHeight               : height of main text
#   dctHotkeys{str : srr} : Hotkey dictionary
#                           [hotkey string, rtncode]
#   sHtext                : Hotkey information text
# Output:
#   str : rtncode in Hotkey dictionary
#------------------------------------------------------------
def HotkeyInfoWindow(insScreen, sTitle, sText, iWidth, iHeight, \
                     dctHotkeys, sHtext):

    # Get line number
    length = len(sText)
    index = 0
    count = 0
    scroll = 0
    while index < length:
        if sText[index] == "\n":
            count += 1
            if count > iHeight:
                scroll = 1
                break
        index += 1

    # Create Text instance
    t1 = snack.Textbox(iWidth - scroll * 2, iHeight, sText, scroll)
    t2 = snack.Textbox(iWidth, 1, "-" * iWidth)
    t3 = snack.Textbox(iWidth, 1, sHtext)

    # Create Grid instance
    g = snack.GridForm(insScreen, sTitle, 1, 3)
    g.add(t1, 0, 0)

    insScreen.pushHelpLine("  "+sHtext)

    for x in dctHotkeys.keys():
        g.addHotKey(x)
    # Display window
    while True:
        result = g.run()
        if result in dctHotkeys:
            break

    # Return
    insScreen.popHelpLine()
    insScreen.popWindow()
    return dctHotkeys[result]

#------------------------------------------------------------
# def HotkeyInfoButtonWindow()
#
#   Display information window for Hotkey mode.
#
# Input:
#   insScreen             : screen instance
#   sTitle                : title string
#   sText                 : main text
#   iWidth                : width of main text
#   iHeight               : height of main text
#   dctHotkeys{str : srr} : Hotkey dictionary
#                           [hotkey string, rtncode]
#   sHtext                : Hotkey information text
# Output:
#   str : rtncode in Hotkey dictionary
#------------------------------------------------------------
def HotkeyInfoButtonWindow(insScreen, sTitle, sText, iWidth, iHeight, \
                     dctHotkeys, sHtext):

    # Get line number
    length = len(sText)
    index = 0
    count = 0
    scroll = 0
    while index < length:
        if sText[index] == "\n":
            count += 1
            if count > iHeight:
                scroll = 1
                break
        index += 1

    # Create Text instance
    t1 = snack.Textbox(iWidth - scroll * 2, iHeight, sText, scroll)
    t2 = snack.Textbox(iWidth, 1, "-" * iWidth)
    t3 = snack.Textbox(iWidth, 1, sHtext)

    b = snack.ButtonBar(insScreen,((" Yes ", "y"), (" No ", "n")))

    # Create Grid instance
    g = snack.GridForm(insScreen, sTitle, 1, 4)
    g.add(t1, 0, 0)
    g.add(t2, 0, 1, (-1, 0, -1, 0))
    g.add(b, 0, 2, (1, 0, 1, -1))

    # Display window
    result = g.run()

    # Return
    insScreen.popWindow()
    
    if b.buttonPressed(result) == "y":
       return 'y'
    elif b.buttonPressed(result) == "n":
       return 'n'

#------------------------------------------------------------
# def PKGINSTTypeInfoWindow()
#
#   Display install type information window.
#
# Input:
#   insScreen    : screen instance
#   sSubject     : install type subject
#   sDescription : description about the install type
#   Infotitle    : description of title
# Output:
#   None
#------------------------------------------------------------
def PKGINSTTypeInfoWindow(insScreen, sSubject, sDescription, titleDescription="Install type information"):

    # Create Main Text
    (main_width, main_height) = GetHotKeyMainSize(insScreen)

    wrapper = textwrap.TextWrapper(width = main_width - 2)

    wrapper.initial_indent    = ""
    wrapper.subsequent_indent = ""
    main_text = wrapper.fill("[ %s ]" % sSubject) + "\n"

    wrapper.initial_indent    = "  "
    wrapper.subsequent_indent = "  "
    main_text += (wrapper.fill(sDescription) + "\n\n")

    # Display information window
    HotkeyInfoWindow(insScreen, titleDescription, main_text, \
                     main_width, main_height, {"F4" : "b"}, "F4:Back")

#------------------------------------------------------------
# def PKGINSTTypeWindowCtrl()
#
#    Select install type
#
# Input:
#    insScreen         : screen instance
#    insPKGINSTXmlinfo : xml information
#    insPKGINSTPkginfo : package information
#    iType             : select type (first -1)
#
# Output:
#    int  : select type
#------------------------------------------------------------
def PKGINSTTypeWindowCtrl(insScreen, lstSubject, iType):

    type = iType

    while True:
        (hkey, type) = PKGINSTTypeWindow(insScreen, lstSubject, type)

        if hkey == "ENTER" or hkey == " ":
            # select/unselect
            return type

        elif hkey == "i":
            # info
            description = lstSubject[type][1]
            subject = lstSubject[type][0]
            PKGINSTTypeInfoWindow(insScreen, subject, description)

        elif hkey == "x":
            # exit
            exit_hkey = HotkeyExitWindow(insScreen)
            if exit_hkey == "y":
                if insScreen != None:
                    StopHotkeyScreen(insScreen)
                    insScreen = None
                sys.exit(0)

#------------------------------------------------------------
# def PKGINSTTypeWindow()
#
#   Display install type select window.
#
# Input:
#   insScreen  : screen instance
#   lstSubject : install type subject list
#      [ str ]
#        str : subject of each install type
#   iPosition  : current entry position
# Output:
#   str   : pressed hotkey "ENTER", " ", "i", or "x"
#   int   : position
#------------------------------------------------------------
def PKGINSTTypeWindow(insScreen, lstSubject, iPosition):

    # Create CheckboxTree instance
    (main_width, main_height) = GetHotKeyMainSize(insScreen)

    if len(lstSubject) > main_height:
        scroll = 1
    else:
        scroll = 0

    li = snack.Listbox(main_height, scroll = scroll, width = main_width)

    idx = 0
    for idx in range(len(lstSubject)):
        str = "%s" % lstSubject[idx][0]
        li.append(str+"  --->", idx)

    num_subject = len(lstSubject)
    if num_subject > iPosition:
        li.setCurrent(iPosition)
    else:
        li.setCurrent(num_subject - 1)
    # Create Text instance
    t1 = snack.Textbox(main_width, 1, "-" * main_width)
    text = "  F5:Info  F9:Exit"
    t2 = snack.Textbox(main_width, 1, text)

    # Create Grid instance
    g = snack.GridForm(insScreen, "Select install type", 1, 3)
    g.add(li, 0, 0)
    g.add(t1, 0, 1, (-1, 0, -1, 0))
    g.add(t2, 0, 2, (0, 0, 0, -1))

    myhotkeys = {"ENTER" : "ENTER", \
                 " "     : " ", \
                 "F5"     : "i", \
                 "F9"     : "x"}
    for x in myhotkeys.keys():
        g.addHotKey(x)

    # Display window
    while True:
        result = g.run()
        if result in myhotkeys:
            idx = li.current()
            break

    insScreen.popWindow()
    return (myhotkeys[result], idx)
#------------------------------------------------------------
# def PKGINSTActionWindowCtrl()
#
#    Select install type
#
# Input:
#    insScreen         : screen instance
#    insPKGINSTXmlinfo : xml information
#    insPKGINSTPkginfo : package information
#    iType             : select type (first -1)
#    title             : title of grid, transmit to PKGINSTActionWindow
#
# Output:
#    int  : select type
#------------------------------------------------------------
def PKGINSTActionWindowCtrl(insScreen, lstSubject, iType, title=None):

    type = iType

    while True:
        if title:
            (hkey, type) = PKGINSTActionWindow(insScreen, lstSubject, type, title)
        else:
            (hkey, type) = PKGINSTActionWindow(insScreen, lstSubject, type)

        if hkey == "ENTER" or hkey == " ":
            # select/unselect
            return type

        elif hkey == "i":
            # info
            description = lstSubject[type][1]
            subject = lstSubject[type][0]
            if len(lstSubject[type])>2:
                #if title is userdefined, show it
                PKGINSTTypeInfoWindow(insScreen, subject, description, lstSubject[type][2])
            else:
                PKGINSTTypeInfoWindow(insScreen, subject, description)

        elif hkey == "x":
            # exit
            exit_hkey = HotkeyExitWindow(insScreen)
            if exit_hkey == "y":
                if insScreen != None:
                    StopHotkeyScreen(insScreen)
                    insScreen = None
                sys.exit(0)

#------------------------------------------------------------
# def PKGINSTActionWindow()
#
#   Display action select window.
#
# Input:
#   insScreen  : screen instance
#   lstSubject : install type subject list
#      [ str ]
#        str : subject of each install type
#   iPosition  : current entry position
#   title             : title of grid
# Output:
#   str   : pressed hotkey "ENTER", " ", "i", or "x"
#   int   : position
#------------------------------------------------------------
def PKGINSTActionWindow(insScreen, lstSubject, iPosition, title="Select your operation"):

    # Create CheckboxTree instance
    (main_width, main_height) = GetHotKeyMainSize(insScreen)

    if len(lstSubject) > main_height:
        scroll = 1
    else:
        scroll = 0

    li = snack.Listbox(main_height, scroll = scroll, width = main_width)

    idx = 0
    for idx in range(len(lstSubject)):
        str = "%s" % lstSubject[idx][0]
        li.append(str+"  --->", idx)

    num_subject = len(lstSubject)
    if num_subject > iPosition:
        li.setCurrent(iPosition)
    else:
        li.setCurrent(num_subject - 1)
    # Create Text instance
    t1 = snack.Textbox(main_width, 1, "-" * main_width)
    text = "  F5:Info  F9:Exit" + "\n Fffff"
    t2 = snack.Textbox(main_width, 1, text)

    # Create Grid instance
    g = snack.GridFormHelp(insScreen, title, "F1", 1, 5)
    insScreen.pushHelpLine(text)
    g.add(li, 0, 0, (0, 0, 0, 0))

    myhotkeys = {"ENTER" : "ENTER", \
                 " "     : " ", \
                 "F5"     : "i", \
                 "F9"     : "x"}
    for x in myhotkeys.keys():
        g.addHotKey(x)

    # Display window
    while True:
        result = g.run()
        if result in myhotkeys:
            idx = li.current()
            break

    #return
    insScreen.popHelpLine()
    insScreen.popWindow()
    return (myhotkeys[result], idx)

# ------------------------------------------------------------
# def PKGCUSActionWindowCtrl()
#
#    Select install type
#
# Input:
#    insScreen         : screen instance
#    insPKGINSTXmlinfo : xml information
#    insPKGINSTPkginfo : package information
#    iType             : select type (first -1)
#    group_hotkey      : group_hotkey
#    title             : title of grid
# Output:
#    int  : select type
# ------------------------------------------------------------
def PKGCUSActionWindowCtrl(insScreen, lstSubject, iType, group_hotkey=False, title=None):

    type = iType

    while True:
        if title:
            (hkey, type) = PKGCUSActionWindow(insScreen, lstSubject, type, group_hotkey, title)
        else:
            (hkey, type) = PKGCUSActionWindow(insScreen, lstSubject, type, group_hotkey)

        if hkey == "b" :
            # back
            return (hkey, type)

        if hkey == "ENTER" or hkey == " ":
            # select/unselect
            return (hkey, type)

        elif hkey == "i":
            # info
            description = lstSubject[type][1]
            subject = lstSubject[type][0]
            if len(lstSubject[type])>2:
                #if title is userdefined, show it
                PKGINSTTypeInfoWindow(insScreen, subject, description, lstSubject[type][2])
            else:
                PKGINSTTypeInfoWindow(insScreen, subject, description)

        elif hkey == "x":
            # exit
            exit_hkey = HotkeyExitWindow(insScreen)
            if exit_hkey == "y":
                if insScreen != None:
                    StopHotkeyScreen(insScreen)
                    insScreen = None
                sys.exit(0)
      
        if group_hotkey == True:
            if hkey == "g":
                # groupinfo switch
                return (hkey, type)


# ------------------------------------------------------------
# def PKGCUSActionWindow()
#
#   Display action select window.
#
# Input:
#   insScreen  : screen instance
#   lstSubject : install type subject list
#      [ str ]
#        str : subject of each install type
#   iPosition  : current entry position
#   group_hotkey  : show group_hotkey
#   title             : title of grid
# Output:
#   str   : pressed hotkey "ENTER", " ", "i", or "x"
#   int   : position
# ------------------------------------------------------------
def PKGCUSActionWindow(insScreen, lstSubject, iPosition, group_hotkey=False, title="Select install type"):

    # Create CheckboxTree instance
    (main_width, main_height) = GetHotKeyMainSize(insScreen)

    if len(lstSubject) > main_height:
        scroll = 1
    else:
        scroll = 0

    li = snack.Listbox(main_height, scroll=scroll, width=main_width)

    idx = 0
    for idx in range(len(lstSubject)):
        str = "%s" % lstSubject[idx][0]
        li.append(str+"  --->", idx)

    num_subject = len(lstSubject)
    if num_subject > iPosition:
        li.setCurrent(iPosition)
    else:
        li.setCurrent(num_subject - 1)
    # Create Text instance
    t1 = snack.Textbox(main_width, 1, "-" * main_width)
    if group_hotkey == True:
        text = "  F4:Back  F5:Info  F6:Group  F9:Exit"
        g = snack.GridForm(insScreen, "Select group", 1, 3)
    else:
        text = "  F4:Back  F5:Info  F9:Exit"
        g = snack.GridForm(insScreen, title, 1, 3)

    t2 = snack.Textbox(main_width, 1, text)

    #insScreen.pushHelpLine(" ")
    insScreen.pushHelpLine(text)
    # Create Grid instance
    g.add(li, 0, 0)
    #g.add(t1, 0, 1, (-1, 0, -1, 0))
    #g.add(t2, 0, 2, (0, 0, 0, -1))

    myhotkeys = {"ENTER": "ENTER", \
                 " ": " ", \
                 "F5": "i", \
                 "F9": "x", \
                 "F4": "b"}

    #If group exists, add group_hotkey
    if group_hotkey == True:
        myhotkeys["F6"] = "g"

    for x in myhotkeys.keys():
        g.addHotKey(x)

    # Display window
    while True:
        result = g.run()
        if result in myhotkeys:
            idx = li.current()
            break

    #return
    insScreen.popHelpLine()
    insScreen.popWindow()
    return (myhotkeys[result], idx)

#------------------------------------------------------------
# def PKGINSTPackageInfoWindow()
#
#   Display install package information window.
#
# Input:
#   insScreen            : screen instance
#   pkg               : selected package info list
#     [str, str, str, long, str, str, [str]]
#       str  : name
#       str  : version
#       str  : release
#       long : size
#       str  : licence
#       str  : summary
#       str  : description
# Output:
#   None
#------------------------------------------------------------
def PKGINSTPackageInfoWindow(insScreen, pkg):
    # Create Main Text
    (main_width, main_height) = GetHotKeyMainSize(insScreen)
    name     = pkg.name
    ver      = pkg.version
    rel      = pkg.release
    arch     = pkg.arch
    size     = format_number(float(pkg._size))
    repo     = pkg.repoid
    summ     = pkg.summary
    url      = pkg.url
    license  = pkg.license
    desc     = pkg.description    

    deplist = []
    for req in sorted([str(req) for req in pkg.requires]):
        deplist.append(req)

    deplist = sorted(list(set(deplist)))

    wrapper = textwrap.TextWrapper(width = main_width - 2)

    main_text = []

    main_text.append("Name    : %s\n" % name)
    main_text.append("Version : %s\n" % ver)
    main_text.append("Release : %s\n" % rel)
    main_text.append("Arch    : %s\n" % arch)
    main_text.append("Size    : %s\n" % size)
    main_text.append("Repo    : %s\n" % repo)
    main_text.append("License : %s\n\n" % license)

    main_text.append("Summary:\n")
    wrapper.initial_indent    = "  "
    wrapper.subsequent_indent = "  "
    main_text.append(wrapper.fill(summ) + "\n\n")

    main_text.append("Description:\n")
    main_text.append(wrapper.fill(desc) + "\n\n")
    main_text.append("Dependency:\n")
    for dep in deplist:
        main_text.append(wrapper.fill(str(dep)) + "\n")

    main_join_text = "".join(main_text)
    del main_text

    # Display information window
    HotkeyInfoWindow(insScreen, "Package information", main_join_text, \
                     main_width, main_height, {"F4" : "b"}, "F4:Back")

#------------------------------------------------------------
# def ButtonInfoWindow()
#
#   Display information window for Button mode.
#
# Input:
#   insScreen : screen instance
#   sTitle    : title string
#   sText     : main text
#   iWidth    : width of main text
#   iHeight   : height of main text
#   lstButtons: Button list [button name1, button name2, ...]
# Output:
#   str       : initial character in pressed button name
#------------------------------------------------------------
def ButtonInfoWindow(insScreen, sTitle, sText, iWidth, iHeight, lstButtons):

    # Get line number
    length = len(sText)
    index = 0
    count = 0
    scroll = 0
    while index < length:
        if sText[index] == "\n":
            count += 1
            if count > iHeight:
                scroll = 1
                break
        index += 1

    # Create Text instance
    t1 = snack.Textbox(iWidth - scroll * 2, iHeight, sText, scroll)

    # Create Button instance
    bb = snack.ButtonBar(insScreen, lstButtons)

    # Create Grid instance
    g = snack.GridForm(insScreen, sTitle, 1, 2)
    g.add(t1, 0, 0)
    g.add(bb, 0, 1, (0, 1, 0, -1))

    # Display window
    while True:
        result = bb.buttonPressed(g.run())

        rcode = None
        for x in lstButtons:
            if result == x.lower():
                rcode = x[0].lower()
                break
        if rcode != None:
            break

    insScreen.popWindow()
    return rcode

#------------------------------------------------------------
# def GetButtonMainSize()
#
#   Get best full screen main object size for Button mode
#
# Input:
#   insScreen : screen instance
# Output:
#   int       : width
#   int       : height
#------------------------------------------------------------
def GetButtonMainSize(insScreen):
    (width, height) = GetWindowSize(insScreen)

    width -= 8

    # It is not centered well only by doing -12 when the Height is an Odd.
    # In addition, it is necessary to do 1.
    height -= (12 - (height % 2))

    return (width, height)

def _make_grid_search(insScreen, search_id):

    l = snack.Label("Search Value:")
    l1 = snack.Label(" ")
    e = snack.Entry(30, search_id)
    b = snack.ButtonBar(insScreen,(("Search","search"),("Search off","cancel")))

    g = snack.GridForm(insScreen, "Enter Search String", 3, 6)
    g.add(l, 0, 1)
    g.add(l1,0, 2)
    g.add(e, 0, 3)
    g.add(l1,0, 4)
    g.add(b, 0, 5)

    return e, b, g

def _make_grid_input_path(insScreen, title, label, strText):

    l = snack.Label(label)
    l1 = snack.Label(" ")
    e = snack.Entry(50, strText)
    b = snack.ButtonBar(insScreen,(("   OK   ", "ok"), (" Cancel ", "cancel")))

    g = snack.GridForm(insScreen, title, 3, 6)
    g.add(l, 0, 1)
    g.add(l1,0, 2)
    g.add(e, 0, 3)
    g.add(l1,0, 4)
    g.add(b, 0, 5)

    return e, b, g

def SampleMissWindow(insScreen, error_str):
    buttons = ['  OK  ']
    (w, h) = GetButtonMainSize(insScreen)
    rr = ButtonInfoWindow(insScreen, "  Error !  ", error_str, w, h, buttons)
    return

#------------------------------------------------------------
# def PKGINSTPathInputWindow()
#
#   Display a window which you can input a path.
#
# Input:
#       title : Title of the window
#       label : A text aim to guide the users operation
# Output:
#   path   : path you have inputed
#------------------------------------------------------------
def PKGINSTPathInputWindow(insScreen, check_dir_exist, title, label, text_prev=""):

    rtn_sts = None

    while rtn_sts == None:
        (e, b, g) = _make_grid_input_path(insScreen, title, label , text_prev)
        r = g.runOnce()
        insScreen.popWindow()
        str = e.value()

        result = b.buttonPressed(r)
        if b.buttonPressed(r) == "ok":
            #  judge if or not the input is correct
            if check_dir_exist :
                if os.path.isdir(str) or os.path.isfile(str):
                    rtn_sts=str
                else:
                    buttons = ['  OK  ']
                    (w, h) = GetButtonMainSize(insScreen)
                    rr = ButtonInfoWindow(insScreen, "  Error !  ", "Not a correct path! Input again, please !", \
                                          w, h, buttons)
            else:
                real_path=os.path.realpath(str)
                folder=os.path.split(real_path)
                folder='/'.join(folder[:-1])
                if os.path.isdir(folder):
                    rtn_sts=real_path
                else:
                    buttons = ['  OK  ']
                    (w, h) = GetButtonMainSize(insScreen)
                    rr = ButtonInfoWindow(insScreen, \
                                          "  Error !  ", \
                                          "The path but the last folder must exist. Please check it ! ", \
                                          w, h, buttons)
        else:
            if str:
                text_prev = str
            rtn_sts = text_prev
            break

    insScreen.popWindow()
    return (result, rtn_sts)

def PKGINSTPackageSearchWindow(insScreen):

    search_id = ""
    rtn_sts = None

    while rtn_sts == None:

        (e, b, g) = _make_grid_search(insScreen, search_id)
        r = g.runOnce()
        insScreen.popWindow()

        sts = e.value()

        if b.buttonPressed(r) == "search":
            regexp = re.compile(r'^[-\+\*/\:;,.\?_&$#\"\'!()0-9A-Za-z]+$')
            rs = regexp.search(sts)
            if rs != None:
                rtn_sts = sts
            else:
                buttons = ['OK']
                (w, h) = GetButtonMainSize(insScreen)
                rr = ButtonInfoWindow(insScreen, "Error!", "Search Value Invalid!", \
                                  w, h, buttons)
        else:
            break
        search_id = sts

    return rtn_sts

#------------------------------------------------------------
# def PKGTypeSelectWindow()
#
#   Display locale doc and dbg pacakges select window.
#
# Input:
#   pkgTypeList   : package type list 
#     ["locale", "doc", "dbg"]
#      "locale" = True/False : install/not install *-locale/*-localedata package
#      "doc"    = True/False : install/not install doc package 
#      "dbg"    True/False : install/not install dbg package
#      "static"    True/False : install/not install *-staticdev package
#      "ptest"    True/False : install/not install *-ptest package
# Output:
#   pkgTypeList   : select result
#------------------------------------------------------------
def PKGTypeSelectWindow(insScreen, pkgTypeList, position = 0):

    iPosition = position
    # Create CheckboxTree instance
    (main_width, main_height) = GetHotKeyMainSize(insScreen)
    main_height -= 2

    #print " packages = %s" % len(packages)
    if len(pkgTypeList) > main_height:
        scroll = 1
    else:
        scroll = 0

    hotkey_base_text = "  F3:Next  F4:Back  F5:Info  F9:Exit"
    wrapper = textwrap.TextWrapper(width = main_width)
    hotkey_text = wrapper.fill(hotkey_base_text)

    insScreen.pushHelpLine(hotkey_text)
    if hotkey_text != hotkey_base_text:
        main_height -= 1
        hotkey_line = 2
    else:
        hotkey_line = 1

    li = snack.Listbox(main_height, scroll = scroll, width = main_width)
    idx = 0
    for x in pkgTypeList:
        if x.status:
            status = "*"
        else:
            status = " "
        str = "%s [%s]" % (x.name, status)

        li.append(str, idx)
        idx += 1
    # Set position
    num_type = len(pkgTypeList)
    if num_type > 1:
        if num_type <= iPosition:
            iPosition = num_typr - 1
        if  num_type > (iPosition + main_height / 2):
            before_position = (iPosition + main_height / 2)
        else:
            before_position = num_type - 1
    li.setCurrent(before_position)
    li.setCurrent(iPosition)

    t1 = snack.Textbox(main_width, 1, "-" * main_width)
    t2 = snack.Textbox(main_width, hotkey_line, hotkey_text)

    # Create Grid instance
    title = "Customize special type packages"

    g = snack.GridForm(insScreen, title, 1, 3)
   
    #g.add(t1, 0, 2) 
    #g.add(t2, 0, 4, (0, 0, 0, -1))
    g.add(li, 0, 0)

############# append test key 'S' ####
    myhotkeys = {"ENTER" : "ENTER", \
                 " "     : " ", \
                 "F3"     : "n", \
                 "F4"     : "b", \
                 "F5"     : "i", \
                 "F9"     : "x"}

    for x in myhotkeys.keys():
        g.addHotKey(x)
#####################################
    while True:
        result = g.run()
        idx = li.current()
        if result in myhotkeys:
            if myhotkeys[result] == "ENTER" or \
               myhotkeys[result] == " ":
                curr_type = pkgTypeList[idx]
                if not curr_type.status:
                    curr_type.status = True
                    newsign = "*"
                else:
                    curr_type.status = False
                    newsign = " "
                item = "%s [%s]" % (curr_type.name, newsign)
                li.replace(item, idx)    
                idx += 1

                if idx >= num_type:
                    idx = num_type - 1
                li.setCurrent(idx)
            else:
                break

    #return
    insScreen.popHelpLine()
    insScreen.popWindow()
    return (myhotkeys[result], idx, pkgTypeList)


def PKGTypeSelectWindowCtrl(insScreen, pkgTypeList):
    idx = 0
    while True:
        (hkey, idx, pkgTypeList) = PKGTypeSelectWindow(insScreen, pkgTypeList, idx)
        if hkey == "i":
            # info
            description = pkgTypeList[idx].description
            subject = pkgTypeList[idx].name
            PKGINSTTypeInfoWindow(insScreen, subject, description)

        elif hkey == "x":
            # exit
            exit_hkey = HotkeyExitWindow(insScreen)
            if exit_hkey == "y":
                if insScreen != None:
                    StopHotkeyScreen(insScreen)
                    insScreen = None
                    sys.exit(0)

        elif hkey == "n":
            return ("n", pkgTypeList)
        elif hkey == "b":
            return ("b", pkgTypeList)

#------------------------------------------------------------
# def PKGINSTPackageWindow()
#
#   Display package select window.
#
# Input:
#   insScreen   : screen instance
#   lstPackage  : package info list
#     [str, str, i]
#      str      : package name
#      str      : package summary
#      i        : select status
#   dispPackage ; disp package info list
#   iPosition   : current entry position
#   lTargetSize : target size
#   lHostSize   : host size
#   search      : search string
#   install_type: INSTALL or REMOVE or UPDATE
#   group_hotkey: show group_hotkey
# Output:
#   str   : pressed hotkey "r", "f", "c", "n", "b", "d", "s", "i", or "x"
#   int   : position
#   lst   : package info list (updated)
#------------------------------------------------------------
def PKGINSTPackageWindow(insScreen, packages, selected_packages, iPosition, lTargetSize, lHostSize, search, \
                                                                                               install_type, group_hotkey=False):
    installed_pkgs = 0
    numChange=True      #Select or unselect operation that lead selected number change


    # Create CheckboxTree instance
    (main_width, main_height) = GetHotKeyMainSize(insScreen)
    main_height -= 2

    #print " packages = %s" % len(packages)
    if len(packages) > main_height:
        scroll = 1
    else:
        scroll = 0

    if group_hotkey == True:
        hotkey_base_text = "  F1:select/unselect All  F2:Search  F3:Next  F4:Back  F5:Info  F6:Group  F9:Exit"
    else:
        hotkey_base_text = "  F1:select/unselect All  F2:Search  F3:Next  F4:Back  F5:Info  F9:Exit"

    #insScreen.pushHelpLine(" ")
    insScreen.pushHelpLine(hotkey_base_text)
    wrapper = textwrap.TextWrapper(width = main_width)
    hotkey_text = wrapper.fill(hotkey_base_text)
    if hotkey_text != hotkey_base_text:
        main_height -= 1
        hotkey_line = 2
    else:
        hotkey_line = 1

    li = snack.Listbox(main_height, scroll = scroll, width = main_width)

    idx = 0
    for x in packages:
        if install_type==ACTION_INSTALL and x.installed :
            status = "I"
            installed_pkgs += 1
        elif x in selected_packages:
            status = SIGN_SELECT[install_type]
        else:
            status = " "
        str = "[%s] %s " % (status, x.name)

        li.append(str, idx)
        idx += 1
    # Set position
    num_package = len(packages)
    before_position = 0
    if num_package > 1:
        if num_package <= iPosition:
            iPosition = num_package - 1
        if  num_package > (iPosition + main_height / 2):
            before_position = (iPosition + main_height / 2)
        else:
            before_position = num_package - 1
    li.setCurrent(int(before_position))
    li.setCurrent(int(iPosition))

    # Create Text instance
    text=""
    t1 = snack.Textbox(main_width, 1, "-" * main_width)
    t2 = snack.Textbox(main_width, 1, text)
    t3 = snack.Textbox(main_width, 1, "-" * main_width)
    t4 = snack.Textbox(main_width, hotkey_line, hotkey_text)

    # Create Grid instance
    if search == None:
        title = "Select package"
    else:
        title = "Select package - (%s)" % search

    g = snack.GridForm(insScreen, title, 1, 3)
    g.add(li, 0, 0)
    g.add(t1, 0, 1, (-1, 0, -1, 0))
    g.add(t2, 0, 2, (0, 0, 0, 0))
    #g.add(t3, 0, 3, (-1, 0, -1, 0))
    #g.add(t4, 0, 4, (0, 0, 0, -1))




############# append test key 'S' ####
    myhotkeys = {"ENTER" : "ENTER", \
                 " "     : " ", \
                 "F3"     : "n", \
                 "F4"     : "b", \
                 "F2"     : "r", \
                 "F5"     : "i", \
                 "F9"     : "x", \
                 "F1"     : "a"}

    #If group exists, add group_hotkey
    if group_hotkey == True:
        myhotkeys["F6"] = "g"

    for x in myhotkeys.keys():
        g.addHotKey(x)

#####################################
    while True:

        if numChange:
            if install_type == ACTION_INSTALL:
                text = "All Packages [%ld]    Installed Packages [%ld]    Selected Packages [%ld]" % \
                       (num_package, installed_pkgs, len(selected_packages))
            else:
                text = "All Packages [%ld]    Selected Packages [%ld]" % \
                       (num_package, len(selected_packages))
            t2.setText(text)
            numChange = False

        result = g.run()
        idx = li.current()
        if result in myhotkeys:
            if myhotkeys[result] == "ENTER" or \
               myhotkeys[result] == " ":
                numChange=True
                li = _StatusToggle(li, myhotkeys[result], idx, selected_packages, \
                                                          packages, install_type)
                idx += 1
                if idx >= num_package:
                    idx = num_package - 1
                li.setCurrent(idx)
            elif myhotkeys[result]=="a":        ###
                li = _SelectAll(li, myhotkeys[result],num_package, selected_packages, \
                                                         packages, install_type)
                li.setCurrent(idx)
                numChange = True
            else:
                break

    #return
    insScreen.popHelpLine()
    insScreen.popWindow()
    return (myhotkeys[result], idx, selected_packages)

#------------------------------------------------------------
# def PKGINSTDebuginfoWindow()
#
#   Display package select window.
#
# Input:
#   insScreen   : screen instance
#   lstDebugPkg : package info list
#     [str, str, i]
#      str      : package name
#      str      : package summary
#      i        : select status
#   iPosition   : current entry position
#   lTargetSize : target size
#   lHostSize   : host size
# Output:
#   str   : pressed hotkey "c", "n", "b", "i", or "x"
#   int   : position
#   lst   : package info list (updated)
#------------------------------------------------------------
def PKGINSTDebuginfoWindow(insScreen, lstDebugPkg, selected_packages, iPosition, \
                         lTargetSize, lHostSize):
    
    installed_pkgs = 0
    # Create CheckboxTree instance

    (main_width, main_height) = GetHotKeyMainSize(insScreen)
    main_height -= 2

    if len(lstDebugPkg) > main_height:
        scroll = 1
    else:
        scroll = 0

    hotkey_base_text = "SPACE/ENTER:select/unselect  N:Next  B:Back  I:Info  X:eXit"
    wrapper = textwrap.TextWrapper(width = main_width)
    hotkey_text = wrapper.fill(hotkey_base_text)
    if hotkey_text != hotkey_base_text:
        main_height -= 1
        hotkey_line = 2
    else:
        hotkey_line = 1

    li = snack.Listbox(main_height, scroll = scroll, width = main_width)

    idx = 0
    for x in lstDebugPkg:
        if x.installed:
            status = "I"
            installed_pkgs += 1
        elif x in selected_packages:
            status = "*"
        else:
            status = " "
        str = "[%s] %s " % (status, x.name)

        li.append(str, idx)
        idx += 1

    # Set position
    num_package = len(lstDebugPkg)
    if num_package <= iPosition:
        iPosition = num_package - 1
    if  num_package > (iPosition + main_height / 2):
        before_position = (iPosition + main_height / 2)
    else:
        before_position = num_package - 1
    li.setCurrent(before_position)
    li.setCurrent(iPosition)

    # Create Text instance
    t1 = snack.Textbox(main_width, 1, "-" * main_width)
    text = "All Packages [%ld]    Installed Packages    [%ld] Selected Packages [%ld]" % \
          (num_package, installed_pkgs, len(selected_packages))

    t2 = snack.Textbox(main_width, 1, text)
    t3 = snack.Textbox(main_width, 1, "-" * main_width)
    t4 = snack.Textbox(main_width, hotkey_line, hotkey_text)

    # Create Grid instance
    g = snack.GridForm(insScreen, "Select debuginfo packages", 1, 5)
    g.add(li, 0, 0)
    g.add(t1, 0, 1, (-1, 0, -1, 0))
    g.add(t2, 0, 2)
    g.add(t3, 0, 3, (-1, 0, -1, 0))
    g.add(t4, 0, 4, (0, 0, 0, -1))



############# append test key 'S' ####
    myhotkeys = {"ENTER" : "ENTER", \
                 " "     : " ", \
                 "n"     : "n", \
                 "N"     : "n", \
                 "b"     : "b", \
                 "B"     : "b", \
                 "i"     : "i", \
                 "I"     : "i", \
                 "x"     : "x", \
                 "X"     : "x"}
    for x in myhotkeys.keys():
        g.addHotKey(x)
#####################################


    # Display window
    while True:
        result = g.run()
        idx = li.current()
        if result in myhotkeys:
            if myhotkeys[result] == "ENTER" or \
               myhotkeys[result] == " ":
                li = _StatusToggle(li, myhotkeys[result], idx, selected_packages, lstDebugPkg)
                idx += 1
                if idx >= num_package:
                    idx = num_package - 1
                li.setCurrent(idx)
            else:
                break

    insScreen.popWindow()
    return (myhotkeys[result], idx, selected_packages)

def ConfirmGplv3Window(insScreen, packages):
    if insScreen == None:
        print ("error ConfirmGplv3Window: the screen is None")
    # Create CheckboxTree instance
    (main_width, main_height) = GetHotKeyMainSize(insScreen)
    main_height -= 2

    if len(packages) > main_height:
        scroll = 1
    else:
        scroll = 0

    hotkey_base_text = "These GPLv3 packages are depended"
    wrapper = textwrap.TextWrapper(width = main_width)
    hotkey_text = wrapper.fill(hotkey_base_text)
    if hotkey_text != hotkey_base_text:
        main_height -= 1
        hotkey_line = 2
    else:
        hotkey_line = 1

    li = snack.Listbox(main_height, scroll = scroll, width = main_width)

    idx = 0
    for x in packages:
        li.append(x.name, idx)
        idx += 1

    # Set position
    iPosition=0
    li.setCurrent(iPosition)

    # Create Text instance
    t1 = snack.Textbox(main_width, 1, "-" * main_width)
    t4 = snack.Textbox(main_width, hotkey_line, hotkey_text)

    # Create the help line
    insScreen.pushHelpLine("  F3:Next  F4:Back  F9:Exit")

    # Create Grid instance
    title = "GPLv3 that be depended"

    g = snack.GridForm(insScreen, title, 1, 5)
    g.add(li, 0, 0)
    g.add(t1, 0, 1, (-1, 0, -1, 0))
    g.add(t4, 0, 4, (0, 0, 0, 0))

############# append test key 'S' ####
    myhotkeys = {"F3"     : "n", \
                 "F4"     : "b", \
                 "F9"     : "x"}
    for x in myhotkeys.keys():
        g.addHotKey(x)
#####################################
    result = g.run()
    if result in myhotkeys:
        if myhotkeys[result] == "b" or myhotkeys[result] == "n":
            insScreen.popWindow()
            return (myhotkeys[result])

        elif myhotkeys[result] == "x":
            # exit
            insScreen.popHelpLine()
            insScreen.popWindow()
            exit_hkey = HotkeyExitWindow(insScreen)
            if exit_hkey == "y":
                if insScreen != None:
                    StopHotkeyScreen(insScreen)
                    insScreen = None
                    sys.exit(0)

