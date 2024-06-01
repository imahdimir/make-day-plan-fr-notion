"""

    Removes empty sections from the routine project.

    """

import datetime
import time
import uuid
from pathlib import Path

import requests

from .models import TODOIST as TO
from .models import TODOISTTASK as TSK
from .util import get_all_tasks

PLND_TOD_SEC_ID = '156240085'

def move_a_non_sectioned_task_to_plnd_tod(task_id) :
    muuid = uuid.uuid4()
    dta = {
            "commands" : r'[ {"type": "item_move", "uuid": ' + f'"{muuid}" ,' + r' "args": { "id": ' + f' "{task_id}", ' + r' "section_id": ' + f' "{PLND_TOD_SEC_ID}" ' + r'}}]'
            }
    requests.post('https://api.todoist.com/sync/v9/sync' ,
                  headers = TO.hdrs ,
                  data = dta)

def get_all_inbox_tasks() :
    df = get_all_tasks()
    msk = df[TSK.project_id].eq(TO.inbox_id)
    df = df[msk]
    return df

def move_all_non_sectioned_tasks_to_plnd_tod(all_inbox_tasks_df) :
    df = all_inbox_tasks_df

    msk = df[TSK.section_id].isna()
    df = df[msk]

    for ind , ro in df.iterrows() :
        move_a_non_sectioned_task_to_plnd_tod(ro[TSK.id])

def move_unsectioned_and_sort_plnd_tod_section() :
    """ """

    ##
    df = get_all_inbox_tasks()

    move_all_non_sectioned_tasks_to_plnd_tod(df)

    msk = df['section_id'].eq(PLND_TOD_SEC_ID)
    df = df[msk]

    sort_cols = ['priority' , 'order']
    df = df.sort_values(by = sort_cols , ascending = [False , True])

    df = df.reset_index(drop = True)

    ##
    items = ', '.join([f'{{"id": "{ro[TSK.id]}", "child_order": {idx}}}' for
                       idx , ro in df.iterrows()])

    muuid = uuid.uuid4()

    dta = {
            "commands" : r'[ {"type": "item_reorder", "uuid": ' + f'"{muuid}" ,' + r' "args": { "items": [ ' + f' {items} ' + r']}}]'
            }

    ##
    end_point = 'https://api.todoist.com/sync/v9/sync'
    r = requests.post(end_point , headers = TO.hdrs , data = dta)
    r.text

    ##

def main() :
    pass

    ##
    strt = datetime.datetime.now()

    while True :
        move_unsectioned_and_sort_plnd_tod_section()

        now = datetime.datetime.now()

        l = now - strt
        print(l)

        if l.seconds > 10 * 60 :
            break

        time.sleep(10)

##
if __name__ == '__main__' :
    main()
    print(Path(__file__).name , ' Done!')

##
def _test() :
    pass

    ##
    move_unsectioned_and_sort_plnd_tod_section()

    ##
    from src.todoist_auto.util import get_all_tasks

    df = get_all_tasks()

    ##

    ##
