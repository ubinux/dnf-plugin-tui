# tui.py
# Tgui CLI command.
#
# Copyright (C) 2018 FUJITSU LIMITED
#
from __future__ import absolute_import
from __future__ import unicode_literals
from dnf.cli import commands
from dnf.cli.option_parser import OptionParser
from dnf.i18n import _
from itertools import chain
import dnf.subject

import dnf.exceptions
import hawkey
import logging

from .window import *
from .utils import fetchSPDXorSRPM, read_environ, conflictDetection, getInstalledList
import sys, os, copy, textwrap, snack, string, time, re, shutil, hashlib
from snack import *

from .Define import _TXT_ROOT_TITLE, Install_actions, Custom_actions, Image_types
from .mkimg.MKIMGJFFS2Window import *
from .mkimg.MKIMGINITRAMFSWindow import *
from .mkimg.MKIMGINITRDWindow import *
from .mkimg.MKIMGRAWWindow import *
from .mkimg.MKIMGSquashFSWindow import *
from .mkimg.MKIMGUBIFSWindow import *
from .mkimg.MKIMGInfo import *

import dnf
import dnf.cli.demand
import dnf.cli.option_parser
import dnf.cli.commands.shell
import dnf.conf
from dnf.cli.option_parser import OptionParser
import dnf.conf.substitutions
import dnf.const
import dnf.exceptions
import dnf.cli.format
import dnf.logging
import dnf.plugin
import dnf.persistor
import dnf.rpm
import dnf.cli.utils
import dnf.yum.misc
from subprocess import call

#Make image function entrance
Image_type_functions = { 0: [MKIMGJFFS2WindowCtrl, MKIMGConfirmJFFS2WindowCtrl],
                         1: [MKIMGINITRAMFSWindowCtrl, MKIMGConfirmINITRAMFSWindowCtrl],
                         2: [MKIMGINITRDWindowCtrl, MKIMGConfirmINITRDWindowCtrl],
                         3: [MKIMGRAWWindowCtrl, MKIMGConfirmRAWWindowCtrl],
                         4: [MKIMGSquashFSWindowCtrl, MKIMGConfirmSquashFSWindowCtrl],
                         5: [MKIMGUBIFSWindowCtrl, MKIMGConfirmUBIFSWindowCtrl],
                       }

Image_type_name      = { 0: "rootfs.jffs2.bin",
                         1: "rootfs.initramfs.cpio",
                         2: "rootfs.initrd.bin",
                         3: "rootfs.raw.bin",
                         4: "rootfs.SquashFS.bin",
                         5: "rootfs.ubi.img"
                       }

ACTION_INSTALL     = 0
ACTION_REMOVE      = 1
ACTION_UPGRADE     = 2
ACTION_GET_PKG     = 3
ACTION_GET_SOURCE  = 4
ACTION_GET_SPDX    = 5
ACTION_GET_ALL     = 6
ACTION_MAKE_IMG    = 7
GROUP_INSTALL      = 8

NEW_INSTALL        = 0
RECORD_INSTALL     = 1
SAMPLE_INSTALL     = 2

CONFIRM_EXIT       = 0
CONFIRM_INSTALL    = 1
CONFIRM_LICENSE    = 2
CONFIRM_REMOVE     = 3
CONFIRM_UPGRADE    = 4
CONFIRM_GET_PKG    = 5
CONFIRM_GET_SOURCE = 6
CONFIRM_GET_SPDX   = 7
CONFIRM_GET_ALL    = 8

ATTENTON_NONE           = 0
ATTENTON_HAVE_UPGRADE   = 1
ATTENTON_NONE_UPGRADE   = 2

STAGE_INSTALL_TYPE = 1
STAGE_CUSTOM_TYPE = 2
STAGE_RECORD_INSTALL = 3
STAGE_SAMPLE_INSTALL = 4
STAGE_PKG_TYPE = 5
STAGE_CUST_LIC = 6
STAGE_PACKAGE = 7
STAGE_PACKAGE_SPEC = 8
STAGE_PROCESS = 9
STAGE_GROUP = 10
STAGE_IMAGE_TYPE = 11

if "OECORE_NATIVE_SYSROOT" in os.environ:
    NATIVE_SYSROOT = os.environ["OECORE_NATIVE_SYSROOT"]
else:
    NATIVE_SYSROOT = "/opt/poky/2.6/sysroots/x86_64-pokysdk-linux"
SAMPLE = NATIVE_SYSROOT + "/usr/share/dnf"

logger = logging.getLogger('dnf')

