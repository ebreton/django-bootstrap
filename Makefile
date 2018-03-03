#!make
# Default values, can be overridden either on the command line of make
# or in .env

.PHONY: version vars init-venv build build-travis init-db reset \
	up down logs restart restart-web \
	collectstatic migrations \
	deploy dump restore release \
	test coverage

VERSION = $(shell python update_release.py -v)

version:
	@echo $(VERSION)

vars:
	@echo 'Used by App:'
	@echo '  SECRET_KEY=${SECRET_KEY}'
	@echo '  DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE}'
	@echo '  ALLOWED_HOST=${ALLOWED_HOST}'
	@echo '  SITE_URL=${SITE_URL}'
	@echo '  DATABASE_URL=${DATABASE_URL}'
	@echo ''
	@echo 'Used by docker-compose and Nginx'
	@echo '  DEV_PORT=${DEV_PORT}'
	@echo '  ALLOWED_HOST=${ALLOWED_HOST}'
	@echo ''
	@echo 'Used by Makefile'
	@echo '  SUPER_ADMIN_USERNAME=${SUPER_ADMIN_USERNAME}'
	@echo '  SUPER_ADMIN_EMAIL=${SUPER_ADMIN_EMAIL}'
	@echo '  GITHUB_OWNER=${GITHUB_OWNER}'
	@echo '  GITHUB_REPO=${GITHUB_REPO}'
	@echo '  GITHUB_USER=${GITHUB_USER}'
	@echo '  GITHUB_KEY=${GITHUB_KEY}'
	@echo '  DATABASE_USER=${DATABASE_USER}'
	@echo '  DATABASE_PASSWORD=xxx'
	@echo '  DB_NAME=${DB_NAME}'
	@echo ''
	@echo 'Defined as helpers'
	@echo '  DB_URL=${DB_URL}'

init-venv:
ifeq ($(wildcard .env),)
	cp env/django.env .env
	echo SECRET_KEY=`openssl rand -base64 32` >> .env
	echo PYTHONPATH=`pwd`/src >> .env
	@echo "! Set up your .env file before running"
endif
	@echo "! If you want a clean state from a docker standpoint, run"
	@echo "!   $$ make reset"

build:
	# udpating requirements
	pipenv lock --requirements > requirements.txt
	echo "-r requirements.txt" > requirements-dev.txt
	pipenv lock --requirements --dev >> requirements-dev.txt
	# clean up requirements	
	sed -i "s/# -e git/-e git/g" requirements.txt
	sed -i -r "s/--hash=[^ ]+//g" requirements.txt
	sed -i -r "s/--hash=[^ ]+//g" requirements-dev.txt
	# build docker image
	docker-compose -f docker-compose-dev.yml down
	docker-compose -f docker-compose-dev.yml build

build-travis:
	docker-compose -f docker-compose-dev.yml build
	docker-compose -f docker-compose-dev.yml up -d
	sleep 2

init-db:
	# create DB
	docker-compose -f docker-compose-dev.yml exec postgres \
		psql -c 'CREATE DATABASE "${DB_NAME}";' -U postgres
	# create DB user for app
	docker-compose -f docker-compose-dev.yml exec postgres \
		psql ${DB_NAME} -c "CREATE USER ${DATABASE_USER} WITH PASSWORD '${DATABASE_PASSWORD}';" -U postgres
	docker-compose -f docker-compose-dev.yml exec postgres \
		psql ${DB_NAME} -c "ALTER ROLE ${DATABASE_USER} WITH CREATEDB;" -U postgres
	# initialize DBs executing migration scripts
	docker-compose -f docker-compose-dev.yml exec web \
		python src/manage.py migrate
	# create super admin in app
	docker-compose -f docker-compose-dev.yml exec web \
		python src/manage.py createsuperuser --username=${SUPER_ADMIN_USERNAME} --email=${SUPER_ADMIN_EMAIL} --noinput
	@echo "  -> All set up! You can connect with your tequila acount or the admin (${SUPER_ADMIN_EMAIL})"

reset: build up
	@echo ''
	@echo "! sleeping 3secs, time for postgres container to be available"
	@echo ''
	sleep 3
	make init-db

up:
	docker-compose -f docker-compose-dev.yml up -d

down:
	docker-compose -f docker-compose-dev.yml down

logs:
	docker-compose -f docker-compose-dev.yml logs -f

restart:
	# FIXME: OperationalError at / FATAL: role "django" does not exist
	# docker-compose -f docker-compose-dev.yml down
	docker-compose -f docker-compose-dev.yml up -d
	docker-compose -f docker-compose-dev.yml logs

restart-web:
	docker-compose -f docker-compose-dev.yml stop web
	docker-compose -f docker-compose-dev.yml start web

collectstatic:
	docker-compose -f docker-compose-dev.yml exec web \
		python src/manage.py collectstatic --noinput

migrations:
	docker-compose -f docker-compose-dev.yml exec web \
		python src/manage.py makemigrations

dump:
	@echo dumping DB on last commit `git rev-parse --verify HEAD`
	docker-compose -f docker-compose-dev.yml run --rm \
		-v $(shell pwd)/backup/:/backup \
		postgres sh -c 'exec pg_dump -C -hpostgres -Upostgres -Ox -Ft \
		   -f/backup/$(shell date +"%F:%T")-$(shell git rev-parse --verify HEAD).sql.tar -d${DB_NAME}'

restore:
	@echo restoring DB from file `ls -t backup/*.sql.tar | head -1`
	# retrieve commit number and checkout
	git checkout $(shell ls -t backup/*.sql.tar | head -1 | cut -d'-' -f4 | cut -d '.' -f1)

	# restore DB
	docker-compose -f docker-compose-dev.yml run --rm \
		-v $(shell pwd)/backup/:/backup \
		postgres sh -c 'exec pg_restore -c -hpostgres -U${DATABASE_USER} -Ox -Ft -d${DB_NAME} `ls -t /backup/*.sql.tar | head -1`'

	# restart web container
	make restart-web

release:
	# make sure we are in master
	python update_release.py check --branch=master

	# update versions and ask for confirmation
	python update_release.py
	python update_release.py confirm

	# create branch and tag
	git checkout -b release-$(VERSION)
	git add .
	git commit -m "Prepared release $(VERSION)"
	git push --set-upstream origin release-$(VERSION)

	git tag $(VERSION)
	git push --tags

	# updating CHANGELOG
	github_changelog_generator

	# commit master
	git add CHANGELOG.md
	git commit -m "updated CHANGELOG"
	git push

	# create github release
	python update_release.py publish

	# cancel pre-update of versions
	git checkout src/exports/versions.py

	# git merge master
	git checkout master
	git merge release-$(VERSION)
	git push

deploy: dump
	git pull
	# update docker image
	docker-compose -f docker-compose-dev.yml build web
	# update DB
	docker-compose -f docker-compose-dev.yml exec web \
		python src/manage.py migrate
	# restart web container
	make restart-web

test: check-env
	flake8 src/exports --max-line-length=120
	docker-compose -f docker-compose-dev.yml exec web python src/manage.py test exports --noinput --failfast --keepdb

coverage: check-env
	flake8 src/exports --max-line-length=120
	docker-compose -f docker-compose-dev.yml exec web src/manage.py test exports --noinput
	coverage html
	open htmlcov/index.html

check-env:
ifeq ($(wildcard .env),)
	@echo "Please create your .env file first, from .env.sample or by running make venv"
	@exit 1
else
include .env
export
endif
