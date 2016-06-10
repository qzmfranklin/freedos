#!/usr/bin/env python3

"""Create bootable FreeDos 1.1 disk image.

Inspired by the following blog:
    https://www.chtaube.eu/computers/freedos/bootable-usb/image-generation-howto

TODO: Cleanup.
"""

import argparse
import atexit
import os
import uuid
import subprocess
import sys
import textwrap
import time

RED  = '\x1b[01;31m'
NONE = '\x1b[00m'

def __download_iso(url, fname):
    if os.path.isfile(fname):
        print("The source image '{}' already exists. Skip downloading.".format(fname))
        return

    tmp_fname = fname + '.tmp'
    cmdlist = [
            'rm -f {}'.format(tmp_fname),
            'wget -q {} --output-document {}'.format(url, tmp_fname),
            'mv {} {}'.format(tmp_fname, fname),
    ]
    for cmd in cmdlist:
        print(RED + cmd + NONE)
        subprocess.check_call(cmd, shell = True)

def __map_device(img_fname):
    """Map image file to device.
    Returns the path to the mapped device.
    """
    # Create device map from partition tables.
    cmd = 'sudo kpartx -av {}'.format(img_fname)
    print(RED + cmd + NONE)
    raw = subprocess.check_output(cmd, shell = True).decode('us-ascii')
    prefix = 'add map '
    if not raw.startswith(prefix):
        raise RuntimeError("The output of command '{}' to stdout is '{}', not starting with '{}'".
                format(cmd, raw, prefix))
    devpath = '/dev/mapper/{}'.format(raw[len(prefix):].split()[0])
    return devpath

def main():
    # TODO: Clean up these variables!
    iso_url = 'http://www.freedos.org/download/download/fd11src.iso'
    iso_fname = '/tmp/freedos-1.1.src.iso' # official 1.1 iso file.
    img_fname = 'dos.img' # the new file we create
    parted_fname = 'dos.parted' # the script fed to parted
    mnt_dir = 'mnt'
    new_dev = os.path.join(mnt_dir, 'mem')     # mount point for the new image
    old_dev = os.path.join(mnt_dir, 'fd11')    # mount point for the free source 1.1 image
    # tmp_dir = '/tmp/create-freedos-bootable-image-{}'.format(uuid.uuid4())
    tmp_dir = '/tmp/freedos-tmp'
    bios_dir = 'bios'    # directory containing the zipped bios files.
    sync_dir = 'sync'

    __download_iso(iso_url, iso_fname)

    def __cleanup():
        cmdlist = [
                'sudo umount {}'.format(new_dev),
                'sleep 0.5',
                'sudo umount {}'.format(old_dev),
                'sleep 0.5',
                'sudo rm -R {}'.format(mnt_dir),
                'sudo rm -rf {}'.format(tmp_dir),
                'sudo kpartx -dv {}'.format(img_fname),
                'sleep 0.5',
        ]
        for cmd in cmdlist:
            print(RED + cmd + NONE)
            subprocess.call(cmd, shell = True)
    atexit.register(__cleanup)

    # Create raw disk image. Create partition table. Create the boot partition.
    cmdlist = [
            # Create raw disk image.
            'dd if=/dev/zero of={} bs=1MiB count=100'.format(img_fname),
            # Create msdos partition table with a bootable fat16 partition. No
            # file system yet. Use dedicated tool, mkfs.fat, to create the file
            # system.
            'cat {} | xargs parted {} -s'.format(parted_fname, img_fname),
    ]
    for cmd in cmdlist:
        print(RED + cmd + NONE)
        subprocess.check_call(cmd, shell = True)

    devpath = __map_device(img_fname)

    # Format the boot partition as FAT16.
    cmdlist = [
            # Create fat16 file system on the boot partition.
            'sudo mkfs.fat -F 16 {}'.format(devpath),
            # Install the syslinux bootloader.
            'sudo syslinux -i {}'.format(devpath),
            # Create the mnt directory
            'mkdir mnt ||  true',
            # Mount the mem device.
            'mkdir -p {1} || true; sudo mount {0} {1}'.format(devpath, new_dev),
            'sleep 0.5',
            # Mount the freedos 1.1 source iso image.
            'mkdir -p {1} || true; sudo mount {0} {1}'.format(iso_fname, old_dev),
            'sleep 0.5',
            # Unpack packages and copy files to the memdisk.
            'mkdir -p {}'.format(tmp_dir),
            'sudo mkdir -p {}/fdos'.format(new_dev),
            'unzip -nq {}/freedos/packages/boot/syslnxx.zip -d {}/fdos'.format(old_dev, tmp_dir),
            'find {}/freedos/packages/base/*.zip | xargs -l unzip -nq -d {}/fdos'.format(old_dev, tmp_dir),
            'sudo cp -r {}/fdos/bin/* {}/fdos/'.format(tmp_dir, new_dev),
            'sudo cp -r {}/fdos/BIN/* {}/fdos/'.format(tmp_dir, new_dev),
            # Install custom configuration files.
            'sudo cp -r sync/* {}/'.format(new_dev),
            # Install flash program, used for upgrading bios.
            'mkdir -p {}/flash'.format(tmp_dir),
            # The supermicro flash zip file
            'mkdir {} || true'.format(bios_dir),
            'find {}/*.zip | xargs -l unzip -nq -d {}/flash || true'.format(bios_dir, tmp_dir),
            'sudo mkdir -p {}/flash'.format(new_dev),
            'sudo cp -r {}/flash/* {}/flash'.format(tmp_dir, new_dev),
    ]
    for cmd in cmdlist:
        print(RED + cmd + NONE)
        subprocess.check_call(cmd, shell = True)

    print(textwrap.dedent("""\
        ================================================================================
                                          READ ME
        ================================================================================
        '{iso}' is not deleted for future use.

        To get the list of commands issued:
            {prog} 2> /dev/null | grep -P '^\\x1b\\[[0-9;]*[mK]' | sed 's:\\x1b\\[[0-9;]*[mK]::g'
        ================================================================================
        """).format(
            iso = iso_fname,
            prog = __file__,
        ))

if __name__ == '__main__':
    main()