@dnf.plugin.register_command
class TuiCommand(commands.Command):
    """A class containing methods needed by the cli to execute the
    tui command.
    """

    aliases = ('tui',)
    summary = _('Enter tui interface.')

    def __init__(self, cli=None):
        cli = cli or dnf.cli.Cli()
        super(TuiCommand, self).__init__(cli=cli)
        self.screen = None
        self.no_gpl3 = False
        self.install_type = ACTION_INSTALL
        self.image_type = 0

        self.pkgnarrow = 'all'
        self.patterns = None
        self.installed_available = False
        self.reponame = None
        self.config_file = ".config"
        self.pkginfo_file = None
        self.grps = []
        self.group_flag = False #Has group info or not
        self.group_botton = False #Press hotkey 'F6' or not
        self.save = True
        self.info_save = True

    @staticmethod
    def set_argparser(parser):
        parser.add_argument("--init", dest="with_init",
                          action="store_true", default=None,
                          help=_("Init the dnf environment for toolchain"))
        parser.add_argument("--call", dest="with_call",
                          action="store_true", default=None,
                          help=_(""))
        parser.add_argument("--pkg_list", dest="pkg_list",
                          help=_("Package list file"))
        # The value of dest can't be 'command' as value self.opts.command is already be used.
        parser.add_argument("--command", nargs='*', action="store", dest="command_args",
                                 default=None, help=_("Execute dnf command line"))
        parser.add_argument("--mkrootfs", action="store_true", dest="mkrootfs",
                                 default=None, help=_("Put rootfs to directory as user defines"))
        parser.add_argument("--nosave", action="store_true", dest="nosave",
                                 default=None, help=_("Don't save Package list file"))

    def pre_configure(self):
        # Used in target
        if "OECORE_NATIVE_SYSROOT" not in os.environ:
            return
        else:    
        # Used in host
            plugin_dir = os.path.split(__file__)[0] #the dir of dnf-host script
            if self.opts.with_init:
                os.system("%s/dnf-host init" %plugin_dir)
                sys.exit(0)
            if self.opts.with_call:
                return
            else:
                #Reload the conf and args
                env_path = os.getcwd() + "/.env-dnf"
                if os.path.exists(env_path):
                    # Before using dnf in cross-environment, source env path first
                    read_environ(env_path)

                    install_root_from_env = os.environ['HIDDEN_ROOTFS']
                    self.opts.installroot = install_root_from_env
                    self.opts.config_file_path = install_root_from_env + "/etc/dnf/dnf-host.conf"
                    self.opts.logdir = os.path.dirname(install_root_from_env)

                    #Execute dnf command line
                    if self.opts.command_args is not None:
                        os.environ["LD_PRELOAD"] = ''
                        base_cmd = "%s/dnf-host" % (plugin_dir)
                        if len(self.opts.command_args) > 0:
                            #Get cmd option for dnf
                            cmdstring = self.cli.cmdstring
                            cmdoption = cmdstring[cmdstring.find('--command') + 9:]
                            cmd = base_cmd + " %s" % (''.join(cmdoption))
                        #If args number of '--command' is 0, skip it.
                        elif not self.opts.mkrootfs:
                            logger.warning("Command line error: argument --command: expected at least one argument")
                            sys.exit(0)
                        else:
                            cmd = base_cmd + " --mkrootfs"

                        os.system(cmd)
                        sys.exit(0)

                    # "--pkg_list", "--mkrootfs", "--nosave" can not be used alone
                    if self.opts.pkg_list or self.opts.mkrootfs or self.opts.nosave:
                        logger.warning("Command line error: dnf tui expected --command")
                        sys.exit(0)

                    #Call subprocess dnf tui
                    tar = False
                    old_md5 = None

                    rpm_dbfile = self.opts.installroot + "/var/lib/rpm/rpmdb.sqlite"
                    if os.path.exists(rpm_dbfile):
                        f1 = open(rpm_dbfile, 'rb')
                        old_md5 = hashlib.md5(f1.read()).hexdigest()

                    exit_code = call(["dnf", "tui", "--call", "-c{}".format(
                                      self.opts.config_file_path), "--installroot={}".format(
                                      self.opts.installroot), "--setopt=logdir={}".format(
                                      self.opts.logdir), "--releasever=None"])
                    if exit_code != 0:
                        raise dnf.exceptions.Error(_("Failed to call dnf tui"))
                    
                    #When you choose tui, the rootfs will be made only after pkg operation
                    if old_md5:
                        f2 = open(rpm_dbfile, 'rb')
                        new_md5 = hashlib.md5(f2.read()).hexdigest()
                        #old_md5 and new_md5 is compared to determine whether the RPM source has changed,
                        #so as to determine whether rootfs needs to be packaged
                        if old_md5 != new_md5:
                            tar = True
                    elif os.path.exists(rpm_dbfile):
                        tar = True

                    if tar: 
                        plugin_dir = os.path.split(__file__)[0]
                        os.environ["LD_PRELOAD"] = ''
                        os.system("%s/dnf-host --mkrootfs" %plugin_dir)
                    sys.exit(0)
                
                else:
                    logger.warning("Please Init the environment first!\nUsage: dnf tui --init")
                    sys.exit(0)

    def configure(self):
        # append to ShellDemandSheet missing demands from
        # dnf.cli.demand.DemandSheet with their default values.
        default_demands = self.cli.demands
        self.cli.demands = dnf.cli.commands.shell.ShellDemandSheet()
        for attr in dir(default_demands):
            if attr.startswith('__'):
                continue
            try:
                getattr(self.cli.demands, attr)
            except AttributeError:
                setattr(self.cli.demands, attr, getattr(default_demands, attr))

        demands = self.cli.demands
        demands.root_user = False

    def run(self, command=None, argv=None):
        if "OECORE_NATIVE_SYSROOT" in os.environ: #if used in toolchain
            if self.opts.with_call:
                logger.debug("Enter tui interface.")
                self.PKGINSTDispMain()
                exist_pkgs = getInstalledList(self)
                self.Save_PackageInfo(exist_pkgs, "w")
            else:
                pass
        else:
            logger.debug("Enter tui interface.")
            self.PKGINSTDispMain()
            exist_pkgs = getInstalledList(self)
            self.Save_PackageInfo(exist_pkgs, "w")

    def run_dnf_command(self, s_line):
        """Execute the subcommand you put in.
        """
        opts = self.cli.optparser.parse_main_args(s_line)
        cmd_cls = self.cli.cli_commands.get(opts.command)
        cmd = cmd_cls(self)
        try:
            opts = self.cli.optparser.parse_command_args(cmd, s_line)
            cmd.cli = self.cli
            cmd.cli.demands = copy.deepcopy(self.cli.demands)
            cmd.configure()
            cmd.run()
