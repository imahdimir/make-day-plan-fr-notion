import asyncio
import inspect

import pandas as pd
from todoist_api.api import TodoistAPI
from todoist_api.api_async import TodoistAPIAsync

from src.todoist_auto.models import TODOIST as TO
from src.todoist_auto.models import TODOISTSECTION
from src.todoist_auto.models import TODOISTTASK
from src.todoist_auto.models import TODOISTPROJECT

def ret_not_special_items_of_a_class(class_instance) :
    m = inspect.getmembers(class_instance)
    return {x : y for x , y in m if not x.startswith('__')}

TSD = ret_not_special_items_of_a_class(TODOISTSECTION)
TTD = ret_not_special_items_of_a_class(TODOISTTASK)
TPD = ret_not_special_items_of_a_class(TODOISTPROJECT)

def get_all_sections() :
    secs = asyncio.run(get_sections_async())
    df = pd.DataFrame()
    for col in TSD :
        df[col] = [getattr(x , col) for x in secs]
    return df

def del_sections(id_list) :
    api = TodoistAPI(TO.tok)
    for idi in id_list :
        api.delete_section(idi)

async def get_sections_async() :
    api = TodoistAPIAsync(TO.tok)
    try :
        scs = await api.get_sections()
        return scs
    except Exception as error :
        print(error)

async def get_all_tasks_async() :
    api = TodoistAPIAsync(TO.tok)
    tsks = await api.get_tasks()
    return tsks

def get_all_tasks() :
    tsks = asyncio.run(get_all_tasks_async())
    df = pd.DataFrame()
    for col in TTD :
        df[col] = [getattr(x , col) for x in tsks]
    return df

async def get_all_projects_async() :
    api = TodoistAPIAsync(TO.tok)
    prjs = await api.get_projects()
    return prjs

def get_all_projects() :
    prjs = asyncio.run(get_all_projects_async())
    df = pd.DataFrame()
    for col in TPD :
        df[col] = [getattr(x , col) for x in prjs]

    return df

##
df = get_all_projects()

##
df = get_all_sections()

##
##
