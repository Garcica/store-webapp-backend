FROM python:3

RUN mkdir -p /opt/src/applications
WORKDIR /opt/src/applications

COPY storekeeper_application.py storekeeper_application.py
COPY configuration_migrate.py configuration_migrate.py
COPY configuration_manage.py configuration_manage.py
COPY models.py models.py
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "storekeeper_application.py"]