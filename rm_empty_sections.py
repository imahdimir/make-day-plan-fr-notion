"""

    """

import asyncio
from pathlib import Path

import pandas as pd
from mirutil.classs import return_not_special_variables_of_class as rnsvoc
from todoist_api_python.api_async import TodoistAPIAsync

from day_plan import del_sections
from day_plan import get_all_sections
from day_plan import to
from day_plan import ts


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
    tsks = asyncio.run(get_all_tasks())
    ##
    tsks[0].__dict__

    ##
    tt = TodoistTask()
    tt.assignee_id

    ##
    t = Task()

    ##
    rnsvoc(Task)

    ##
    df1 = get_all_tasks()

    ##
    from githubdata import GitHubDataRepo


    url = 'https://github.com/Doist/todoist-api-python'

    ##
    ghd = GitHubDataRepo(url)

    ##
    ghd.clone_overwrite()

    ##
    from purl import URL


    u = URL.from_string(url)

    ##
    u
