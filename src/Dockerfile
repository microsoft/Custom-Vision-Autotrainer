FROM python:3.6-slim

WORKDIR /autotrainer

COPY autotrainer/requirements.txt .

RUN pip install -r requirements.txt

COPY autotrainer/ .

ENV CV_TRAINING_KEY ""
ENV CV_ENDPOINT ""
ENV STORAGE_ACCOUNT_CONNECTION_STRING ""

ENTRYPOINT ["python", "autotrainer_cli.py" ]