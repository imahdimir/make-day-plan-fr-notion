"""

    """

import asyncio
from pathlib import Path

import pandas as pd
import time
import datetime as dt
import pytz

from models import Todoist
from models import TodoistSection
from models import TodoistTask , ColName
from util import del_sections
from util import get_all_sections , get_all_tasks , Params

to = Todoist()
tt = TodoistTask()
ts = TodoistSection()
pa = Params()
c = ColName()

def split_max_time_of_section_from_its_name(df) :
    df[c.secmt] = df[ts.name].str.split('-')
    df[c.secmt] = df[c.secmt].apply(lambda x : x[1] if len(x) > 1 else None)
    df[c.secmt] = df[c.secmt].str.strip()
    return df

def find_next_reset_datetime() :
    dtn = dt.datetime.now(pa.tz)

    # routine reset date time
    if dtn.time() > pa.routine_reset_time :
        rrdate = dtn.date() + dt.timedelta(days = 1)
        rrdt = dt.datetime.combine(rrdate , pa.routine_reset_time)
    else :
        rrdt = dt.datetime.combine(dtn.date() , pa.routine_reset_time)

    print('next reset datetime: ' , rrdt)

    return rrdt

def main() :
    pass

    ##
    dfs = get_all_sections()

    ##
    dfs = split_max_time_of_section_from_its_name(dfs)

    ##
    dft = get_all_tasks()

    ##
    msk = dfs[ts.project_id].eq(pa.routine_proj_id)

    print('All sections count in the project: ' , len(msk[msk]))

    ##
    msk &= ~ dfs[ts.id].isin(dft[tt.section_id])

    print('Empty sections: ' , len(msk[msk]))

    ##
    msk &= ~ dfs[ts.name].str.contains('📌')

    print('Not pinned (!📌) and empty sections: ' , len(msk[msk]))

    ##
    del_sections(dfs.loc[msk , ts.id])

##


if __name__ == '__main__' :
    main()
    print(f'{Path(__file__).name} Done!')

##

if False :
    pass

    ##
    st1 = '6 AM'
    st2 = '6:00 AM'
    dt.datetime.strptime(st2 , '%I %p').time()

    ##
