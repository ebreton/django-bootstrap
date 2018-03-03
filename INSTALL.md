<!-- markdownlint-disable MD034 -->
INSTALL.md (with Docker)
===

Table of Content
---

<!-- TOC -->

- [Express set-up](#express-set-up)
    - [0. Pre-requisite](#0-pre-requisite)
    - [1. initialize a fresh .env file](#1-initialize-a-fresh-env-file)
    - [2. Setup containers and DB](#2-setup-containers-and-db)
- [Development environment](#development-environment)
- [A few words on config](#a-few-words-on-config)
    - [Production](#production)
    - [Development](#development)

<!-- /TOC -->

## Express set-up

### 0. Pre-requisite

- git repo checked out (`git clone git@github.com:ebreton/infoscience-exports.git`)
- sudo gem install github_changelog_generator in order to generate automatically the CHANGELOG file
- sudo pip install docopt in order to install post-commit

### 1. initialize a fresh .env file

    $ make init-venv
    ...

You might want to change the default values for the following vars:

- DJANGO_SETTINGS_MODULE=settings.dev
- SITE_URL=https://your-host.com/path
- ALLOWED_HOST=your-host.com
- DEV_PORT=443

You can check what values will be taken into account with

    $ make vars
    App-related vars:
      SECRET_KEY="SeLKDmig0mYF04WVkpZ6mowJ1FiodYkC0C4ZV6Rkuvc="
      DJANGO_SETTINGS_MODULE=settings.dev
      SITE_URL=https://your-host.com/path
      ALLOWED_HOST=your-host
    ...

### 2. Setup containers and DB

    $ make init-docker
    $ make init-db
    ...

or the following alias

    $ make reset
    ...

## Development environment

Warning if you are an EPFL developer, running your developement environment on Ubuntu, with VPN activated :

First, check your VPN connexion is not blocked par your docker

    $ sudo iptables -L
    ....

If ciscovpn services are inside "Chain FORWAR (policy DROP)", you should

    sudo iptables -F ciscovpn

The first thing to do is enable a post-commit git hook in order to have the versions taken care of

    $ pip install docopt
    $ cp update_releases.py .git/hooks/post-commit

    $ which python
    /usr/bin/python

    # if your path is different, change it in the first line of the post-commit file
    $ vi .git/hooks/post-commit
    ...

You can access, with the default configuration :

- the app itself
  - any gaspar credential
  - https://127.0.0.1:8000/
- its admin
  - with the service account *infoscience-exports*
  - or with a gaspar account which has received admin rights
  - https://127.0.0.1:8000/admin

To release a new version (i.e version, branch, tag, github release)

    make release

To deploy a new version of your code (without losing data)

    make deploy

To rebuild everything from scratch

    make reset

This command can actually be split in two parts if you only want to reset docker / db

    make init-docker
    make init-db

To run the tests

    docker-compose -f docker-compose-dev.yml exec web python src/manage.py test exports --noinput [--failfast --keepdb]

Or to test more intensively with nose and coverage

    docker-compose -f docker-compose-dev.yml exec web src/manage.py test exports --noinput [-x]

To check your environment variables

    # on your host
    $ make vars

    # inside the web container
    $ docker-compose -f docker-compose-dev.yml run web env

## A few words on config

Three docker images will be pulled / build on the following command. Those docker images are the same for all environments.

### Production

Files are copied inside the images for production purpose.

- the code of the application: ./src
- the generated static files:  ./staticfiles

Once the images built, just run the containers with

    docker-compose up

If you want to run the containers as a daemon, use the -d option. Logs are still available on demand

    docker-compose up -d
    docker-compose logs

### Development

For development purpose, those files can also be mounted with local tree structure

    docker-compose -f docker-compose-dev.yml up

You will thus be allowed to get change on the fly :

- the code of the application: ./src
- the generated static files:  ./staticfiles
- some assets you might need:  ./nginx/assets
- the nginx configuration:     ./nginx/sites-enabled/web.conf

Aside from the volumes, docker-compose-dev.yml  also makes use of

- .env to load environment variables
- settings/dev.py to set django settings

Would you need to connect directly to the DB, we exposed an access to the host on port 25432

    psql -h 127.0.0.1 -p 25432 -U django -W src
