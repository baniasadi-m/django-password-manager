FROM python:3.11-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN  pip install pip setuptools -U && pip install wheel  && \
     apt update && apt install -y --no-install-recommends nano \
                                  iputils-ping pkg-config supervisor nginx default-mysql-client


COPY requirements.txt /app/

RUN pip install -r requirements.txt

COPY ./core /app/

COPY docker/django-entrypoint.sh /usr/local/bin/django-entrypoint.sh
RUN chmod +x /usr/local/bin/django-entrypoint.sh

COPY docker/nginx.conf /etc/nginx/nginx.conf

COPY docker/supervisord.conf /etc/supervisord.conf


EXPOSE 8080

ENTRYPOINT ["django-entrypoint.sh"]

CMD ["/usr/bin/supervisord"]