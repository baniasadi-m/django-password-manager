#!/bin/bash
export TZ
cd /app

python manage.py makemigrations && python manage.py migrate

# python manage.py registerlicense -d $DJANGO_LICENSE_DAYS -p $DJANGO_LICENSE_USERS -a $DJANGO_LICENSE_API -N "$DJANGO_LICENSE_FULL_NAME" -n "$DJANGO_LICENSE_SHORT_NAME"

if [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] ; then
    (python manage.py createsuperuser --email=$DJANGO_SUPERUSER_EMAIL --noinput)
fi


# Run the original CMD
exec "$@"