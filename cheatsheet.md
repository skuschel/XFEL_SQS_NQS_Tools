# Online Analysis Cheatsheet

Notes on Setup in the very bottom of the file.

Open the cheatsheet in a nice looking way (not for editing, need to ssh to server with ssh -Y <user>@<server>):
```
pandoc cheatsheet.md >tmp.html; firefox tmp.html; rm tmp.html
```

## Terminology

Rapid Analysis: Analysis / mostly monitoring using the live data stream (~few seconds after event)
Online Analysis: Analysis at beamline using preprocessed h5 files (~few minutes after event)
Offline Analysis: Analysis of data after the beamtime or at least after some hours of generation using the h5 files

## Rapid Analysis

### Checkout & Status Rapid / Datastream 

checkout what is reaching us in the data stream (bash)
`karabo-bridge-glimpse tcp://10.253.0.142:6666`

## Online Analysis

...

## Initial Setup

Here some ideas on initial setup that will make your live easier:

### .zshrc

Automatize some things when opening a new shell. Therefore you can add to the end of file ~/.zshrc:

#### Aliases for most used directories 

last line: personal directory where git was cloned to (may need to be changed)

```
alias goexp="cd /gpfs/exfel/exp/SQS/201802/p002195/"
alias goraw="cd /gpfs/exfel/exp/SQS/201802/p002195/raw/"
alias gousr="cd /gpfs/exfel/exp/SQS/201802/p002195/usr/"
alias goscratch="cd /gpfs/exfel/exp/SQS/201802/p002195/scratch/"
alias gocode="cd ~/code/XFEL2019_OnlineAnalysis"
```
you then change directory to eg experiment directory just by calling `goexp`

#### Automatically load anaconda3 module
```
module load anaconda3/5.2
```

#### Apply Changes

To make changes effective you need to run `source ~/.zshrc`.
Please note that these steps have to be done twice - once on maxwell and once on ONC since personal directories are not in sync

### getting started with git

Log into maxwell or ONC and/or go to home directory (`~`)

Choose local directory for your code eg:
```
mkdir code
cd code
```

Clone git repo(sitory) into directory:
```
git clone /gpfs/exfel/exp/SQS/201802/p002195/usr/Software/XFEL2019_OnlineAnalysis.git
```

To get the most recent version (eg after somebody updated the code (see below)) execute from the directory of the git:
```
git pull
```

After you worked on the files and may implemented a new feature you can stage files for a commit by:
```
git add <filename>
```

You can do this for multiple files. After you added all files relating to this new feature you may make a commit
```
git commit -a -m "Implemented <you new feature here>"
```

You can then push the commit into the Experiment repository so that everybody can profit from your new feature
```
git push
```
To see what files have changed and what files are staged for commit you can use the command
```
git status
```
