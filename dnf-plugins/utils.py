# Copyright (C) 2016  Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

"""Various utility functions, and a utility class."""

from dnf.cli.format import format_number
from dnf.i18n import _
import dnf.util
import logging
import os
import time
import re, shutil, urllib.request, librepo, filecmp

_USER_HZ = os.sysconf(os.sysconf_names['SC_CLK_TCK'])
logger = logging.getLogger('dnf')

def read_environ(file):
    try:
        with open(file, 'r') as fd:
            lines = fd.readlines()
            for line in lines:
                env = line.rstrip().split('=', 1)
                os.environ[env[0]] = env[1]
    except IOError:
        logger.info(_('Error: Cannot open %s for reading'), self.base.output.term.bold(file))
        sys.exit(1)

def PKG_filter(packages):
    strings_pattern_end = ('-dev', '-doc', '-dbg', '-staticdev', '-ptest')
    notype_pkgs = packages
    for pkg in packages:
        if "-locale-" in pkg.name:
            notype_pkgs.remove(pkg)
        elif "-localedata-" in pkg.name:
            notype_pkgs.remove(pkg)
        elif pkg.name.endswith(strings_pattern_end):
            notype_pkgs.remove(pkg)
    return notype_pkgs

def fetchSPDXorSRPM(option, install_pkgs, srcdir_path, destdir_path):
    """Add for spdx/srpm file cp operation.

    :param option: the file type to be fetch sdpx/srpm.
    :param install_pkgs: The pkgs objexts which will be installed.
    :param srcdir_path:  the repo path of source pkg.
    :param destdir_path:  the destination path of where you want to put your spdx/srpm files. 
    :return: No
    """

    def find_dir(dir_path, file_name):
        for (root, dirs, filenames) in os.walk(dir_path):
            if file_name in filenames:
                found_path = root + '/' + file_name
                return found_path
            else: 
                for dir in dirs:
                    find_dir(root + '/' + dir, file_name)

    def copy_package(option, pkgname):
        #src_path = srcdir_path + '/' + pkgname
        src_path = None
        src_path = find_dir(srcdir_path, pkgname)
        dest_path = destdir_path + '/' + pkgname

        if src_path:
            if os.path.exists(dest_path) and filecmp.cmp(src_path,dest_path):
                logger.info(_("%s already exists."), pkgname)
                return
            try:
                shutil.copyfile(src_path, dest_path)
                logger.info(_("%s copy is OK."), pkgname)
            except Exception as e:
                logger.error(_("%s."), e)
                return
        else:
            logger.warning(_("%s file: %s does not exist....."), option, pkgname)
            return

    def http_download_file(option, pkgname):
        url = srcdir_path + '/' + pkgname
        file_name = destdir_path + '/' + pkgname
        
        try:
            """Example of the simplest usage"""
            fd = os.open(file_name, os.O_RDWR|os.O_CREAT|os.O_TRUNC)
            librepo.download_url(url, fd)
            os.close(fd)
            logger.info(_("%s http download is OK."), pkgname)
        except librepo.LibrepoException as e:
            logger.error(_("%s."), e.args[1])
            os.remove(file_name)
            return

    def ftp_download_file(option, pkgname):
        from ftplib import FTP
        ip = srcdir_path.split('/')[0]
        ftp_path = srcdir_path.replace(ip,'/pub')  + '/' + pkgname
        file_name = destdir_path + '/' + pkgname

        try:
            ftp=FTP()
            ftp.connect(ip) #connect to the ftp server
            ftp.login('','') #login anonymous

            bufsize = 1024 #set the buf size
            file_handler = open(file_name,'wb').write #open the local file
            ftp.retrbinary('RETR ' + ftp_path,file_handler,bufsize) #receive the file from ftp server
            logger.info(_("%s ftp download is OK."), pkgname)
            ftp.quit() #quit the ftp server
        except Exception as e:
            logger.error(_("%s."), e)
            return

    def fetch_package(option, type, pkgname):
        if type == 'local':
            copy_package(option, pkgname)
        elif type == 'remote_http':
            http_download_file(option, pkgname)
        elif type == 'remote_ftp':
            ftp_download_file(option, pkgname)
    
    def local_path_check(path):
        if not os.path.exists(path):
            logger.error(_("local_repodir %s is not exists, please check it."), path)
            return
        else:
            return True

    #Start from here
    srcdir_path = "".join(tuple(srcdir_path))  #transfer a list to string
    '''local fetch'''
    if srcdir_path.startswith('file://') or srcdir_path.startswith('/'):
        type = 'local'
        if srcdir_path.startswith('file://'):
            srcdir_path = dnf.util.strip_prefix(srcdir_path, 'file://')
        if not local_path_check(srcdir_path):
            return
    elif srcdir_path.startswith('http://'):  ##remote fetch
        type = 'remote_http'
    elif srcdir_path.startswith('ftp://'):  ##remote fetch
        type = 'remote_ftp'
        srcdir_path = dnf.util.strip_prefix(srcdir_path, 'ftp://')
    else:
        logger.error(_("The format of %s_repodir is not right, please check it!\nWe only support file:// and http://"), option)   
        return
   
    '''when the destdir_path is not exist, make it'''
    if not os.path.exists(destdir_path):
        try:
            os.mkdir(destdir_path)
        except Exception as e:
            logger.error(_("Create dir failed, %s."), e)
            return
  
    for pkg in sorted(install_pkgs):
        sourcerpm = pkg.sourcerpm
        if option == 'spdx':
            if "-locale" in sourcerpm:
                sourcerpm = sourcerpm.replace('-locale', '')
            match = ''.join(re.findall("-r\d{1,}.src.rpm",sourcerpm))
            '''filter the .src.rpm and r*'''
            spdxname = sourcerpm.replace(match, '') + ".spdx"   
            fetch_package(option, type, spdxname)
        elif option == 'srpm':
            fetch_package(option, type, sourcerpm)
        elif option == 'rpm':
            rpm_name = pkg.name+"-"+pkg.version+"-"+pkg.release+"."+pkg.arch+".rpm"
            fetch_package(option, type, rpm_name)

