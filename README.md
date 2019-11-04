# 1. Introduction
***
dnf tui plugin to use with [DNF package manager](https://github.com/rpm-software-management/dnf) in [yocto project](https://www.yoctoproject.org/).

# 2. Overview
***
Since existing dnf can not be used on cross environment(e.g. a x86 PC with Linux), we developed dnf tui plugin and include it in toolchain of yocto to make dnf work on host. 
The following functions have been developed.
  1. Add new command dnf tui --init to make dnf to work on host 
  2. Text-based user interface for dnf
  3. Manage SPDX files
  4. Manage SRPM files

Now, dnf can be used both on host and target(e.g. an arm board) environment.
This README is for yocto 3.0+.

# 3. Usage of dnf tui plugin
***
## 3.1 On host

### 3.1.1 Prepare

Make sure you have prepared the following:
  * toolchain (mandatory)
  * rpm packages (mandatory)
  * config file /etc/dnf/dnf.conf (mandatory in ubuntu)
  * srpm packages (optional)
  * spdx files (optional)

  Note
  - SELinux must be closed.
  - Run as root.
  - If you want to make filesystem image, ensure following tools are exist on your host:
    1. mtd-utils(Ubuntu), e2fsprogs(Fedora)
    2. squashfs-tools
  - Do not run two processes of dnf in one directory at the same time, as some temp files may be covered.

#### (1) toolchain
&emsp;&emsp;Before using dnf tui plugin, you should bitbake the cross-development toolchain by Yocto.

&emsp;&emsp;Checkout poky and meta-oe to stable version.

```
      $ git clone git://git.yoctoproject.org/poky
      $ cd poky
      $ git checkout origin/zeus -b zeus
      
      $ git clone git://git.openembedded.org/meta-openembedded
      $ cd meta-openembedded
      $ git checkout origin/zeus -b zeus
```
&emsp;&emsp;Before creating toolchain. Plese apply the patch in patches-yocto because this patch has not been merged by Yocto yet. We are trying to push this patch to the Yocto community.

```
      $ cd poky
      $ patch -p1 < 0001-poky-3.0-PATCH-Added-MACHINE_ARCH-in-toolchain.patch

```
&emsp;&emsp;Bitbake meta-toolchain.

```
      $ source poky/oe-init-build-env build/
      $ tail -n 2 conf/local.conf
      # Add dnf-plugin-tui and createrepo-c into toolchain.
      TOOLCHAIN_HOST_TASK_append = " nativesdk-dnf-plugin-tui nativesdk-createrepo-c"

      $ bitbake meta-toolchain 
      $ ls tmp/deploy/sdk/poky-glibc-x86_64-meta-toolchain-core2-64-qemux86-64-toolchain-3.0.sh
```
&emsp;&emsp;Copy toolchain script to your host and install.

```
      # sh poky-glibc-x86_64-meta-toolchain-core2-64-qemux86-64-toolchain-3.0.sh
```

&emsp;&emsp;Before using dnf，Please set up the environment of crosscompile. 
```
      # . /opt/poky/3.0/environment-setup-core2-64-poky-linux
```
```
      Note
        - If you want to use dnf on the other terminal, please source the environment script again.
```
#### (2) rpm packages
&emsp;&emsp;Put all packages to one repo directory as following:
```
      # ls /home/test/workdir/dnf_test/oe_repo/rpm
        acl-2.2.52-r0.core2_64.rpm
        acl-dbg-2.2.52-r0.core2_64.rpm
        acl-dev-2.2.52-r0.core2_64.rpm
        ......
```

&emsp;&emsp;If you have a [comps](https://fedoraproject.org/wiki/How_to_use_and_edit_comps.xml_for_package_groups) file for your repo, you can put it to the repo directory.

      # ls /home/test/workdir/dnf_test/oe_repo/rpm
        comps.xml

#### (3) srpm packages
&emsp;&emsp;If you enable "archiver" in you Yocto build environment, you can get srpm packages for every OSS you build.
```
      # ls /home/test/workdir/dnf_test/srpm_repo
        bash-5.0-r0.src.rpm
        ......
```
     
#### (4) spdx files (https://github.com/dl9pf/meta-spdxscanner)
&emsp;&emsp;Please refer to the README of meta-spdxscanner to get spdx files produced by Yocto.
```
      # ls /home/test/workdir/dnf_test/spdx_repo
        bash-4.3.30.spdx
        ......
```

### 3.1.2 Initialize

If you want to create an empty rootfs, you have to run "dnf tui --init".

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
Read the SPDX repodata from the directory.

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
Read the SRPM repodata from the directory.

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
Read the RPM repodata from the directory.

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
```
```
  Note
    - Because dnf tui reads configuration from `pwd`, please make sure dnf tui runs in the same directory as you run init.
    - Dnf tui will save what you have done until you run init again.
```

After init, you can manage packages by tui or command line.

### 3.1.3 Manage packages in tui

  Dnf tui(textual user interface) Function is developed for dnf. With tui, it is easy to customize rootfs for target.
  <br/>Note
  <br/>&emsp;- Please make sure your screen is at least 24 lines and 80 columns.
  <br/>&emsp;- In "Confirm" interface and "License" interface, you can use "←" or "→" to choose "Yes" or "No", and use "Enter" to confirm. "F4" can help you back to previous interface.

  By the following command you can enter the main interface of tui.
  ``` 
      # dnf tui
        ┌────────────────────────┤ Select your operation ├─────────────────────────┐
        │                                                                          │
        │ Install  --->                                                            │
        │ Remove  --->                                                             │
        │ Upgrade  --->                                                            │
        │ Create binary package archives  --->                                     │
        │ Create a source archive  --->                                            │
        │ Create an spdx archive  --->                                             │
        │ Create archive(rpm, src.rpm and spdx files)  --->                        │
        │ Make filesystem image  --->                                              │
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
&emsp;&emsp; After enter into "install", the tui will list some ways for user to install package.
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
```
```
	Note
          - New : user can use it to install new package.
          - Load package file : package list for user.
	  - Reference : Now we predefined two samples for base root file system. When you choose busybox,
	    these packages will be installed in your rootfs, it’s a minimal bootable rootfs with busybox
	    as the initialization manager.

```
##### (1). filter GPLv3
&emsp;&emsp;If you select "install" and "New" in above, dnf tui will ask you whether you want to install packages
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
```
```
       - No  : GPLv3 packages will not be selected and displayed in the next step.
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
```
```
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
```
```
	-  locale : Language package
        -  dev : Provide header files for other software
	-  doc : Document
	-  dbg : Debug file
	-  staticdev : Static compilation file
	-  ptest : Python unit testing framework
```
##### (4). Confirm install
&emsp;&emsp;If you select "No" in the "License" interface, but there are GPLv3 packages in the dependencies,
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
&emsp;&emsp;After select "Load package file", when user enter the name of package list file and enter
"OK", dnf tui will install the package which in the list.
```

           ┌──────────────────┤   Config File   ├───────────────────┐
           │                                                        │
           │ Enter the name of package list file you wish to load:  │
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
&emsp;&emsp;You can choose the package that you want to remove after entering "Remove" in main interface.
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
```
```
	Note
          - []  Means the package could be removed and has not been selected. 
                If you want to remove it, you can select it by pressing Space or Enter.
          - [-] Means the package has been selected, installed and will be removed.

```
#### 3.1.3.3 Upgrade
&emsp;&emsp;You can choose the package that you want to upgrade after entering "Upgrade" in main interface.
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
```
```
        Note
          - []  Means the package could be upgraded and has not been selected. 
                If you want to upgrade it, you can select it by pressing Space or Enter.
          - [U] Means the package has been selected, installed and will be upgraded.
```
#### 3.1.3.4 manage binary package archives
&emsp;&emsp;You can choose the package that you want to get binary package archive after entering "Create binary package archives" in main interface.
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
```
```
        Note
          - []  Means the package has not been selected.
          - [R] Means the package has been selected, installed and will be created.
```
#### 3.1.3.5 manage source archive & spdx archive
&emsp;&emsp;You can choose the package that you want to get spdx/srpm archive after entering "Create spdx archive" or "Create source archive" in main interface.
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
```
```
        Note
          - []  Means the package has not been selected.
          - [S] Means the package has been selected, installed and will be created.
```
#### 3.1.3.6 manage archive
&emsp;&emsp;You can choose the package that you want to get archive after entering "Create archive(rpm, src.rpm and spdx files)" in main interface.
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
```
```
        Note
          - []  Means the package has not been selected.
          - [A] Means the package has been selected, installed and will be created.
```
#### 3.1.3.7 Make filesystem image
&emsp;&emsp;You can choose the filesystem image which you want to make after entering "Make filesystem image" in main interface.
```
        ┌──────────────────────────┤ Select Image type ├───────────────────────────┐
        │                                                                          │
        │ JFFS2  --->                                                              │
        │ INITRAMFS  --->                                                          │
        │ INITRD  --->                                                             │
        │ RAW  --->                                                                │
        │ SquashFS  --->                                                           │
        │ UBIFS  --->                                                              │
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
```
##### (1) JFFS2 image
&emsp;&emsp;Select JFFS2 in "Select Image type" to make JFFS2 image.
```
        ┌───────────────────┤ JFFS2 Parameter ├───────────────────┐
        │                                                         │
        │   From directory   : /home/test/rootfs____________      │
        │   To directory     : /home/test/image-dir_________      │
        │   Image size       : 10M_________bytes                  │
        │   Page size        : 4K__________bytes                  │
        │   Erase block size : 256K________bytes                  │
        │   Endian(Default is little) :  [ ] Big endian           │
        │                                                         │
        │                   ┌────┐   ┌──────┐                     │
        │                   │ OK │   │ Back │                     │
        │                   └────┘   └──────┘                     │
        │                                                         │
        └─────────────────────────────────────────────────────────┘
```
```

        Note
          - From directory:
            The directory of root filesystem you made before.
          - To directory:
            The path where you want to put your image file.
          - Image size:
            Must bigger than the size of root filesystem you enter in "From directory".
          - Page size and Erase block size:
            Can obtain from mtdinfo.

          Here is an example from an embedded board:
          ~# mtdinfo /dev/mtd0
          mtd0
          Type:                           nand
          Eraseblock size:                262144 bytes, 256.0 KiB  (Erase block size) ★
          Amount of eraseblocks:          2048 (536870912 bytes, 512.0 MiB)
          Minimum input/output unit size: 4096 bytes    (Page size) ★
          Sub-page size:                  4096 bytes

          - Endian:
            Create little-endian or big-endian filesystem.
```

##### (2) INITRAMFS image
&emsp;&emsp;Select INITRAMFS in "Select Image type" to make INITRAMFS image.
```
        ┌─────────────────┤ INITRAMFS Parameter ├─────────────────┐
        │                                                         │
        │   From directory   : /home/test/rootfs____________      │
        │   To directory     : /home/test/image-dir_________      │
        │                                                         │
        │                   ┌────┐   ┌──────┐                     │
        │                   │ OK │   │ Back │                     │
        │                   └────┘   └──────┘                     │
        │                                                         │
        └─────────────────────────────────────────────────────────┘
```

##### (3) INITRD image
&emsp;&emsp;Select INITRD in "Select Image type" to make INITRD image.
```
        ┌──────────────────┤ INITRD Parameter ├───────────────────┐
        │                                                         │
        │   From directory  :  /home/test/rootfs_____________     │
        │   To directory    :  h/image-dir/rootfs.initrd.bin_     │
        │   Image size      :  10m___________bytes                │
        │   Use loop device :  /dev/loop0_____                    │
        │   Use mount point :  /mnt___________                    │
        │                                                         │
        │                   ┌────┐   ┌──────┐                     │
        │                   │ OK │   │ Back │                     │
        │                   └────┘   └──────┘                     │
        │                                                         │
        └─────────────────────────────────────────────────────────┘
```

##### (4) RAW image
&emsp;&emsp;Select RAW in "Select Image type" to make RAW image.
```
        ┌────────────────────┤ RAW Parameter ├────────────────────┐
        │                                                         │
        │   From directory  :  /home/test/rootfs_____________     │
        │   To directory    :  /test/image-dir/rootfs.raw.bin_    │
        │   Filesystem type :  ext4___________                    │
        │   Image size      :  10m___________bytes                │
        │   Use loop device :  /dev/loop0_______                  │
        │   Use mount point :  /mnt___________                    │
        │                                                         │
        │                   ┌────┐   ┌──────┐                     │
        │                   │ OK │   │ Back │                     │
        │                   └────┘   └──────┘                     │
        │                                                         │
        └─────────────────────────────────────────────────────────┘

```
```
        Note
          - Filesystem type can be ext2/ext3/ext4.
```

##### (5) SquashFS image
&emsp;&emsp;Select SquashFS in "Select Image type" to make SquashFS image.
```
        ┌─────────────────┤ SquashFS Parameter ├──────────────────┐
        │                                                         │
        │   From directory  :  /home/test/rootfs____________      │
        │   To directory    :  /home/test/image-dir_________      │
        │   Block size         4K_____________bytes               │
        │                                                         │
        │                   ┌────┐   ┌──────┐                     │
        │                   │ OK │   │ Back │                     │
        │                   └────┘   └──────┘                     │
        │                                                         │
        └─────────────────────────────────────────────────────────┘
```

##### (6) UBIFS image
&emsp;&emsp;Select UBIFS in "Select Image type" to make UBIFS image.
```
        ┌────────────────────┤ UBIFS Parameter ├─────────────────────┐
        │                                                            │
        │   From directory  :  /home/test/rootfs________________     │
        │   To directory    :  /home/test/image-dir_____________     │
        │   Minimum I/O unit size             : 4k_____________bytes │
        │   Logical erase block size( > 15360): 248k___________bytes │
        │   Maximum logical erase block count : 2048___________count │
        │   Id of UBIFS device :                0______________      │
        │   Name of UBIFS Volume :              rootfs_________      │
        │                                                            │
        │                     ┌────┐   ┌──────┐                      │
        │                     │ OK │   │ Back │                      │
        │                     └────┘   └──────┘                      │
        │                                                            │
        └────────────────────────────────────────────────────────────┘

```
```
	Note
          -  Minimum I/O unit size:
	     Obtain from mtdinfo.
          -  Logical erase block size:
             Calculated in this way: (Eraseblock size) - (Minimum input/output unit size)*2 = 256k - 4k*2 = 248k
          -  Maximum logical erase block count:
	     Obtain from mtdinfo named Amount of eraseblocks.

          For example:
          ~# mtdinfo /dev/mtd0
          mtd0
          Type:                           nand
          Eraseblock size:                262144 bytes, 256.0 KiB
          Amount of eraseblocks:          2048 (536870912 bytes, 512.0 MiB)    （Maximum logical erase block count） ★
          Minimum input/output unit size: 4096 bytes                           （Minimum I/O unit size）★
          Sub-page size:                  4096 bytes
```

### 3.1.4 Manage packages by command line

After init, you can use dnf tui command line to manage packages. 

```
      # dnf tui --command list  
      # dnf tui --command search <spec>   
      # dnf tui --command info <spec>   
      # dnf tui --command repolist  
      # dnf tui --command install <spec>   
      # dnf tui --command remove <spec>   
      # dnf tui --command upgrade <spec>   
```
     
#### 3.1.4.1 New options of 'dnf tui --command'.
##### (1) --nosave
&emsp;&emsp;.config is used to save installed packages. Every time after install, remove or upgrade, dnf tui will automatically update .config file.
```
      # cat .config 
        base-files
        bash
        ......
```
```
	Note
          .config is saved in `pwd`.
```
&emsp;&emsp;If you don't want to update .config file, you can add --nosave option.
<br>&emsp;&emsp;e.g.
```
      # dnf tui --command install bash --nosave
      # dnf tui --command remove bash --nosave
```
##### (2) --pkg_list [file]
&emsp;&emsp;'--pkg_list' is used to manage packages that list in the file.
<br>&emsp;&emsp;e.g.
```
      # dnf tui --command install --pkg_list pkg.list   //Install packages that list in pkg.list
      # dnf tui --command remove --pkg_list pkg.list   //Remove packages that list in pkg.list
```

### 3.1.5 Manage srpm or spdx file by command line

After init, if you want to manage srpm or spdx files without installation, you can use the subcommands as following:
#### (1) fetchsrpm
```
      # dnf fetchsrpm bash
      ......
      # ls srpm_download/
      bash-4.3.30.src.rpm
```
#### (2) fetchspdx
```	
      # dnf fetchspdx bash 
      ......
      # ls spdx_download/
      bash-4.3.30.spdx
```

## 3.2 On target
TODO
