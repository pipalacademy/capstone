FROM python3.10

COPY work /work

RUN pip install -U -r work/requirements.txt work/runner-requirements.txt

ENTRYPOINT ["python3", "runner.py"]
