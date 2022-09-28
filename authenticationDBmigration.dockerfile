FROM python:3

RUN mkdir -p /opt/src/authentication
WORKDIR /opt/src/authentication

COPY authentication/requirements.txt ./requirements.txt
COPY authentication/configuration_manage.py ./configuration_manage.py
COPY authentication/configuration_migrate.py ./configuration_migrate.py
COPY authentication/models.py ./models.py
COPY authentication/migrate.py ./migrate.py

RUN pip install -r ./requirements.txt

ENV PYTHONPATH="/opt/src/authentication"

ENTRYPOINT ["python", "./migrate.py"]