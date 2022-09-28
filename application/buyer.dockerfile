FROM python:3

RUN mkdir -p /opt/src/applications
WORKDIR /opt/src/applications

COPY buyer_application.py buyer_application.py
COPY configuration_migrate.py configuration_migrate.py
COPY configuration_manage.py configuration_manage.py
COPY models.py models.py
COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "buyer_application.py"]