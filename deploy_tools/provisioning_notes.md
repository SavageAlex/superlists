Provisioning a new site
=======================

## Required packages:

* nginx
* Python 3.8
* virtualenv + pip
* Git

eg, on Ubuntu

    sudo add-apt-repository ppa:fkrull/deasnakes
    sudo apt-get install nginx git python38 python3.8-venv

## Nginx Virtual Host config

* see nginx.template.conf
* replace SITENAME with, e.g., staging.my-domain.com

## System service

* see gunicorn-systemd.template.service
* replace SITENAME with, e.g., staging.my-domain.com

## Folder structure:
Assume we have a user account at /home/username

/home/username
    sites
        SITENAME
            database
            source
            static
            virtualenv