"""

    """

import asyncio

import pandas as pd
from todoist_api_python.api import TodoistAPI
from todoist_api_python.api_async import TodoistAPIAsync

from models import Todoist
from models import TodoistProject
from models import TodoistSection

to = Todoist()
tp = TodoistProject()

class Params :
    routin = 'Day Routine ☀️'

pa = Params()

def ret_not_special_items_of_a_class(cls) :
    return {x : y for x , y in cls.__dict__.items() if not x.startswith('__')}

tpd = ret_not_special_items_of_a_class(TodoistProject)
tsd = ret_not_special_items_of_a_class(TodoistSection)

def get_daily_routine_project_id() :
    df = get_all_todoist_projects()
    msk = df[tp.name].eq(pa.routin)
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

def get_all_todoist_projects() :
    apia = TodoistAPIAsync(to.tok)
    secs = asyncio.run(apia.get_projects())
    df = pd.DataFrame()
    for col in tpd :
        df[col] = [getattr(x , col) for x in secs]
    return df

async def get_sections_async() :
    api = TodoistAPIAsync(to.tok)
    try :
        scs = await api.get_sections()
        return scs
    except Exception as error :
        print(error)
