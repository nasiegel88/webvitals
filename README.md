# Webvitals command line interface

## Introduction

__Users:__ Employees at the Primate Center are the expected users of this software. Webvitals can only be accessed from within the Primate Center intranet and requires credentials to access the website. Users will need to have IT run the installation as it requires admin privileges.

__Purpose:__ This software is to be used to aid users in performing large animal queries from within the Primate Center's database. Available parameters include `location`, `weight`, `snomed`, and `diarrhea observations`.

## Installation

Due to the age of the Webvitals website, the only to way launch it is with an older version of Firefox. Note that Firefox 56 will not replace any update-to-date versions of Firefox and will instead by installed as a separate application. Furthermore, this program has only been tested on Windows, which is another result of the aged Webvitals platform.

#### Install Firefox 56

Make sure you have Firefox 56 installed on your system. If the required version of Firefox is not already installed, its installation file can be found [here](https://ftp.mozilla.org/pub/firefox/releases/56.0.2/win64/en-US/).

#### Install Miniconda for Windows

Miniconda for windows can be installed [here](https://docs.conda.io/en/latest/miniconda.html#windows-installers).

#### Install Git

Git will be required for downloading the software from Github. In order to download repos from GitHub users will need a GitHub account. If you do not have a GitHub account one can be made for free [here](https://github.com/join).

The below command will install Git to your base environment.

```bash
conda install -c conda-forge git
```

Associate Git with your installation of Miniconda prompt.

```bash
git config --global user.name <Your_Git_username>
git config --global user.email <Your_Git_email>
```

### Clone this repo and create the environment

```bash
git clone https://github.com/nasiegel88/webvitals.git

# Create environment
conda env create -n webvitals -f environment.yml

# Activate environment
conda activate webvitals
```

The above will only need to be done once however when the program is used the environment must be activated before running any of the below commands.

## Usage

#### Directory layout.

Users should not need to edit any files with the exception of `webvitals_config.properties` which can be used to store login credentials locally so as to avoid having to enter username and password information with every query.

```bash
webvitals
        .
        ├── README.md
        ├── data
        │   └── <output files>
        ├── .gitignore
        ├── environment.yml
        ├── scripts
        │   ├── __init__.py
        │   ├── diarrhea_observations.py
        │   ├── location.py
        │   ├── snomed.py
        │   └── weight.py
        ├── webvitals.py
        └── webvitals_config.properties
```

#### Saving credentials

Create `webvitals_config.properties`

```bash
touch webvitals_config.properties
```

__Store credentails.__ Note, this file is listed in .gitigore so even if changes are made to the repo by user wanting to fork this repo login information will remain secure. Now edit the file...

    # Open a text editor, like vim
    vim webvitals_config.properties

webvitals_config.properties

    # Webvitals login information
    USERNAME=`<Your Primate Webvitals Username>`
    PASSWORD=`<Your Primate Webvitals Password>`

#### Running the program

    > python webvitals.py --help
    usage: webvitals.py [-h] [-l LIST] [-f FILE]
                        [-q [{location,diarrhea_observations,weight,snomed}]]

    optional arguments:
      -h, --help            show this help message and exit
      -l LIST, --list LIST  delimited list input
      -f FILE, --file FILE  text input
      -q [{location,diarrhea_observations,weight,snomed}], --query [{location,diarrhea_observations,weight,snomed}]

Animal queries can be entered as a list or text file. When entering ids as a list make sure to avoid spaces, and use commas and double quotation marks.

__Example list__

```bash
python webvitals.py --list "<animal 1>,<animal 2>,<animal 3>" --query location
```

__Example text file (test.txt)__

    <animal 1>
    <animal 2>
    <animal 3>

```bash
python webvitals.py --file text.txt --query location
```

## Final remark

This package is to only be used at the Primate Center for research purposes!
