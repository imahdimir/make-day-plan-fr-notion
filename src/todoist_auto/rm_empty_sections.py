"""

    Removes empty sections from the routine project.

    """

from pathlib import Path

from src.todoist_auto.models import TODOIST as to
from src.todoist_auto.models import TODOISTSECTION as ts
from src.todoist_auto.models import TODOISTTASK as tt
from src.todoist_auto.models import VAR as v
from src.todoist_auto.util import del_sections
from src.todoist_auto.util import get_all_sections
from src.todoist_auto.util import get_all_tasks

def update_rm_sec_based_on_having_no_task(df) :
    dft = get_all_tasks()

    # mark sections with no tasks as true
    msk = ~ df[ts.id].isin(dft[tt.section_id])

    df.loc[: , v.rm_sec] &= msk

    return df

def update_rm_sec_on_not_pinned_sections(df) :
    msk = ~ df[ts.name].str.contains('📌')
    df.loc[: , v.rm_sec] &= msk
    return df

def main() :
    pass

    ##
    dfs = get_all_sections()

    ##
    # keep only routine project sections
    msk = dfs[ts.project_id].eq(to.routine_proj_id)
    dfs = dfs[msk]

    ##
    nc = {
            v.rm_sec : True
            }

    df = dfs.assign(**nc)

    ##
    df = update_rm_sec_based_on_having_no_task(df)

    ##
    df = update_rm_sec_on_not_pinned_sections(df)

    ##
    del_sections(df.loc[df[v.rm_sec] , ts.id])

##
if __name__ == '__main__' :
    main()
    print(Path(__file__).relative_to(Path.cwd()) , ' Done!')
