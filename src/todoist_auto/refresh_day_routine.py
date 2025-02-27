"""

    """

import uuid
from pathlib import Path

import pandas as pd
import requests
import time
from todoist_api.api import TodoistAPI

from .models import GSHEET
from .models import TODOIST as TO
from .models import TODOISTPROJECT as TP
from .models import TODOISTSECTION as TS
from .models import TODOISTTASK as TSK
from .models import VAR as V
from .util import del_sections
from .util import get_all_sections
from .util import get_all_tasks
from .util import ret_not_special_items_of_a_class

tsd = ret_not_special_items_of_a_class(TS)
tpd = ret_not_special_items_of_a_class(TP)

API = TodoistAPI(TO.tok)

def _move_a_task_under_a_section_out_to_routine_project(task_id) :
    muuid = uuid.uuid4()
    dta = {
            "commands" : r'[ {"type": "item_move", "uuid": ' + f'"{muuid}" ,' + r' "args": { "id": ' + f' "{task_id}", ' + r' "project_id": ' + f' "{TO.routine_proj_id}" ' + r'}}]'
            }
    requests.post('https://api.todoist.com/sync/v9/sync' ,
                  headers = TO.hdrs ,
                  data = dta)

def _filter_tasks_to_take_out_from_sections() :
    # get all tasks
    df = get_all_tasks()
    # keep only tasks in the routine project
    msk = df[TSK.project_id].eq(TO.routine_proj_id)
    df = df[msk]
    # keep those with section_id == those in some section
    msk = df[TSK.section_id].notna()
    df = df[msk]
    # keep only level 1 tasks
    msk = df[TSK.parent_id].isna()
    df = df[msk]
    return df

def move_all_tasks_out_of_sections() :
    """ move all not done tasks out of sections TO routine project body """
    df = _filter_tasks_to_take_out_from_sections()
    for ind , ro in df.iterrows() :
        _move_a_task_under_a_section_out_to_routine_project(ro[TSK.id])

def rm_all_sections_in_the_routine_proj() :
    df = get_all_sections()
    # keep only sections in the day routine project
    msk = df[TS.project_id].eq(TO.routine_proj_id)
    df = df[msk]
    del_sections(df[TS.id])

def replace_by_nan_and_rm_empty_rows(df) :
    df = df.replace('' , pd.NA)
    cols = [V.sec , V.l1 , V.l2 , V.l3 , V.l4]
    msk = df[cols].notna().any(axis = 1)
    df = df[msk]
    return df

def specify_indents(df) :
    for i in range(1 , 5) :
        msk = df['L' + str(i)].notna()
        df.loc[msk , V.indnt] = i
        cn = 'L' + str(i)
        df.loc[msk , V.cnt] = df[cn]
        df = df.drop(columns = cn)
    return df

def rm_empty_rows(df) :
    cols = [V.sec , V.cnt]
    msk = df[cols].notna().any(axis = 1)
    df = df[msk]
    return df

def _find_next_not_sub_task_index(subdf , indent) :
    df = subdf
    df.loc[: , ['h']] = df[V.indnt].le(indent)
    return df['h'].idxmax()

def drop_excluded_tasks(df) :
    df[V.excl] = df[V.excl].eq('TRUE')
    df = df[~ df[V.excl]]
    return df

def _fix_indents(df) :
    df[V.indnt] = df[V.indnt].fillna(1)
    df[V.indnt] = df[V.indnt].astype(int)
    return df

def _fillna_priority(df) :
    msk = df[V.pri].isna()
    df.loc[msk , V.pri] = 4
    return df

def fix_cols(df) :
    df.loc[: , [V.par_id , V.tsk_id]] = None
    df = _fix_indents(df)
    df = _fillna_priority(df)
    df[V.dsc] = df[V.dsc].fillna('')
    return df

def make_all_sections(df) :
    """ Make all sections and get their IDs, assuming section order prefixes are unique. """
    df1 = df.copy()
    df1 = df1.dropna(subset = [V.sec])
    df1 = df1[[V.sec]]
    for idx , ro in df1.iterrows() :
        s = ro[V.sec]
        ose = API.add_section(s , TO.routine_proj_id)
        df.at[idx , V.sec_id] = ose.id
    print('All sections created.')
    df[V.sec_id] = df[V.sec_id].ffill()
    return df

def make_tasks_with_the_indent(df , indent) :
    """ """
    msk = df[V.indnt].eq(indent)
    df.loc[msk , [V.par_id]] = df[V.tsk_id].ffill()
    df1 = df[msk]
    for idx , row in df1.iterrows() :
        s_id = row[V.sec_id] if not pd.isna(row[V.sec_id]) else None
        tsk = API.add_task(content = row[V.cnt] ,
                           description = row[V.dsc] ,
                           project_id = TO.routine_proj_id ,
                           section_id = s_id ,
                           priority = 5 - int(row[V.pri]) ,
                           parent_id = row[V.par_id])
        df.loc[idx , [V.tsk_id]] = tsk.id
        time.sleep(.1)
    return df

def main() :
    pass

    ##
    move_all_tasks_out_of_sections()

    ##
    rm_all_sections_in_the_routine_proj()

    ##
    # get all tasks & Sections
    df = pd.DataFrame(GSHEET.sheet_1.get_all_records())

    ##
    df = replace_by_nan_and_rm_empty_rows(df)

    ##
    df = specify_indents(df)

    ##
    df = drop_excluded_tasks(df)

    ##
    df = fix_cols(df)

    ##
    df = rm_empty_rows(df)

    ##
    df = make_all_sections(df)

    ##
    df = df.dropna(subset = V.cnt)

    ##
    for indnt in sorted(df[V.indnt].unique().tolist()) :
        df = make_tasks_with_the_indent(df , indnt)

##
if __name__ == '__main__' :
    pass

    ##
    main()
    print(Path(__file__).name , 'Done!')

    ##

def _tset() :
    pass

    ##
    df = get_all_sections()

    # keep only sections in the day routine project
    msk = df[TS.project_id].eq(TO.routine_proj_id)
    df = df[msk]

    ##
    API.update_section(155975100 ,
                       name = '-3 _ Right after Wake Up' ,
                       order = 1)

    ##
    muuid = uuid.uuid4()
    dta = {
            "commands" : r'[ {"type": "section_reorder", "uuid": ' + f'"{muuid}" ,' + r' "args": { "sections": [{"id": 155975100, "section_order": 6}]}}]'
            }
    requests.post('https://api.todoist.com/sync/v9/sync' , headers = TO.hdrs ,

                  data = dta)

    ##
