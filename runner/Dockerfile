FROM python:3.10-slim

COPY . /code

WORKDIR /code

RUN apt-get update && apt-get install -y \
    git

RUN pip install -U -r /code/runner/requirements.txt

ENTRYPOINT ["python3", "/code/run-checks.py"]
