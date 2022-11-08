"""

    """

import asyncio

import pandas as pd
from todoist_api_python.api import TodoistAPI

from day_plan import get_all_todoist_projects
from day_plan import get_sections_async
from day_plan import to
from day_plan import tp
from day_plan import tsd


def ret_not_special_items_of_a_class(cls) :
    return {x : y for x , y in cls.__dict__.items() if not x.startswith('__')}

def get_daily_routine_project_id() :
    df = get_all_todoist_projects()
    msk = df[tp.name].eq('📆')
    ind = df[msk].index[0]
    return df.at[ind , tp.id]

def get_all_sections() :
    secs = asyncio.run(get_sections_async())
    df = pd.DataFrame()
    for col in tsd :
        df[col] = [getattr(x , col) for x in secs]
    return df

def del_sections(id_list) :
    api = TodoistAPI(to.tok)
    for id in id_list :
        api.delete_section(id)
