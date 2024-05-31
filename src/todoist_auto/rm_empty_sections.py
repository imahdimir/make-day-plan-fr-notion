"""

    Removes empty sections from the routine project.

    """

from pathlib import Path

from .models import TODOIST as TO
from .models import TODOISTSECTION as TS
from .models import TODOISTTASK as TT
from .models import VAR as V
from .util import del_sections
from .util import get_all_sections
from .util import get_all_tasks

def update_rm_sec_based_on_having_no_task(df) :
    dft = get_all_tasks()
    # mark sections with NO tasks as true
    msk = ~ df[TS.id].isin(dft[TT.section_id])
    df.loc[: , V.rm_sec] &= msk
    return df

def update_rm_sec_on_not_pinned_sections(df) :
    msk = ~ df[TS.name].str.contains('📌')
    df.loc[: , V.rm_sec] &= msk
    return df

def main() :
    pass

    ##
    dfs = get_all_sections()

    ##
    # keep only routine project sections
    msk = dfs[TS.project_id].eq(TO.routine_proj_id)
    dfs = dfs[msk]

    ##
    nc = {
            V.rm_sec : True
            }

    df = dfs.assign(**nc)

    ##
    df = update_rm_sec_based_on_having_no_task(df)

    ##
    df = update_rm_sec_on_not_pinned_sections(df)

    ##
    del_sections(df.loc[df[V.rm_sec] , TS.id])

##
if __name__ == '__main__' :
    main()
    print(Path(__file__).name , ' Done!')
