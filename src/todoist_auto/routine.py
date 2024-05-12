"""

    Renew the routine project in Todoist.

    """

import uuid
from pathlib import Path

import pandas as pd
import requests
from todoist_api.api import TodoistAPI

from .models import NOTION as NO
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

def get_txt_content_fr_notion_name(name) :
    ti = name['title']
    os = ''
    for el in ti :
        os += el['text']['content']
    return os

def get_select_col_val(x) :
    if x['select'] is None :
        return None
    else :
        return x['select']['name']

def get_num_col_val(x) :
    return x['number']

def get_checkbox_col_val(x) :
    return x['checkbox']

def fix_indents(df) :
    df[V.indnt] = df[V.indnt].fillna(1)
    df[V.indnt] = df[V.indnt].astype(int)
    return df

def fillna_priority(df) :
    msk = df[V.pri].isna()
    df.loc[msk , V.pri] = 4
    return df

def make_sections(df) :
    """ Make sections and get their ids """
    for sec in df[V.sec].unique().tolist() :

        if pd.isna(sec) :
            continue

        ose = API.add_section(sec , TO.routine_proj_id)

        msk = df[V.sec].eq(sec)
        df.loc[msk , V.sec_id] = ose.id

    return df

def make_tasks_with_the_indent(df , indent) :
    msk = df[V.indnt].eq(indent)

    df.loc[msk , [V.par_id]] = df[V.par_id].ffill()

    _df = df[msk]

    for ind , row in _df.iterrows() :
        sid = row[V.sec_id] if not pd.isna(row[V.sec_id]) else None

        tska = API.add_task(content = row[V.cnt] ,
                            project_id = TO.routine_proj_id ,
                            section_id = sid ,
                            priority = 5 - int(row[V.pri]) ,
                            parent_id = row[V.par_id])

        df.loc[ind , [V.par_id]] = tska.id

    return df

def get_pgs(url , proxies = None) :
    r = requests.get(url , headers = NO.hdrs , proxies = proxies)
    return str(r.json())

def find_next_not_sub_task_index(subdf , indent) :
    df = subdf
    df.loc[: , ['h']] = df[V.indnt].le(indent)
    return df['h'].idxmax()

def propagate_exculsion_and_drop_final_exculded_tasks(df) :
    # reset index
    df = df.reset_index(drop = True)

    # propagate exculde TO sub-tasks
    for indx , row in df.iloc[:-1].iterrows() :
        if not row[V.excl] :
            continue

        nidx = find_next_not_sub_task_index(df[indx + 1 :] , row[V.indnt])

        msk_range = pd.RangeIndex(start = indx , stop = nidx)

        msk = df.index.isin(msk_range)

        df.loc[msk , V.excl] = True

    # drop exculded tasks
    df = df[~ df[V.excl]]

    return df

def filter_tasks_to_take_out_from_sections() :
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

def move_a_task_under_a_section_out_to_routine_project(task_id) :
    muuid = uuid.uuid4()
    dta = {
            "commands" : r'[ {"type": "item_move", "uuid": ' + f'"{muuid}" ,' + r' "args": { "id": ' + f' "{task_id}", ' + r' "project_id": ' + f' "{TO.routine_proj_id}" ' + r'}}]'
            }
    requests.post('https://api.todoist.com/sync/v9/sync' ,
                  headers = TO.hdrs ,
                  data = dta)

def move_all_tasks_out_of_sections() :
    """ move all not done tasks out of sections TO routine project body """

    df = filter_tasks_to_take_out_from_sections()
    for ind , ro in df.iterrows() :
        move_a_task_under_a_section_out_to_routine_project(ro[TSK.id])

def rm_all_sections_in_the_routine_proj() :
    df = get_all_sections()

    # keep only sections in the day routine project
    msk = df[TS.project_id].eq(TO.routine_proj_id)
    df = df[msk]

    del_sections(df[TS.id])

def get_routine_from_notion_db() :
    r = requests.post(NO.db_url , headers = NO.hdrs)

    secs = r.json()['results']
    df = pd.DataFrame(secs)

    df = df[['id']]
    df['id'] = df['id'].str.replace('-' , '')
    df[V.url] = NO.pg_url + df['id']

    return df

def get_all_pages_in_routine_db_from_notion(df) :
    df[V.jsn] = df[V.url].apply(lambda x : get_pgs(x))
    df = df[V.jsn].apply(lambda x : pd.Series(eval(x)))
    df = df[['id' , 'properties']]
    df = df['properties'].apply(pd.Series)
    return df

def format_page_properties(df) :
    apply_dct = {
            V.id    : lambda x : str(x['unique_id']['number']) ,
            V.sec   : get_select_col_val ,
            V.srt   : get_num_col_val ,
            V.pri   : get_select_col_val ,
            V.cnt   : get_txt_content_fr_notion_name ,
            V.indnt : get_select_col_val ,
            V.excl  : get_checkbox_col_val ,
            }

    for col , func in apply_dct.items() :
        df[col] = df[col].apply(func)

    df = df[apply_dct.keys()]

    return df

def split_section_order_and_section_name(df) :
    new_cols = [V.secn , V.sec]
    df[new_cols] = df[V.sec].str.split('-' , expand = True , n = 1)

    df[V.secn] = df[V.secn].str.strip()
    df[V.sec] = df[V.sec].str.strip()

    return df

def fix_section_order(df) :
    msk = df[V.secn].isna()
    df.loc[msk , V.secn] = 0
    return df

def sort_tasks_based_on_section_and_sort(df) :
    df = df.sort_values([V.secn , V.srt] , ascending = True)
    df = df.drop(columns = [V.secn , V.srt])
    return df

def fix_cols(df) :
    df = fix_indents(df)
    df = fillna_priority(df)
    return df

def main() :
    pass

    ##
    move_all_tasks_out_of_sections()

    ##
    rm_all_sections_in_the_routine_proj()

    ##
    dfa = get_routine_from_notion_db()

    ##
    dfb = get_all_pages_in_routine_db_from_notion(dfa)

    ##
    df = dfb.copy()
    df = format_page_properties(df)

    ##
    df = split_section_order_and_section_name(df)

    ##
    df = fix_section_order(df)

    ##
    df = sort_tasks_based_on_section_and_sort(df)

    ##
    df = fix_cols(df)

    ##
    df = make_sections(df)
    print('All sections created.')

    ##
    df = propagate_exculsion_and_drop_final_exculded_tasks(df)

    ##
    df.loc[: , [V.par_id]] = None

    ##
    for indnt in sorted(df[V.indnt].unique().tolist()) :
        df = make_tasks_with_the_indent(df , indnt)

##
if __name__ == '__main__' :
    main()
    print(Path(__file__).relative_to(Path.cwd()) , ' Done!')
