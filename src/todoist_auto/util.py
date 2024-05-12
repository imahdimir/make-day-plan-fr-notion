import asyncio

import pandas as pd
from todoist_api.api import TodoistAPI
from todoist_api.api_async import TodoistAPIAsync

from .models import TODOIST as TO
from .models import TODOISTPROJECT as TP
from .models import TODOISTSECTION as TS
from .models import TODOISTTASK as TSK

def ret_not_special_items_of_a_class(cls) :
    return {x : y for x , y in cls.__dict__.items() if not x.startswith('__')}

tpd = ret_not_special_items_of_a_class(TP)
tsd = ret_not_special_items_of_a_class(TS)
ttd = ret_not_special_items_of_a_class(TSK)

def get_all_sections() :
    secs = asyncio.run(get_sections_async())
    df = pd.DataFrame()
    for col in tsd :
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
    for col in ttd :
        df[col] = [getattr(x , col) for x in tsks]
    return df
