"""Read-only query of a pre-existing HappyHorse task owned by your Key."""

import argparse

from happyhorse_crewai import HappyHorseRetrieveTaskTool

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("task_id")
a = p.parse_args()
print(HappyHorseRetrieveTaskTool().run(task_id=a.task_id, wait_seconds=0))
