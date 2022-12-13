#
# SPDX-License-Identifier: GPL-2.0-only
#

import sys, os, copy, re, string, shutil, hashlib, subprocess
import logging
import dnf
from subprocess import call

logger = logging.getLogger('dnf')

class RpmPM():
    def __init__(self,
                 target_rootfs,
                 target_vendor,
                 task_name='target',
                 arch_var=None,
                 os_var=None,
                 rpm_repo_workdir="oe_repo",
                 filterbydependencies=True,
                 needfeed=True):
        self.target_rootfs = target_rootfs
        self.target_vendor = target_vendor
        self.task_name = task_name
        self.packaging_data_dirs = ['etc/rpm', 'etc/rpmrc', 'etc/dnf', 'var/lib/rpm', 'var/lib/dnf', 'var/cache/dnf']

    def _configure_dnf(self):
        # libsolv handles 'noarch' internally, we don't need to specify it explicitly
        confdir = "%s/%s" %(self.target_rootfs, "etc/dnf/vars/")
        if not os.path.exists(confdir):
            os.makedirs(confdir)
        distro_codename = os.environ['DISTRO_CODENAME']
        open(confdir + "releasever", 'w').write(distro_codename if distro_codename is not None else '')
        open(os.path.join(self.target_rootfs, "etc/dnf/dnf.conf"), 'w').write("")

    def _configure_rpm(self):
        # We need to configure rpm to use our primary package architecture as the installation architecture,
        # and to make it compatible with other package architectures that we use.
        # Otherwise it will refuse to proceed with packages installation.
        platformconfdir = "%s/%s" %(self.target_rootfs, "etc/rpm/")
        rpmrcconfdir = "%s/%s" %(self.target_rootfs, "etc/")
        if not os.path.exists(platformconfdir):
            os.makedirs(platformconfdir)
        with open(platformconfdir + "macros", 'w') as f:
            f.write("%_transaction_color 7\n")
            f.write("%_var /var\n")

        if os.getenv('RPM_PREFER_ELF_ARCH', 'null') != 'null':
            open(platformconfdir + "macros", 'a').write("%%_prefer_color %s" % (os.environ['RPM_PREFER_ELF_ARCH']))

    def create_configs(self):
        self._configure_dnf()
        self._configure_rpm()