#        except:
#            pass
        except Exception as e:
            logger.error(_("%s."), e)
            StopHotkeyScreen(self.screen)
            self.screen = None
            sys.exit(0)

    def PKG_filter(self, packages):
        strings_pattern_end = ('-dev', '-doc', '-dbg', '-staticdev', '-ptest', '-src', '-lic')
        notype_pkgs = packages
        for pkg in packages:
            if "-locale-" in pkg.name:
                notype_pkgs.remove(pkg)
            elif "-localedata-" in pkg.name:
                notype_pkgs.remove(pkg)
            elif pkg.name.endswith(strings_pattern_end):
                notype_pkgs.remove(pkg)
        return notype_pkgs

    def GET_SOURCE_or_SPDX(self, selected_pkgs):
        if self.screen != None:
            StopHotkeyScreen(self.screen)
            self.screen = None
        notype_pkgs = self.PKG_filter(selected_pkgs)
        if self.install_type == ACTION_GET_SOURCE:
            srcdir_path = os.environ['SRPM_REPO_DIR']
            destdir_path = os.environ['SRPM_DESTINATION_DIR']
            fetchSPDXorSRPM('srpm', notype_pkgs, srcdir_path, destdir_path)
        elif self.install_type == ACTION_GET_SPDX:
            srcdir_path = os.environ['SPDX_REPO_DIR']
            destdir_path = os.environ['SPDX_DESTINATION_DIR']
            fetchSPDXorSRPM('spdx', notype_pkgs, srcdir_path, destdir_path)

    def GET_RKG(self, selected_pkgs):
        if self.screen != None:
            StopHotkeyScreen(self.screen)
            self.screen = None
        srcdir_path = os.environ['RPM_REPO_DIR']
        destdir_path = os.environ['RPM_DESTINATION_DIR']
        fetchSPDXorSRPM('rpm', selected_pkgs, srcdir_path, destdir_path)

    def GET_ALL(self, selected_pkgs):
        if self.screen != None:
            StopHotkeyScreen(self.screen)
            self.screen = None
        fetchSPDXorSRPM('rpm', selected_pkgs, 
                    os.environ['RPM_REPO_DIR'], os.environ['RPM_DESTINATION_DIR'])
        notype_pkgs = self.PKG_filter(selected_pkgs)
        fetchSPDXorSRPM('srpm', notype_pkgs, 
                    os.environ['SRPM_REPO_DIR'], os.environ['SRPM_DESTINATION_DIR'])
        fetchSPDXorSRPM('spdx', notype_pkgs, 
                    os.environ['SPDX_REPO_DIR'], os.environ['SPDX_DESTINATION_DIR'])

    def Read_ConfigFile(self, display_pkgs=[], selected_pkgs=[]):
        f = open(self.config_file, "r")
        get_text = f.read()
        config_list = get_text.split('\n')
        
        if display_pkgs:
            for pkg in display_pkgs:
                for config_pkg in config_list:
                    if pkg.name == config_pkg:
                        selected_pkgs.append(pkg)
                    elif pkg.name == "lib32-" + config_pkg:
                        selected_pkgs.append(pkg)
                    elif pkg.name == "lib64-" + config_pkg:
                        selected_pkgs.append(pkg)
            selected_pkgs = list(set(selected_pkgs))
            f.close()
            return selected_pkgs
        else:
            f.close()
            return config_list

    def Save_ConfigFile(self, selected_pkgs, file_name, mode):
        save_list = []
        for pkg in selected_pkgs:
            save_list.append(pkg.name)

        f = open(file_name, mode)
        for line in save_list:
            f.write(line + '\n')
        f.close()

    def Confirm_ConfigFile(self):
        result = ""
        if self.install_type == ACTION_INSTALL:
            self.config_file = ".config"
            (result, self.config_file) = PKGINSTPathInputWindow(self.screen, \
                                            False, \
                                            "  Package List File  ", \
                                            "Enter the name of package list file you wish to save:", \
                                            self.config_file )
        if result == "cancel":
            # save config file
            self.save = False

    def Confirm_PackageInfo(self):
        date = os.popen("date +%Y%m%d%H%M").read().split("\n")[0]
        self.pkginfo_file = "installed-packages-list-" + date + ".csv"
        (result, self.pkginfo_file) = PKGINSTPathInputWindow(self.screen, \
                                        False, \
                                        "  Installed Package Info File  ", \
                                        "Enter the name of installed package info list file you wish to save:",      \
                                        self.pkginfo_file )
        if result == "cancel":
            self.info_save = False


    def Save_PackageInfo(self, existed_pkgs, mode):
        if self.info_save == True:
            f = open(self.pkginfo_file, mode)
            for line in existed_pkgs:
                f.write(line.name + ", " + line.version + ", " + line.license + '\n')
            f.close()

    def Get_NotExistList(self):
        try:
            ypl = self.base.returnPkgLists(
                self.pkgnarrow, self.patterns, self.installed_available, self.reponame)
        except dnf.exceptions.Error as e:
            return 1, [str(e)]

        package_list = ypl.available + ypl.installed
        name_list = []
        for package_item in package_list:
            name_list.append(package_item.name)

        f = open(self.config_file, "r")
        get_text = f.read()
        config_list = get_text.split('\n')
        if config_list[-1] == "":
            del config_list[-1]

        not_exist_pkgs_list = []
        for config_item in config_list:
            if config_item not in name_list:
                not_exist_pkgs_list.append(config_item)

        return not_exist_pkgs_list

    def Read_Samples(self):
        sample_list = []
        if os.path.isdir(SAMPLE):
            for (root, dirs, filenames) in os.walk(SAMPLE):
                filenames.sort()
                for index in range(len(filenames)):
                    sample = ("Reference" + str(index+1) + "(" + filenames[index] + " based root file system)", filenames[index] + " based root file system", filenames[index])
                    sample_list.append(sample)
            return (True, sample_list)
        else:
            return (False, "There is no sample files")

    def installDisp(self, selected_pkgs, selected_pkgs_spec, pkgs_spec):
        self.install_type = PKGINSTActionWindowCtrl(self.screen, Install_actions, self.install_type)

        if self.install_type == ACTION_INSTALL:
            stage = STAGE_CUSTOM_TYPE
            return (stage, selected_pkgs, selected_pkgs_spec, pkgs_spec)
        elif self.install_type == ACTION_MAKE_IMG:
            stage = STAGE_IMAGE_TYPE
        else:
            stage = STAGE_PACKAGE

        self.group_botton = False
        return (stage, [], [], [])

    def customDisp(self):
        sample_type = 0
        (result, custom_type) = PKGCUSActionWindowCtrl(self.screen, Custom_actions, self.install_type)

        # Read comps information
        self.base.read_comps(arch_filter=True)
        self.grps = self.base.comps.groups
        if self.grps:
            self.group_flag = True # Has group info
            self.group_botton = False #hotkey F6 hasn't been pressed

        if result == "b":
            # back
            stage = STAGE_INSTALL_TYPE
            return (stage, sample_type, custom_type)

        if custom_type == NEW_INSTALL:
            stage = STAGE_PACKAGE
            result = HotkeyExitWindow(self.screen, confirm_type=CONFIRM_LICENSE)
            if result == "y":
                self.no_gpl3 = False
            else:
                self.no_gpl3 = True

        # Load Package list install
        elif custom_type == RECORD_INSTALL:
            stage = STAGE_RECORD_INSTALL
            self.no_gpl3 = False
            # Load Sample to install
        elif custom_type >= SAMPLE_INSTALL:
            sample_type = custom_type-2
            custom_type = SAMPLE_INSTALL
            stage = STAGE_SAMPLE_INSTALL
            self.no_gpl3 = False
        return (stage, sample_type, custom_type)
    
    def recordDisp(self):
        (result, self.config_file) = PKGINSTPathInputWindow(self.screen, \
                                                      True, \
                                                      "  Package List File  ", \
                                                      "Enter the name of package list file you wish to load:", \
                                                      self.config_file )

        if result == "cancel":
            # back
            stage = STAGE_CUSTOM_TYPE

        else:
            # next
            not_exist_list = self.Get_NotExistList()
            if not_exist_list:
                hkey = HotkeyNotExistWindow(self.screen, not_exist_list)
                if hkey == "n":
                    stage = STAGE_CUSTOM_TYPE
                else:
                    stage = STAGE_PACKAGE
            else:
                stage = STAGE_PACKAGE
        return stage

    def sampleDisp(self, sample_list, sample_type):
        config_file = SAMPLE + '/' + sample_list[sample_type][2]
        try:
            f = open(config_file, "r")
        except Exception as e:
            logger.error(_("%s."), e)
            StopHotkeyScreen(self.screen)
            self.screen = None
            sys.exit(0)
        self.config_file = config_file
        stage = STAGE_PACKAGE
        return stage

    def groupDisp(self): 
        group_list = []
        pkg_group = []
        for grp in self.grps:
            group = (grp.ui_name, grp.ui_description, grp.mandatory_packages)
            group_list.append(group)
                    
        # Show group list
        (result, group_id) = PKGCUSActionWindowCtrl(self.screen, group_list, self.install_type, True)

        if result == "b":
            # back
            stage = STAGE_CUSTOM_TYPE

        elif result == "g":
            # Back to non-group
            self.group_botton = False
            stage = STAGE_PACKAGE

        # Enter in group
        else:
            pkg_group = group_list[group_id][2]
            stage = STAGE_PACKAGE
        return  (stage, result, pkg_group)

    def packageDisp(self, selected_pkgs, custom_type, pkg_group):
        confirm_type = ""
        stage = STAGE_PACKAGE
        if self.install_type == ACTION_INSTALL:
            # Show hotkey F6 in package selection interface
            if self.group_botton == False:
                (result, selected_pkgs, pkgs_spec, cancel_pkgs) = self.PKGINSTWindowCtrl(None, None, selected_pkgs, custom_type, pkg_group=[], group_hotkey=True)

            else:
                # Enter group interface
                (result, selected_pkgs, pkgs_spec, cancel_pkgs) = self.PKGINSTWindowCtrl(None, None, selected_pkgs, custom_type, pkg_group, group_hotkey=False)

        else:
            (result, selected_pkgs, pkgs_spec, cancel_pkgs) = self.PKGINSTWindowCtrl(None, None, selected_pkgs, custom_type)

        if result == "b":
            # back
            if self.install_type == ACTION_INSTALL:
                stage = STAGE_CUSTOM_TYPE
            else:
                stage = STAGE_INSTALL_TYPE
                self.no_gpl3 = False

            if self.group_botton == True:
                stage = STAGE_GROUP
            return  (stage, result, selected_pkgs, pkgs_spec, cancel_pkgs, confirm_type)

        if result == "g":
            if self.group_flag == True and self.install_type == ACTION_INSTALL:
                # Switch between group and simple
                self.group_botton = True
                stage = STAGE_GROUP
                return  (stage, result, selected_pkgs, pkgs_spec, cancel_pkgs, confirm_type)

        elif result == "n":
            if self.install_type == ACTION_INSTALL:
                stage = STAGE_PKG_TYPE
            else:
                #confirm if or not continue process function
                install_type_switch = {ACTION_REMOVE: CONFIRM_REMOVE, \
                                    ACTION_UPGRADE: CONFIRM_UPGRADE, \
                                    ACTION_GET_PKG: CONFIRM_GET_PKG, \
                                    ACTION_GET_SOURCE: CONFIRM_GET_SOURCE, \
                                    ACTION_GET_SPDX: CONFIRM_GET_SPDX, \
                                    ACTION_GET_ALL: CONFIRM_GET_ALL}
                confirm_type = install_type_switch.get(self.install_type)

                hkey = HotkeyExitWindow(self.screen, confirm_type)
                if hkey == "y":
                    stage = STAGE_PROCESS
                elif hkey == "n":
                    stage = STAGE_PACKAGE
        return  (stage, result, selected_pkgs, pkgs_spec, cancel_pkgs, confirm_type)

    def pkgTypeDisp(self, custom_type, pkgTypeList, pkg_installed):
        if custom_type == RECORD_INSTALL:
            # get packagelist from .config
            pkgConfigList = self.Read_ConfigFile()
            pkgConfigList_temp = copy.deepcopy(pkgConfigList)
            for pkg in pkgConfigList_temp:
                for pkg_install in pkg_installed:
                    if pkg == pkg_install.name:
                        pkgConfigList.remove(pkg)
            strings_pattern_end = ['-dev', '-doc', '-dbg', '-staticdev', '-ptest', '-src', '-lic']
            for pkgName in pkgConfigList:
                if "-locale-" in pkgName or "-localedata-" in pkgName:
                    for Type in pkgTypeList:
                        if Type.name == "locale":
                            Type.status = True
                if pkgName.endswith(tuple(strings_pattern_end)):
                    index = pkgName.rindex('-')
                    string_pattern = pkgName[index+1:]
                    for Type in pkgTypeList:
                        if Type.name == string_pattern:
                            Type.status = True
                    strings_pattern_end.remove("-" + string_pattern)

        (result, pkgTypeList) = PKGTypeSelectWindowCtrl(self.screen, pkgTypeList)
        if result == "b":
            # back
            stage = STAGE_PACKAGE
        elif result == "n":
            stage = STAGE_PACKAGE_SPEC
        return (stage, pkgTypeList)

    def packageSpecDisp(self, pkgTypeList, pkgs_spec, selected_pkgs_spec, custom_type, selected_pkgs):
        (result, selected_pkgs_spec, pkgs_temp, cancel_pkgs) = self.PKGINSTWindowCtrl(pkgTypeList, pkgs_spec, selected_pkgs_spec, custom_type, conflict_attach_pkgs=selected_pkgs)
        if result == "b":
            # back
            stage = STAGE_PKG_TYPE
        elif result == "n":
            stage = STAGE_PROCESS
        return (stage, selected_pkgs_spec, selected_pkgs, cancel_pkgs)

    def imageTypeDisp(self, Image_types):
        state = 0
        while state < 3:
            # Select Image Type
            if state == 0:
                (result, self.image_type) = PKGCUSActionWindowCtrl(self.screen, Image_types, self.image_type, title="Select Image type")
                if result == "b":
                    # back
                    stage = STAGE_INSTALL_TYPE
                    break

                insMKIMGInfo = MKIMGInfo(self.image_type)

            # Setup Configuration
            elif state == 1:
                #Press ENTER, you can call the corresponding make image function
                rcode = Image_type_functions[self.image_type][0](self.screen, insMKIMGInfo)
                #retrun button of MKIMGxxxWindowCtrl
                if rcode == "b":
                    # back
                    state = 0
                    continue

            # Confirm
            elif state == 2:
                # Make Image file name
                if os.path.isdir(insMKIMGInfo.get_to_dir_path()):
                    insMKIMGInfo.set_image_file_name(Image_type_name[self.image_type])
                else:
                # If you give the abspath of img_patch, no need to set the img_name
                    (to_dir, img_name) = os.path.split(insMKIMGInfo.get_to_dir_path())
                    insMKIMGInfo.set_to_dir_path(to_dir)
                    insMKIMGInfo.set_image_file_name(img_name)

                # information confirm function
                rcode = Image_type_functions[self.image_type][1](self.screen, insMKIMGInfo)
                if rcode == "b":
                    state = 1
                    continue

            state = state + 1
        return stage

    def processDisp(self, selected_pkgs, selected_pkgs_spec, cancel_pkgs, confirm_type):
        stage = STAGE_PROCESS
        if self.install_type == ACTION_GET_SOURCE or self.install_type == ACTION_GET_SPDX:
            self.GET_SOURCE_or_SPDX(selected_pkgs)
            return ("b", stage)
        if self.install_type == ACTION_GET_PKG:
            self.GET_RKG(selected_pkgs)
            return ("b", stage)
        if self.install_type == ACTION_GET_ALL:
            self.GET_ALL(selected_pkgs)
            return ("b", stage)
        else:
            self.Confirm_PackageInfo()

            for cancel_pkg in cancel_pkgs:
                if cancel_pkg in selected_pkgs:
                    selected_pkgs.remove(cancel_pkg)
                if cancel_pkg in selected_pkgs_spec:
                    selected_pkgs_spec.remove(cancel_pkg)
            if self.install_type == ACTION_INSTALL:
                s_line = ["install"]
                for pkg in selected_pkgs:           #selected_pkgs
                    s_line.append(pkg.name)
                for pkg in selected_pkgs_spec:
                    s_line.append(pkg.name)
            elif self.install_type == ACTION_REMOVE:
                s_line = ["remove"]
                for pkg in selected_pkgs:           #selected_pkgs
                    s_line.append(pkg.name)
            elif self.install_type == ACTION_UPGRADE:
                s_line = ["upgrade"]
                for pkg in selected_pkgs:           #selected_pkgs
                    s_line.append(pkg.name)
            #Determine whether there are parameters after install, remove, and upgrade.
            if len(s_line) != 1:
                self.run_dnf_command(s_line)

            if self.no_gpl3:
                try:
                    #obtain the transaction
                    self.base.resolve(self.cli.demands.allow_erasing)
                except Exception as e:
                    #do not handle conflict exceptions here
                    pass
                #obtain the deps of selected pkgs
                install_set = self.base.transaction.install_set

                result = self.showChangeSet(install_set)
                #continue to install
                if result == "y" or result == "n":
                    if self.install_type == ACTION_INSTALL:
                        confirm_type = CONFIRM_INSTALL

                    hkey = HotkeyExitWindow(self.screen, confirm_type)
 
                    if hkey == "y":
                        self.Confirm_ConfigFile()
                        if self.install_type == ACTION_INSTALL:
                            if self.save == True:
                                self.Save_ConfigFile(selected_pkgs, self.config_file, "w")
                                #selected_pkgs_spec
                                if selected_pkgs_spec:
                                    self.Save_ConfigFile(selected_pkgs_spec, self.config_file, "a")
                        if self.screen != None:
                            StopHotkeyScreen(self.screen)
                            self.screen = None
                        if self.install_type != ACTION_REMOVE:
                            self.base.conf.assumeyes = True
                        return ("b", stage)
                    elif hkey == "n":
                        stage = STAGE_PKG_TYPE
                #don't want to install GPLv3 that depended by others
                elif result == "b":
                    stage = STAGE_PKG_TYPE
            else:
                self.Confirm_ConfigFile()
 
                if self.install_type == ACTION_INSTALL:
                    confirm_type = CONFIRM_INSTALL
                    hkey = HotkeyExitWindow(self.screen, confirm_type)
                    if hkey == "y":
                        if self.save == True:
                            self.Save_ConfigFile(selected_pkgs, self.config_file, "w")
                            #selected_pkgs_spec
                            if selected_pkgs_spec:
                                self.Save_ConfigFile(selected_pkgs_spec, self.config_file, "a")
                    elif hkey == "n":
                        stage = STAGE_PKG_TYPE
                        return (" ", stage)
                if self.screen != None:
                    StopHotkeyScreen(self.screen)
                    self.screen = None
                    if self.install_type != ACTION_REMOVE:
                        self.base.conf.assumeyes = True
                return ("b", stage)

        return (" ", stage)

    def PKGINSTDispMain(self):
        custom_type = NEW_INSTALL
        pkg_group = []
        #----returnPkgLists function of dnf------
        try:
            ypl = self.base.returnPkgLists(
                self.pkgnarrow, self.patterns, self.installed_available, self.reponame)
        except dnf.exceptions.Error as e:
            return 1, [str(e)]
        else:
            if len(ypl.available + ypl.installed) < 1:
                print ("Error! No packages!")
                sys.exit(0)
            self.screen = StartHotkeyScreen(_TXT_ROOT_TITLE)
            if self.screen == None:
                sys.exit(1)
            stage = STAGE_INSTALL_TYPE
 
            def __init_pkg_type():
                pkgTypeList = []
            
                pkgType_locale = pkgType("locale", False, "If select, you can see/select *-locale/*-localedata packages in the next step.")
                pkgTypeList.append(pkgType_locale)
                pkgType_dev = pkgType("dev", False, "If select, you can see/select *-dev packages in the next step.")
                pkgTypeList.append(pkgType_dev)
                pkgType_doc = pkgType("doc", False, "If select, you can see/select *-doc packages in the next step.")
                pkgTypeList.append(pkgType_doc)
                pkgType_dbg = pkgType("dbg", False, "If select, you can see/select *-dbg packages in the next step.")
                pkgTypeList.append(pkgType_dbg)
                pkgType_staticdev = pkgType("staticdev", False, "If select, you can see/select *-staticdev packages in the next step.")
                pkgTypeList.append(pkgType_staticdev)
                pkgType_ptest = pkgType("ptest", False, "If select, you can see/select *-ptest packages in the next step.")
                pkgTypeList.append(pkgType_ptest)
                pkgType_src = pkgType("src", False, "If select, you can see/select *-src packages in the next step.")
                pkgTypeList.append(pkgType_src)
                pkgType_lic = pkgType("lic", False, "If select, you can see/select *-lic packages in the next step.")
                pkgTypeList.append(pkgType_lic)

                return pkgTypeList

            pkgTypeList = __init_pkg_type()
            selected_pkgs = []
            selected_pkgs_spec = []
            pkgs_spec = []
            #init the samples from sample file
            (Flag, sample_list) = self.Read_Samples()
            if Flag == True:
                for sample in sample_list:
                    Custom_actions.append(sample)

            while True:
                #==============================
                # select install type
                #==============================
                if stage == STAGE_INSTALL_TYPE:
                    (stage, selected_pkgs, selected_pkgs_spec, pkgs_spec) = self.installDisp(selected_pkgs, selected_pkgs_spec, pkgs_spec)
                    if stage == STAGE_CUSTOM_TYPE:
                        continue
                # ==============================
                # custom type
                # ==============================
                elif stage == STAGE_CUSTOM_TYPE:
                    (stage, sample_type, custom_type) = self.customDisp()
                    if stage == STAGE_INSTALL_TYPE:
                        continue
                # ==============================
                # record install
                # ==============================
                # Load Package list to install
                elif stage == STAGE_RECORD_INSTALL:
                    stage = self.recordDisp()
                    if stage == STAGE_CUSTOM_TYPE:
                        continue
                # ==============================
                # sample install
                # ==============================
                elif stage == STAGE_SAMPLE_INSTALL:
                    stage = self.sampleDisp(sample_list, sample_type)
                #==============================
                # Grouplist 
                #==============================
                elif stage == STAGE_GROUP:
                    (stage, result, pkg_group) = self.groupDisp()
                    if result == "b" or result == "g":
                        continue
                #==============================
                # select package
                #==============================
                elif stage == STAGE_PACKAGE:
                    (stage, result, selected_pkgs, pkgs_spec, cancel_pkgs, confirm_type) = self.packageDisp(selected_pkgs, custom_type, pkg_group)
                    if result == "b":
                        continue
                    if result == "g":
                        if self.group_flag == True and self.install_type == ACTION_INSTALL:
                            continue
                #==============================
                # select package type
                #==============================
                elif stage == STAGE_PKG_TYPE:
                    (stage, pkgTypeList) = self.pkgTypeDisp(custom_type, pkgTypeList, ypl.installed)
                #==============================
                # select special packages(local, dev, dbg, doc, src)
                #==============================
                elif stage == STAGE_PACKAGE_SPEC:
                    (stage, selected_pkgs_spec, selected_pkgs, cancel_pkgs) = self.packageSpecDisp(pkgTypeList, pkgs_spec, selected_pkgs_spec, custom_type, selected_pkgs)
                # ==============================
                # Select image type
                # ==============================
                elif stage == STAGE_IMAGE_TYPE:
                    stage = self.imageTypeDisp(Image_types)
                    continue
                # ==============================
                # Process function
                # ==============================
                elif stage == STAGE_PROCESS:
                    (result, stage) = self.processDisp(selected_pkgs, selected_pkgs_spec, cancel_pkgs, confirm_type)
                    if result == "b":
                        break

            if self.screen != None:
                StopHotkeyScreen(self.screen)
                self.screen = None

    def _DeleteUpgrade(self,packages=None,display_pkgs=[]):
        haveUpgrade=False
        for i, pkg in enumerate(display_pkgs[:-1]):
            for pkg_oth in display_pkgs[i+1:]:
                if pkg.name==pkg_oth.name:
                    haveUpgrade=True
                    break
            if haveUpgrade :
                break
        ctn=0
        if(haveUpgrade):
            for pkg in packages:
                if  (not pkg.installed) and (pkg in display_pkgs):
                    ctn+=1
                    display_pkgs.remove(pkg)
        return haveUpgrade

    def PkgType_filter(self, display_pkgs, packages, pkgTypeList):
        pkgType_dic= dict()  
        Type_status = False
        for pkgType in pkgTypeList:
            pkgType_dic[pkgType.name] = pkgType.status
            if pkgType.status == True:
                Type_status = True

        if Type_status:
            #Don't show dev, doc, dbg, src, staticdev, doc, lic and ptest packages
            strings_pattern_end = ('-dev', '-doc', '-dbg', '-staticdev', '-ptest', '-src', '-lic')
            for pkg in packages:
                if "-locale-" in pkg.name and not pkgType_dic["locale"]:
                    display_pkgs.remove(pkg)
                elif "-localedata-" in pkg.name and not pkgType_dic["locale"]:
                    display_pkgs.remove(pkg)
                elif pkg.name.endswith(strings_pattern_end):
                    index = pkg.name.rindex('-')
                    string_pattern = pkg.name[index+1:]
                    if not pkgType_dic[string_pattern]:
                        display_pkgs.remove(pkg)

        else:
            display_pkgs = []

        return display_pkgs

    def PKGINSTWindowCtrl(self, pkgTypeList, packages=None, selected_pkgs=[], custom_type=0, pkg_group=[], group_hotkey=False, conflict_attach_pkgs=[]):
        STAGE_SELECT = 1
        STAGE_PKG_TYPE = 2
        STAGE_BACK   = 3
        STAGE_INFO   = 4
        STAGE_EXIT   = 5
        STAGE_SEARCH = 6
        STAGE_NEXT = 7
        STAGE_GROUP = 8

        iTargetSize = 0
        iHostSize = 0

        searched_ret = [] 
        pkgs_spec = []
        cancel_pkgs = []
        position = 0
        search_position = 0
        check = 0
        stage = STAGE_SELECT
        search = None

        hotkey_switch = {"n": STAGE_NEXT, \
                     "b": STAGE_BACK, \
                     "i": STAGE_INFO, \
                     "x": STAGE_EXIT, \
                     "g": STAGE_GROUP, \
                     "r": STAGE_SEARCH}
 
        try:
            ypl = self.base.returnPkgLists(
                self.pkgnarrow, self.patterns, self.installed_available, self.reponame)
        except dnf.exceptions.Error as e:
            return 1, [str(e)]
 
        if pkgTypeList == None:
            pkg_available = copy.copy(ypl.available)
            pkg_installed = copy.copy(ypl.installed)
            packages = ypl.installed + ypl.available
            display_pkgs = pkg_installed + pkg_available
            sorted(packages)
            sorted(display_pkgs)
        else:
            display_pkgs = copy.copy(packages)

        if self.no_gpl3:
            for pkg in packages:
                license = pkg.license
                if license:
                    if "GPLv3" in license:
                        display_pkgs.remove(pkg)
            packages = copy.copy(display_pkgs) #backup all pkgs

        # In special type pkg select interface (round2)
        if pkgTypeList != None:
            display_pkgs = self.PkgType_filter(display_pkgs, packages, pkgTypeList)

            # In package select interface, only display installed packages
            actions = (ACTION_REMOVE, ACTION_UPGRADE, ACTION_GET_PKG, ACTION_GET_SOURCE, ACTION_GET_SPDX, ACTION_GET_ALL)
            if self.install_type in actions:
                for pkg in packages:
                    if pkg not in ypl.installed:
                        if pkg in display_pkgs:
                            display_pkgs.remove(pkg)

            # If there has upgradeable package, show attention window
            elif self.install_type == ACTION_INSTALL:
                if(self._DeleteUpgrade(packages,display_pkgs)):
                    hkey = HotkeyAttentionWindow(self.screen, ATTENTON_HAVE_UPGRADE)

            # No special type pkg selected
            if len(display_pkgs) == 0:
                if self.install_type == ACTION_INSTALL:
                    if custom_type >= RECORD_INSTALL:
                        pkg_installed = ypl.installed
                        selected_pkgs = []
                        selected_pkgs_temp = []
                        selected_pkgs_temp = self.Read_ConfigFile(packages, selected_pkgs_temp)
                        for selected_pkg_temp in selected_pkgs_temp:
                            if selected_pkg_temp not in pkg_installed:
                                #Since it is impossible to deep copy the object list,
                                #if it is not installed, add it to selected_pkgs.
                                selected_pkgs.append(selected_pkg_temp)
                        return ("n", selected_pkgs, packages, cancel_pkgs)
                    conflicts = conflictDetection(self.base, conflict_attach_pkgs)
                    if conflicts != []:
                        (hkey, cancel_pkgs) = HotkeyConflictWindow(self.screen,conflicts)
                        if hkey == "b":
                            return ("b", selected_pkgs, packages, cancel_pkgs)
                        if hkey == "n":
                            return ("n", selected_pkgs, packages, cancel_pkgs)

                else:
                    hkey=HotkeyAttentionWindow(self.screen,ATTENTON_NONE)
                    return ("b", selected_pkgs, packages, cancel_pkgs)
        else:
            # Filter the type pkg such as -dev (Round1)
            if self.install_type == ACTION_INSTALL:
                strings_pattern_end = ('-dev', '-doc', '-dbg', '-staticdev', '-ptest', '-src', '-lic')
                for pkg in packages:
                    if "-locale-" in pkg.name:
                        display_pkgs.remove(pkg)
                        pkgs_spec.append(pkg)
                    elif "-localedata-" in pkg.name:
                        display_pkgs.remove(pkg)
                        pkgs_spec.append(pkg)
                    elif pkg.name.endswith(strings_pattern_end):
                        display_pkgs.remove(pkg)
                        pkgs_spec.append(pkg)

                if(self._DeleteUpgrade(packages,display_pkgs)):
                    hkey = HotkeyAttentionWindow(self.screen, ATTENTON_HAVE_UPGRADE)

                if self.group_flag == True and self.group_botton == True:
                    # Add package into grouplist
                    groupinfo = []
                    for pkg in pkg_group:
                       groupinfo.append(pkg.name)
                    display_pkgs = []
                    for pkg in packages:
                       if pkg.name in groupinfo:
                           display_pkgs.append(pkg)

            #Except install, e.g. remove,spdx,srpm
            else:
                for pkg in packages:
                    if pkg not in ypl.installed:
                        if pkg in display_pkgs:
                            display_pkgs.remove(pkg)
                display_pkgs = sorted(display_pkgs)

            if self.install_type == ACTION_UPGRADE:
                # List the updated available packages
                try:
                    ypl = self.base.returnPkgLists(
                        'upgrades', self.patterns, self.installed_available, self.reponame)
                except dnf.exceptions.Error as e:
                    return 1, [str(e)]

                display_pkgs = []
                if ypl.updates:
                    for pkg in sorted(ypl.updates):
                        display_pkgs.append(pkg)

        if len(display_pkgs)==0:
            if self.install_type==ACTION_INSTALL:
                stage = STAGE_NEXT
            elif self.install_type==ACTION_UPGRADE:
                hkey = HotkeyAttentionWindow(self.screen, ATTENTON_NONE_UPGRADE)
                return ("b", selected_pkgs, packages, cancel_pkgs)
            else:
                hkey = HotkeyAttentionWindow(self.screen, ATTENTON_NONE)
                return ("b", selected_pkgs, packages, cancel_pkgs)

        # Load package file or sample
        if custom_type >= RECORD_INSTALL:
            pkg_installed = ypl.installed
            selected_pkgs = []
            selected_pkgs_temp = []
            selected_pkgs_temp = self.Read_ConfigFile(display_pkgs, selected_pkgs_temp)
            for selected_pkg_temp in selected_pkgs_temp:
                if selected_pkg_temp not in pkg_installed:
                    #Since it is impossible to deep copy the object list,
                    #if it is not installed, add it to selected_pkgs.
                    selected_pkgs.append(selected_pkg_temp)

        while True:
            if stage == STAGE_SELECT:
                if search == None:
                    (hkey, position, pkglist) = PKGINSTPackageWindow(self.screen, \
                                                            display_pkgs, \
                                                            selected_pkgs, \
                                                            position, \
                                                            iTargetSize, \
                                                            iHostSize, \
                                                            search, \
                                                            self.install_type, group_hotkey)
                else:
                    (hkey, search_position, pkglist) = PKGINSTPackageWindow(self.screen, \
                                                             searched_ret, \
                                                             selected_pkgs, \
                                                             search_position, \
                                                             iTargetSize, \
                                                             iHostSize, \
                                                             search, \
                                                             self.install_type, group_hotkey)

                # If there is no groupinfo, show warning
                if hkey == 'g':
                    if self.group_flag == False:
                        AttentionWindow(self.screen, "No group infomation!")
                stage = hotkey_switch.get(hkey, None)

            elif stage == STAGE_NEXT:
                search = None
                #if in packages select Interface:
                if pkgTypeList == None:
                    return ("n", selected_pkgs, pkgs_spec, cancel_pkgs)
                #if in special type packages(dev,doc,locale) select Interface:
                else:
                    if self.install_type == ACTION_INSTALL : confirm_type = CONFIRM_INSTALL
                    conflicts = conflictDetection(self.base, conflict_attach_pkgs,selected_pkgs)
                    if conflicts != []:
                        (hkey, cancel_pkgs) = HotkeyConflictWindow(self.screen,conflicts)
                        if hkey == "b":
                            return ("b", selected_pkgs, packages, cancel_pkgs)
                    return ("n", selected_pkgs, packages, cancel_pkgs)
            elif stage == STAGE_BACK:
                if not search == None:
                    stage = STAGE_SELECT
                    search = None
                else:
                    return ("b", selected_pkgs, pkgs_spec, cancel_pkgs)
            elif stage == STAGE_GROUP:
                if not search == None:
                    stage = STAGE_SELECT
                    search = None
                else:
                    return ("g", selected_pkgs, pkgs_spec, cancel_pkgs)
            elif stage == STAGE_INFO:
                if not search == None:
                    PKGINSTPackageInfoWindow(self.screen, searched_ret[search_position])
                else:
                    PKGINSTPackageInfoWindow(self.screen, display_pkgs[position])
                stage = STAGE_SELECT
            elif stage == STAGE_EXIT:
                hkey = HotkeyExitWindow(self.screen)
                if hkey == "y":
                    if self.screen != None:
                        StopHotkeyScreen(self.screen)
                        self.screen = None
                    sys.exit(0)
                elif hkey == "n":
                    stage = STAGE_SELECT
            elif stage == STAGE_SEARCH:
                search_position = 0
                search = PKGINSTPackageSearchWindow(self.screen)
                if not search == None:
                    def __search_pkgs(keyword, pkgs):
                        searched_pgks = []
                        keyword = re.escape(keyword)
                        for pkg in pkgs:
                            if re.compile(keyword, re.IGNORECASE).search(pkg.name):
                                searched_pgks.append(pkg)
                        return searched_pgks
                    searched_ret = __search_pkgs(search, display_pkgs)
                    if len(searched_ret) == 0:
                        buttons = ['OK']
                        (w, h) = GetButtonMainSize(self.screen)
                        rr = ButtonInfoWindow(self.screen, "Message", "%s - not found." % search, w, h, buttons)
                        search = None
                stage = STAGE_SELECT

    def showChangeSet(self, pkgs_set):
        gplv3_pkgs = []
        #pkgs = self.opts.pkg_specs
        for pkg in pkgs_set:
            license = pkg.license
            if license:
                if "GPLv3" in license:
                    gplv3_pkgs.append(pkg)
        if len(gplv3_pkgs) > 0:
            hkey = ConfirmGplv3Window(self.screen, gplv3_pkgs)
            if hkey == "b":
                return "b"
            elif hkey == "n":
                return "n"
        else:
            return "y"
