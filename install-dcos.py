#!/usr/bin/env python

import os
from os.path import expanduser
import subprocess
import logging

home = expanduser("~")
builddir = home + "/dcos-vagrant-build"

logging.basicConfig(format='%(asctime)s - [%(levelname)s] - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Cloning the repo into " + builddir + ".\n")
    try:
        subprocess.check_call("git clone https://github.com/dcos/dcos-vagrant " + builddir, shell=True)
    except OSError:
        if not os.path.isdir(builddir):
            raise
        if os.path.exists(builddir):
            logger.error("The directory already exists, Jim! Check it out and remove it or rename it before running this script again.")
        logger.error("Looks like git isn't installed, yo.")

    print("\n")
    logger.info("Changing working directory to " + builddir + ".")
    os.chdir(builddir)

    logger.info("Downloading the dcos_generate_config.sh script to the root of the repo.\n")
    try:
        subprocess.check_call("curl -O https://downloads.dcos.io/dcos/EarlyAccess/dcos_generate_config.sh", shell=True)
    except OSError:
        logger.error("Looks like curl isn't installed, yo.")

    logger.info("Checking out v0.6.0.")
    subprocess.check_call("git checkout v0.6.0", shell=True)

    print("\n")
    logger.info("We need to create a vboxnet0 if it doesn't already exist.")
    try:
        subprocess.check_call("VBoxManage list hostonlyifs | grep vboxnet0 -q || VBoxManage hostonlyif create", shell=True)
    except OSError:
        logger.error("Doesn't look like I can get to VBoxManage, Jim. Might wanna check your path.")

    logger.info("Set the subnet for vboxnet0 to 192.168.65.1.")
    subprocess.check_call("VBoxManage hostonlyif ipconfig vboxnet0 --ip 192.168.65.1", shell=True)

    logger.info("Attempting to install the vagrant-hostmanager plugin.\n")
    try:
        subprocess.check_call("vagrant plugin install vagrant-hostmanager", shell=True)
    except OSError:
        logger.error("Looks like I can't use the vagrant command. Check your path, Jim.")

    print("\n")
    logger.info("We need to export an environment variable to set the config version.")
    os.environ["DCOS_CONFIG_PATH"] = "etc/config-1.7.yaml"

    logger.info("Attempting to rename the VagrantConfig file.")
    try:
        subprocess.check_call("cp VagrantConfig.yaml.example VagrantConfig.yaml", shell=True)
    except OSError:
        logger.error("Couldn't call cp to move the \"VagrantConfig.yaml.example\" file to \"VagrantConfig.yaml\"")

    logger.info("Alright, Jim. This is where I shove off. I'm going to attempt to build a 3-node fully-functional cluster and hand it off to Vagrant.\n")
    subprocess.check_call("vagrant up m1 a1 p1 boot", shell=True)
