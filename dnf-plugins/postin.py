#
# SPDX-License-Identifier: GPL-2.0-only
#

import sys, os, copy, re, string, shutil, hashlib, subprocess
import logging
import dnf
from dnf.cli import commands
from subprocess import call

logger = logging.getLogger('dnf')

class Postinst(commands.Command):
    """A class containing methods to create postinstall scipt.
    """
    def __init__(self, cli=None):
        cli = cli or dnf.cli.Cli()
        self.target_rootfs = None
        self.intercepts_dir = None

    def _initialize_intercepts(self):
        self.target_rootfs = os.environ['HIDDEN_ROOTFS']
        logger.debug("Enter _Initializing intercept,rootfs dir is %s" % self.target_rootfs)
        # As there might be more than one instance of PackageManager operating at the same time
        # we need to isolate the intercept_scripts directories from each other,
        # hence the ugly hash digest in dir name.
        self.intercepts_dir = os.path.join(os.getcwd(), "intercept_scripts-%s" %
                                           (hashlib.sha256(self.target_rootfs.encode()).hexdigest()))
        os.environ["INTERCEPT_DIR"] = self.intercepts_dir
        postinst_intercepts = os.environ["POSTINST_INTERCEPTS"]
        logger.debug("intercepts is %s ", postinst_intercepts)
        if os.path.exists(self.intercepts_dir):
            shutil.rmtree(self.intercepts_dir)
        os.mkdir(self.intercepts_dir)
        for root,dirs,intercepts in os.walk(postinst_intercepts):
            for intercept in intercepts:
                intercept = os.path.join(root,intercept)
                logger.debug("copy intercept= %s to %s", intercept, os.path.join(self.intercepts_dir, os.path.basename(intercept)))
                shutil.copy(intercept, os.path.join(self.intercepts_dir, os.path.basename(intercept)))

    def _script_num_prefix(self, path):
        files = os.listdir(path)
        numbers = set()
        numbers.add(99)
        for f in files:
            numbers.add(int(f.split("-")[0]))
        return max(numbers) + 1

    def save_rpmpostinst(self, pkg):
        logger.debug("Saving postinstall script of %s" % (pkg))
        self.target_rootfs = os.environ['HIDDEN_ROOTFS']

        cmd = "rpm"
        args = ["-q", "--root=%s" % self.target_rootfs, "--queryformat", "%{postin}", pkg]
        logger.debug("******invoke :%s + %s", str([cmd]), str(args))
        try:
            output = subprocess.check_output([cmd] + args,stderr=subprocess.STDOUT).decode("utf-8")
        except subprocess.CalledProcessError as e:
            logger.error("Could not invoke rpm. Command "
                     "'%s' returned %d:\n%s" % (' '.join([cmd] + args), e.returncode, e.output.decode("utf-8")))

        target_path = self.target_rootfs + "/etc/rpm-postinsts/"
        logger.debug("target_path = %s",target_path)
        if not os.path.exists(target_path):
            os.mkdir(target_path)
        num = self._script_num_prefix(target_path)
        saved_script_name = os.path.join(target_path, "%d-%s" % (num, pkg))
        logger.debug("Saving postinstall save output %s",output)
        open(saved_script_name, 'w').write(output)
        logger.debug("Saving postinstall save script of %s", (saved_script_name))
        os.chmod(saved_script_name, 0o755)

    def _handle_intercept_failure(self, registered_pkgs):
        self.target_rootfs = os.environ['HIDDEN_ROOTFS']
        rpm_postinsts_dir = self.target_rootfs + '/etc/rpm-postinsts/'
        if not os.path.exists(rpm_postinsts_dir):
            os.mkdir(rpm_postinsts_dir)
        logger.debug("Enter _handle_intercept_failure")
        # Save the package postinstalls in /etc/rpm-postinsts
        for pkg in registered_pkgs.split():
            logger.debug("_handle_intercept_failure pkg = %s", pkg)
            self.save_rpmpostinst(pkg)
    def _postpone_to_first_boot(self, postinst_intercept_hook):
        logger.debug("Enter__postpone_to_first_boot")
        with open(postinst_intercept_hook) as intercept:
            registered_pkgs = None
            for line in intercept.read().split("\n"):
                m = re.match(r"^##PKGS:(.*)", line)
                if m is not None:
                    registered_pkgs = m.group(1).strip()
                    break
            logger.debug("__postpone_to_first_boot registered_pkgs = %s", registered_pkgs)
            if registered_pkgs is not None:
                logger.debug("If an image is being built, the postinstalls for the following packages "
                        "will be postponed for first boot: %s",registered_pkgs)

                # call the backend dependent handler
                self._handle_intercept_failure(registered_pkgs)

    def run_intercepts(self, populate_sdk=None):
        logger.debug("Running intercept scripts: self.intercepts_dir = %s", self.intercepts_dir)
        self.intercepts_dir = os.environ['INTERCEPT_DIR']
        intercepts_dir = self.intercepts_dir
        for script in os.listdir(intercepts_dir):
            script_full = os.path.join(intercepts_dir, script)
            if script == "postinst_intercept" or not os.access(script_full, os.X_OK):
                continue
            # we do not want to run any multilib variant of this
            if script.startswith("delay_to_first_boot"):
                self._postpone_to_first_boot(script_full)
                continue
            logger.debug("> Executing %s intercept ..." % script)

            try:
                output = subprocess.check_output(script_full, stderr=subprocess.STDOUT)
                if output: logger.debug(output.decode("utf-8"))
            except subprocess.CalledProcessError as e:
                 logger.error("Exit code %d. Output:\n%s" % (e.returncode, e.output.decode("utf-8")))
