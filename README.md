# 1. Introduction
***
Dandified Yum (DNF) is the next upcoming major version of [Yum](http://yum.baseurl.org/). It does package management using [RPM](http://rpm.org/), [libsolv](https://github.com/openSUSE/libsolv) and [hawkey](https://github.com/rpm-software-management/hawkey) libraries. For metadata handling and package downloads it utilizes [librepo](https://github.com/tojaj/librepo). To process and effectively handle the comps data it uses [libcomps](https://github.com/midnightercz/libcomps).

From yocto2.3, rpm5 and smart are replaced by rpm4 and dnf. And this README is for yocto 2.6+.

# 2. Overview
***
Since existing dnf can not be used on cross environment(e.g. a x86 PC with Linux), we developed dnf tui plugin. The following functions have been developed.
  1. Add new command dnf tui --init to make dnf to work on host 
  2. Dnf TUI functions
  3. Manage SPDX files
  4. Manage SRPM files

Now, dnf can be used both on host and target(e.g. an arm board) environment.

# 3. Usage of dnf

## 3.1 On host

### 3.1.1 Prepare

Make sure you have prepared the following:
  * toolchain (mandatory)
  * rpm packages (mandatory)
  * add a config file /etc/dnf/dnf.conf (mandatory in ubuntu)
  * srpm packages (optional)
  * spdx files (optional)

  Note
  - SELinux must be closed.
  - Run as root.

#### (1) toolchain
&emsp;&emsp;install the cross-development toolchain(e.g. for i586: poky-glibc-x86_64-meta-toolchain-i586-toolchain-2.6.sh) and set up environment of toolchain.
```
      # sh poky-glibc-x86_64-meta-toolchain-i586-toolchain-2.6.sh
      # . /opt/poky/2.6/environment-setup-i586-poky-linux
      Note
        - When you compilering toochain, make sure you have patched the patch of patches-yocto.
        - If you change a terminal, you should source toolchain again.
```
#### (2) rpm packages
&emsp;&emsp;Put all packages to one repo directory as following:
```
      # ls /home/test/workdir/dnf_test/oe_repo/rpm
        acl-2.2.52-r0.i586.rpm
        acl-dbg-2.2.52-r0.i586.rpm
        acl-dev-2.2.52-r0.i586.rpm
        ......
```

&emsp;&emsp;If you have a [comps](https://fedoraproject.org/wiki/How_to_use_and_edit_comps.xml_for_package_groups) file for your repo， you can put it to the repo directory    

      # ls /home/test/workdir/dnf_test/oe_repo/rpm
        comps.xml

#### (3) srpm packages
&emsp;&emsp;If you enable "archiver" in you Yocto buid environment, you can get srpm packages for every OSS you build.
```
      # ls /home/test/workdir/dnf_test/srpm_repo
        bash-4.3.30-r0.src.rpm
        ......
```

     
#### (4) spdx files (https://github.com/dl9pf/meta-spdxscanner)
&emsp;&emsp;Please reference to the README of meta-spdxscanner to get spdx files bu Yocto.
```
      # ls /home/test/workdir/dnf_test/spdx_repo
        bash-4.3.30.spdx
        ......
```

### 3.1.2 Initialize

If you want to ctreate an empty rootfs, you have to run "dnf tui --init".

```
# dnf tui --init
Deleting temp rootfs......
=================================================================
Enter repo directory (default: /home/test/dnf/oe_repo): 
You are about to set repo directory to "/home/test/dnf/oe_repo". Are you sure[Y/n]?
```
The system will read the repodata from the directory.

```
=================================================================
Enter rootfs destination directory (default: /opt/ubq/devkit/x86): 
You are about to set rootfs destination directory to "/opt/ubq/devkit/x86". Are you sure[Y/n]?
```
Save the rootfs to rootfs destination directory.

```
=================================================================
Enter SPDX repo directory (default: /home/test/dnf/spdx_repo): 
You are about to set SPDX repo directory to "/home/test/dnf/spdx_repo". Are you sure[Y/n]?
```
Read the SPDX repodata form the directory.

```
=================================================================
Enter SPDX file destination directory (default: /home/test/dnf/spdx_download): 
You are about to set SPDX file destination directory to "/home/test/dnf/spdx_download". Are you sure[Y/n]?
```
Save the SPDX file to the directory.
```
=================================================================
Enter SRPM repo directory (default: /home/test/dnf/srpm_repo): 
You are about to set SRPM repo directory to "/home/test/dnf/srpm_repo". Are you sure[Y/n]?
```
Read the SRPM repodata form the directory.

```
=================================================================
Enter SRPM file destination directory (default: /home/test/dnf/srpm_download): 
You are about to set SRPM file destination directory to "/home/test/dnf/srpm_download". Are you sure[Y/n]?
```
Save the SRPM file to the directory.

```
=================================================================
Enter RPM repo directory (default: /home/test/dnf/oe_repo): 
You are about to set RPM repo directory to "/home/test/dnf/oe_repo". Are you sure[Y/n]?
```
Read the RPM repodata form the directory.

```
=================================================================
Enter RPM file destination directory (default: /home/test/dnf/rpm_download): 
You are about to set RPM file destination directory to "/home/test/dnf/rpm_download". Are you sure[Y/n]?
```
Save the RPM file to the directory.

```
 /home/test/dnf/.rootfs-x86 is not exist. mkdir /home/test/dnf/.rootfs-x86. 
Creating repo ...

Scanning repo ...
progress:[##################################################]100%
Scanning finish
#

  Note
    - Because dnf tui reads configuration from `pwd`, please make sure the above steps are in the same directory same as you run init.
    - Dnf tui will save what you have done until you run init again.
```

After init, then, you can manage packages by TUI or command line.

### 3.1.3 Manage packages in TUI

  Dnf TUI(textual user interface) Function is developed for dnf. With TUI, it is easy to customize rootfs of target.
  <br/>Note
  <br/>&emsp;- Please make sure your screen is at least 24 lines and 80 columns.
  <br/>&emsp;- In "Confirm" interface and "License" interface, you can use "←" or "→" to choose "Yes" or "No", and use "Enter" to confirm. "F4" can help you back to previous interface.

  By the following command you can enter the main interface of TUI.
  ``` 
      # dnf tui
        ┌────────────────────────┤ Select your operation ├─────────────────────────┐
        │                                                                          │
        │ Install  --->                                                            │
        │ Remove  --->                                                             │
        │ Upgrade  --->                                                            │
        │ Create binary package archives(rpm)  --->                                │
        │ Create a source archive(src.rpm)  --->                                   │
        │ Create an spdx archive(spdx)  --->                                       │
        │ Create archive(rpm, src.rpm and spdx files)  --->                        │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        └──────────────────────────────────────────────────────────────────────────┘
	
        F5:Info  F9:Exit

```
#### 3.1.3.1 install
&emsp;&emsp; After enter into "install",the tui will list some ways for user to install package.
```
        ┌─────────────────────────┤ Select install type ├──────────────────────────┐
        │                                                                          │
        │ New  --->                                                                │
        │ Load package file  --->                                                  │
        │ Reference1(busybox based root file system)  --->                         │
        │ Reference2(systemd based root file system)  --->                         │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        └──────────────────────────────────────────────────────────────────────────┘

        F4:Back  F5:Info  F9:Exit
	
	Note
          - New : user can use it to install new package.
          - Load package file : package samples for user.
	  - Reference : Now we predefined two samples for base root file system. When you choose busybox, 
	    these packages will be installed in your rootfs, it’s a minimal bootable rootfs with busybox 
	    as the initialization manager.

```
##### (1). dnf TUI can help you filter GPLv3
&emsp;&emsp;If you select "install" and "NEW" in above, dnf tui will ask you whether you want to install packages
	 with license of GPLv3.
```	 

                  ┌───────────────┤ License ├────────────────┐
                  │                                          │
                  │                                          │
                  │  Do you want to display GPLv3 packages?  │
                  │                                          │
                  │                                          │
                  │ ---------------------------------------- │
                  │          ┌───────┐   ┌──────┐            │
                  │          │  Yes  │   │  No  │            │
                  │          └───────┘   └──────┘            │
                  │                                          │
                  └──────────────────────────────────────────┘


       - No  : GPLv3 packages will not be selected and not display in the next step.
       - Yes : GPLv3 packages can be selected as same as the other packages.
 ```

 ##### (2). customize packages
```
        ┌────────────────────────────┤ Select package ├────────────────────────────┐
        │                                                                          │
        │ [I] base-files                                                         ↑ │
        │ [I] ncurses-terminfo-base                                              ▮ │
        │ [I] libc6                                                              ▒ │
        │ [I] libacl1                                                            ▒ │
        │ [I] libattr1                                                           ▒ │
        │ [I] update-alternatives-opkg                                           ▒ │
        │ [I] bash                                                               ▒ │
        │ [I] acl                                                                ▒ │
        │ [I] libtinfo5                                                          ▒ │
        │ [*] attr                                                               ▒ │
        │ [*] base-passwd                                                        ▒ │
        │ [ ] base-passwd-update                                                 ▒ │
        │ [ ] bash-bashbug                                                       ↓ │
        │ ------------------------------------------------------------------------ │
        │ All Packages [3935]    Installed Packages [9]    Selected Packages [2]   │
        │                                                                          │
        └──────────────────────────────────────────────────────────────────────────┘

        F1:select/unselect All  F2:Search  F3:Next  F4:Back  F5:Info  F9:Exit

         Note
            - []  Means the package has not been selected or installed. If you want to install it, you can
                  select it by pressing Space or Enter.
            - [*] Means the package has been selected and will be installed. If you don't want to install it,
                  you can cancel by pressing Space or Enter.
            - [I] Means the package has been installed in your rootfs.

```

##### (3). customize packages type
&emsp;&emsp;You can select the package type that you want to install into rootfs.
```
        ┌───────────────────┤ Customize special type packages ├────────────────────┐
        │                                                                          │
        │ locale [ ]                                                               │
        │ dev [ ]                                                                  │
        │ doc [ ]                                                                  │
        │ dbg [ ]                                                                  │
        │ staticdev [ ]                                                            │
        │ ptest [ ]                                                                │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        └──────────────────────────────────────────────────────────────────────────┘
	
	F3:Next  F4:Back  F5:Info  F9:Exit 
	
	-  locale : Language pack
        -  dev : provide header files for other software
	-  doc : document
	-  dbg : debug file
	-  staticdev ：static compilation file
	-  ptest : Python unit testing framework
	
```
##### (4). Confirm install
&emsp;&emsp;If you select "No" in the "license" interface, but there is GPLV3 packages in the dependencies,
<br>&emsp;&emsp;a dialog box will ask your decision.
```
        ┌────────────────────────┤ GPLv3 that be depended ├────────────────────────┐
        │                                                                          │
        │ bash                                                                     │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │ ------------------------------------------------------------------------ │
        │ These GPLv3 packages are depended                                        │
        └──────────────────────────────────────────────────────────────────────────┘
	
	F3:Next  F4:Back  F9:Exit

```
##### (5). Load package file
&emsp;&emsp;After select "Load package file", when user enter the name of configuration file and enter
"OK", dnf tui will install the package which the configuration list.
```

           ┌──────────────────┤   Config File   ├───────────────────┐
           │                                                        │
           │ Enter the name of configuration file you wish to load: │
           │                                                        │
           │   .config___________________________________________   │
           │                                                        │
           │              ┌──────────┐   ┌──────────┐               │
           │              │    OK    │   │  Cancel  │               │
           │              └──────────┘   └──────────┘               │
           │                                                        │
           │                                                        │
           └────────────────────────────────────────────────────────┘
```

##### (6). Reference   
&emsp;&emsp;In "Select install type" interface, user can choose Reference1 to install busybox based root 
file system or Reference2 to install systemd based root file system.
```
                  ┌───────────┤ Confirm install ├────────────┐
                  │                                          │
                  │                                          │
                  │  Do you want to begin installation?      │
                  │                                          │
                  │                                          │
                  │ ---------------------------------------- │
                  │          ┌───────┐   ┌──────┐            │
                  │          │  Yes  │   │  No  │            │
                  │          └───────┘   └──────┘            │
                  │                                          │
                  └──────────────────────────────────────────┘
```
#### 3.1.3.2 Remove
&emsp;&emsp;You can choose the package that you want to upgrade after enter "Remove" in main interface.
```
        ┌────────────────────────────┤ Select package ├────────────────────────────┐
        │                                                                          │
        │ [-] libc6                                                                │
        │ [-] ncurses-terminfo-base                                                │
        │ [-] acl                                                                  │
        │ [ ] libacl1                                                              │
        │ [ ] libtinfo5                                                            │
        │ [ ] base-files                                                           │
        │ [ ] update-alternatives-opkg                                             │
        │ [ ] bash                                                                 │
        │ [ ] libattr1                                                             │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │ ------------------------------------------------------------------------ │
        │ All Packages [9]    Selected Packages [0]                                │
        │                                                                          │
        └──────────────────────────────────────────────────────────────────────────┘
	
	F1:select/unselect All  F2:Search  F3:Next  F4:Back  F5:Info  F9:Exit
	
	Note
          - []  Means the package could be upgrade and has not been selected. If you want to upgrade it, you can
                select it by pressing Space or Enter.
          - [-] Means the package has been selected, installed and will be removed.

```
#### 3.1.3.3 Upgrade
&emsp;&emsp;You can choose the package that you want to upgrade after enter "Upgrade" in main interface.
```
        ┌────────────────────────────┤ Select package ├────────────────────────────┐
        │                                                                          │
        │ [U] base-files                                                           │
        │ [U] bash                                                                 │
        │ [U] ncurses-terminfo-base                                                │
        │ [ ] libtinfo5                                                            │
        │ [ ] update-alternatives-opkg                                             │
        │ [ ] libc6                                                                │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │ ------------------------------------------------------------------------ │
        │ All Packages [6]    Selected Packages [0]                                │
        │                                                                          │
        └──────────────────────────────────────────────────────────────────────────┘
	
	F1:select/unselect All  F2:Search  F3:Next  F4:Back  F5:Info  F9:Exit
	
        Note
          - []  Means the package could be upgrade and has not been selected. If you want to upgrade it, you can
                select it by pressing Space or Enter.
          - [U] Means the package has been selected, installed and will be upgraded.
```
#### 3.1.3.4 manage source archive & spdx archive
&emsp;&emsp;You can choose the package that you want to get spdx/srpm archive after enter "Create spdx archive" or "Create spdx archive" in main interface.
```
        ┌────────────────────────────┤ Select package ├────────────────────────────┐
        │                                                                          │
        │ [S] base-files                                                           │
        │ [S] base-passwd                                                          │
        │ [S] busybox                                                              │
        │ [ ] busybox-syslog                                                       │
        │ [ ] busybox-udhcpc                                                       │
        │ [ ] busybox-udhcpd                                                       │
        │ [ ] libc6                                                                │
        │ [ ] update-alternatives-opkg                                             │
        │ [ ] update-rc.d                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │ ------------------------------------------------------------------------ │
        │ All Packages [9]    Selected Packages [3]                                │
        │                                                                          │
        └──────────────────────────────────────────────────────────────────────────┘

        F1:select/unselect All  F2:Search  F3:Next  F4:Back  F5:Info  F9:Exit

        Note
          - []  Means the package has not been selected.
          - [S] Means the package has been selected, installed and will be used to created.
```
#### 3.1.3.5 manage binary package archives
&emsp;&emsp;You can choose the package that you want to get binary package archive after enter "Create binary package archives(rpm)" in main interface.
```
        ┌────────────────────────────┤ Select package ├────────────────────────────┐
        │                                                                          │
        │ [R] base-files                                                           │
        │ [R] base-passwd                                                          │
        │ [R] busybox                                                              │
        │ [ ] busybox-syslog                                                       │
        │ [ ] busybox-udhcpc                                                       │
        │ [ ] busybox-udhcpd                                                       │
        │ [ ] libc6                                                                │
        │ [ ] update-alternatives-opkg                                             │
        │ [ ] update-rc.d                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │ ------------------------------------------------------------------------ │
        │ All Packages [9]    Selected Packages [3]                                │
        │                                                                          │
        └──────────────────────────────────────────────────────────────────────────┘

        F1:select/unselect All  F2:Search  F3:Next  F4:Back  F5:Info  F9:Exit

        Note
          - []  Means the package has not been selected.
          - [R] Means the package has been selected, installed and will be used to created.
```
#### 3.1.3.6 manage archive
&emsp;&emsp;You can choose the package that you want to get archive after enter "Create archive(rpm, src.rpm and spdx files)" in main interface.
```
        ┌────────────────────────────┤ Select package ├────────────────────────────┐
        │                                                                          │
        │ [A] base-files                                                           │
        │ [A] base-passwd                                                          │
        │ [A] busybox                                                              │
        │ [ ] busybox-syslog                                                       │
        │ [ ] busybox-udhcpc                                                       │
        │ [ ] busybox-udhcpd                                                       │
        │ [ ] libc6                                                                │
        │ [ ] update-alternatives-opkg                                             │
        │ [ ] update-rc.d                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │                                                                          │
        │ ------------------------------------------------------------------------ │
        │ All Packages [9]    Selected Packages [3]                                │
        │                                                                          │
        └──────────────────────────────────────────────────────────────────────────┘

        F1:select/unselect All  F2:Search  F3:Next  F4:Back  F5:Info  F9:Exit

        Note
          - []  Means the package has not been selected.
          - [A] Means the package has been selected, installed and will be used to created.
```

### 3.1.4 Manage srpm or spdx file by command line

After init, if you want to manage srpm or spdx files without installation, you can use the subcommands as following:
<br>(1) fetchsrpm
```
      # dnf fetchsrpm bash
      ......
      # ls srpm_download/
      bash-4.3.30.src.rpm
```
  (2) fetchspdx
<br>&emsp;&emsp;fetchsrpm is the same as fetchspdx

```	
      # dnf fetchspdx bash 
      ......
      # ls spdx_download/
      bash-4.3.30.spdx
```

### 3.1.5 Automatically complete installation in command-line

After init, if you want to install packages automatically, you can use the subcommands as following:
```
      # dnf tui --auto -i list         //Here list is the package list file
      ......
      Installed:
      acl.i586 2.2.52-r0                                            bash.i586 4.3.30-r0
      ncurses-terminfo-base.i586 6.0+20161126-r0                    base-files.qemux86 3.0.14-r89
      libacl1.i586 2.2.52-r0                                        libattr1.i586 2.4.47-r0
      libc6.i586 2.25-r0                                            libtinfo5.i586 6.0+20161126-r0
      update-alternatives-opkg.i586 0.3.4+git0+1a708fd73d-r0
    
      Complete!
      Unable to detect release version (use '--releasever' to specify release version)
      Last metadata expiration check: 0:00:04 ago on Wed 19 Dec 2018 12:31:38 PM UTC.
      acl-2.2.52-r0.i586.rpm copy is OK.
      bash-4.3.30-r0.i586.rpm copy is OK.
      acl-2.2.52-r0.src.rpm already exists.
      bash-4.3.30-r0.src.rpm copy is OK.
      acl-2.2.52.spdx already exists.
      spdx file: bash-4.3.30.spdx does not exist.....
      Dependencies resolved.
      Nothing to do.
      Complete!
      Prepare rootfs
      progress:[##################################################]100%
      Put rootfs to destination
      progress:[##################################################]100%
      Do you like to keep the tar file.[Y/n]?
      y
      The tarball is /home/test/workdir/dnf-test/rootfs-poky-201812190433.tar.bz2
      Target dir is /opt/ubq/devkit/x86/rootfs-poky-201812190433
        
      # ls /opt/ubq/devkit/x86/rootfs-poky-201812190433
      bin  boot  dev  etc  home  lib  media  mnt  proc  run  sbin  sys  tmp  usr  var
```

## 3.2 On target

### 3.2.1  Configuration

#### (1) configure rpm repo (mandatory)  
&emsp;&emsp;The same as using dnf on the other Distro (e.g. Fedora), you have to configure your rpm repo in /etc/yum.repos.d/Base.repo.

### 3.2.2 Usage

The same as dnf.

# 4. Documentation

***
If you want to know more knowledge about dnf, read the documentation of dnf.
The DNF package distribution contains man pages, dnf(9) and dnf.conf(8). It is also possible to [read the DNF documentation](http://dnf.readthedocs.org/)online, the page includes API documentation. There's also a [wiki](https://github.com/rpm-software-management/dnf/wiki) meant for contributors to DNF and related projects.
