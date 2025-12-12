ARG PYTHON_VERSION=3.10-slim

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /code

WORKDIR /code

COPY requirements.txt /tmp/requirements.txt
RUN set -ex && \
    pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /root/.cache/
COPY . /code

ENV SECRET_KEY "V57nvrzYFuMXWvUvYgEtczl0trJYBXdiXPTgst9JhiL75ylJEN"
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["daphne","-b","0.0.0.0","-p","8000","mysite.asgi"]
