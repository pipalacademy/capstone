import argparse

from toolkit import setup_logger
import logging
setup_logger()

logger = logging.getLogger(__name__)

from capstone import tq
from capstone.app import app
from capstone.schema import migrate

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
        tq.run_pending_tasks_in_loop()
    elif args.add_dummy_tasks:
        add_dummy_tasks()
    else:
        app.run()

@tq.task_function
def square(x):
    print(f"square of {x} is {x*x}")

def add_dummy_tasks():
    for i in range(10):
        tq.add_task("square", x=i)

if __name__ == "__main__":
    main()