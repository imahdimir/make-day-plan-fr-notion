"""

    """

import asyncio
from pathlib import Path

import pandas as pd
from mirutil.classs import return_not_special_variables_of_class as rnsvoc
from todoist_api_python.api_async import TodoistAPIAsync

from day_plan import del_sections
from day_plan import get_all_sections
from day_plan import Todoist
from day_plan import ts
from day_plan import get_daily_routine_project_id


to = Todoist()

class TodoistTask :
    assignee_id = 'assignee_id'
    assigner_id = 'assigner_id'
    comment_count = 'comment_count'
    is_completed = 'is_completed'
    content = 'content'
    created_at = 'created_at'
    creator_id = 'creator_id'
    description = 'description'
    due = 'due'
    id = 'id'
    labels = 'labels'
    order = 'order'
    parent_id = 'parent_id'
    priority = 'priority'
    project_id = 'project_id'
    section_id = 'section_id'
    url = 'url'

tt = TodoistTask()
ttd = rnsvoc(TodoistTask)

async def get_all_tasks_async() :
    api = TodoistAPIAsync(to.tok)
    tsks = await api.get_tasks()
    return tsks

def get_all_tasks() :
    tsks = asyncio.run(get_all_tasks_async())
    df = pd.DataFrame()
    for col in ttd :
        df[col] = [getattr(x , col) for x in tsks]
    return df

def main() :
    pass

    ##
    ds = get_all_sections()

    ##
    dt = get_all_tasks()

    ##
    to.proj_id = get_daily_routine_project_id()

    ##
    msk = ds[ts.project_id].eq(to.proj_id)

    print(len(msk[msk]))

    ##
    msk &= ~ ds[ts.id].isin(dt[tt.section_id])

    print(len(msk[msk]))

    ##
    msk &= ~ ds[ts.name].str.contains('📌')

    print(len(msk[msk]))

    ##
    del_sections(ds.loc[msk , ts.id])

##


if __name__ == '__main__' :
    main()
    print(f'{Path(__file__).name} Done!')

##
if False :
    pass

    ##

    ##
