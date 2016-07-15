#!/usr/bin/env python

"""dcos-install
Usage:
    dcos-install.py deploy [--dev]
    dcos-install.py destroy [-f | --force]

Options:
    -h --help     Show this screen.
    -f --force    Forcefully destroy the cluster and any data stored there, including the build directory.
"""

import logging
import os
import subprocess

from docopt import docopt
from os.path import expanduser
from shutil import copyfile

home = expanduser("~")
builddir = home + "/dcos-vagrant-build"
uidir = builddir + "/ui"

logging.basicConfig(
    format='%(asctime)s - [%(levelname)s] - %(message)s', level=logging.INFO)
log = logging.getLogger(__name__)

if __name__ == "__main__":
    arguments = docopt(__doc__)

    if arguments["destroy"] == True:
        os.chdir(builddir)
        try:
            subprocess.check_call("vagrant destroy", shell=True)
        except OSError:
            log.error(
                "Looks like I can't use the vagrant command. Check your path, Jim.")

        if arguments["--force"] == True:
            subprocess.check_call("vagrant destroy -f", shell=True)
            try:
                rmtree(builddir)
            except OSError:
                log.error(
                    "More than likely a file was added while trying to remove the directory tree or there are read-only files in there.")
                log.error("Manually delete this directory: " + builddir)

    if arguments["deploy"] == True:
        log.info("Cloning the repo into " + builddir + ".\n")
        try:
            subprocess.check_call(
                "git clone https://github.com/dcos/dcos-vagrant " + builddir, shell=True)
        except OSError:
            if not os.path.isdir(builddir):
                raise
            if os.path.exists(builddir):
                log.error(
                    "The directory already exists, Jim! Remove it or rename it before running this script again.")
                log.error("Looks like git isn't installed, yo.")

        print("\n")
        log.info("Changing working directory to " + builddir + ".")
        os.chdir(builddir)

        log.info(
            "Downloading the dcos_generate_config.sh script to the root of the repo.\n")
        try:
            subprocess.check_call(
                "curl -O https://downloads.dcos.io/dcos/EarlyAccess/dcos_generate_config.sh", shell=True)
        except OSError:
            log.error("Looks like curl isn't installed, yo.")

        log.info("Checking out v0.6.0.")
        subprocess.check_call("git checkout v0.6.0", shell=True)

        print("\n")
        log.info("We need to create a vboxnet0 if it doesn't already exist.")
        try:
            subprocess.check_call(
                "VBoxManage list hostonlyifs | grep vboxnet0 -q || VBoxManage hostonlyif create", shell=True)
        except OSError:
            log.error(
                "Doesn't look like I can get to VBoxManage, Jim. Might wanna check your path.")

        log.info("Set the subnet for vboxnet0 to 192.168.65.1.")
        subprocess.check_call(
            "VBoxManage hostonlyif ipconfig vboxnet0 --ip 192.168.65.1", shell=True)

        log.info("Attempting to install the vagrant-hostmanager plugin.\n")
        subprocess.check_call(
            "vagrant plugin install vagrant-hostmanager", shell=True)

        print("\n")
        log.info(
            "We need to export an environment variable to set the config version.")
        # Note that this is only for the life of the deploy. Once the script
        # exits, this is no longer set.
        os.environ["DCOS_CONFIG_PATH"] = "etc/config-1.7.yaml"

        log.info("Attempting to rename the VagrantConfig file.")
        try:
            copyfile("VagrantConfig.yaml.example", "VagrantConfig.yaml")
        except OSError:
            log.error(
                "Couldn't copy \"VagrantConfig.yaml.example\" to \"VagrantConfig.yaml\"")

        # In case you want to make changes to the UI
        if arguments["[--dev]"] == True:
            subprocess.check_call(
                "git clone https://github.com/dcos/dcos-ui " + uidir, shell=True)

            # Change directory to the newly cloned dcos-ui inside builddir
            os.chdir(uidir)

            try:
                subprocess.check_call("npm install", shell=True)
            except OSError:
                log.error(
                    "Looks like I can't use the npm command. Check your path, Jim.")

            subprocess.check_call("npm run scaffold", shell=True)

        os.chdir(builddir)

        log.info("Attempting to build a 3-node fully-functional cluster...\n")
        subprocess.check_call("vagrant up m1 a1 p1 boot", shell=True)
