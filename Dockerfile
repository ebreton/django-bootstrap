FROM python:3

# create directories
RUN mkdir -p /usr/src/app && \
	mkdir -p /usr/src/app/staticfiles && \
	mkdir -p /usr/src/app/src && \
	mkdir -p /var/log/django

WORKDIR /usr/src/app

# install requirements 
# (asap to make cache more efficent)
COPY ./requirements*.txt /usr/src/app/
RUN pip install -r requirements-dev.txt

# copy project files
COPY ./src /usr/src/app/src

# collectstatic
RUN DJANGO_SETTINGS_MODULE=settings.prod \ 
	SECRET_KEY="not needed to collectstaticfiles" \
	ALLOWED_HOST="not needed to collectstaticfiles" \
	SITE_URL="not needed to collectstaticfiles" \
	DATABASE_URL="not needed to collectstaticfiles" \
	python src/manage.py collectstatic
