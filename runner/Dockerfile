FROM python3.10

COPY . /code

WORKDIR /code

RUN pip install -U -r /code/runner/requirements.txt

ENTRYPOINT ["python3", "/code/runner/run.py"]
