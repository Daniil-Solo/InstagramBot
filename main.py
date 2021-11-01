from yaml import load, SafeLoader
from service_functions import get_account
from tasks import *
import logging

logging.basicConfig(filename='log.log', level=logging.INFO,
                    format='%(asctime)s * %(levelname)s * %(message)s')
wdm_loger = logging.getLogger('WDM')
wdm_loger.disabled = True


if __name__ == "__main__":
    task_configs = load(open("schedule.yml"), Loader=SafeLoader).get("tasks")
    seq = TaskSequence()
    for task_config in task_configs:
        task_name = task_config.get("alias")
        account = get_account(task_name)
        task_type = task_config.get("type")
        seq.create_and_add_task(account, task_name, task_type)
    seq.run()
