import argparse
import logging

from toolkit import setup_logger
from rq import Worker

from capstone.tasks import queue
from capstone.app import app
from capstone.schema import migrate

setup_logger()
logger = logging.getLogger(__name__)

logger.info("Starting Capstone...")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--migrate", action="store_true", default=False, help="migrate database")
    p.add_argument("--tasks", action="store_true", default=False, help="run tasks")
    p.add_argument("--add-dummy-tasks", action="store_true", default=False, help="add dummy tasks")
    return p.parse_args()

def main():
    args = parse_args()
    if args.migrate:
        migrate()
    elif args.tasks:
        worker = Worker([queue], connection=queue.connection)
        worker.work()
    else:
        app.run(host="localhost", debug=True)

if __name__ == "__main__":
    main()
