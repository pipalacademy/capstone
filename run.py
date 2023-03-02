import argparse
from capstone import tq
from capstone.app import app
from capstone.log import setup_logger

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--tasks", action="store_true", default=False, help="run tasks")
    p.add_argument("--add-dummy-tasks", action="store_true", default=False, help="add dummy tasks")
    return p.parse_args()

def main():
    setup_logger()
    args = parse_args()
    if args.tasks:
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