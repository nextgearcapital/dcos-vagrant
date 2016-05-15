## Requirements
Make sure you use an up to date version of Vagrant (eg: >=1.8.0). You can find
out your version of Vagrant by doing `vagrant version` in a terminal. If you're
on OSX, please make sure you use a current version of Ruby obtained from
Hombebrew.

## How to use
Just run the `install-dcos.py` script. It will setup a directory in `$HOME/dcos-vagrant-build` and launch the cluster for you.
If you use the `--dev` argument, it will download and install all the dependencies for the UI if you want to develop against that.
All you have to do is run `npm start` in `$HOME/dcos-vagrant-build/ui`.

## Why Python and not Bash?
I know there's a lot of subprocess calls, but I wanted this to be relatively cross-platform.
