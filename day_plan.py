"""

    """

import asyncio
from functools import partial
from pathlib import Path

import pandas as pd
import requests
from todoist_api_python.api import TodoistAPI
from todoist_api_python.api_async import TodoistAPIAsync

from models import ColName
from models import Notion
from models import Todoist
from models import TodoistProject
from models import TodoistSection
from models import Types
from util import del_sections
from util import get_all_sections
from util import get_daily_routine_project_id
from util import ret_not_special_items_of_a_class as rnsioac


c = ColName()
ty = Types()
ts = TodoistSection()
tsd = rnsioac(TodoistSection)
tp = TodoistProject()
tpd = rnsioac(TodoistProject)
no = Notion()
to = Todoist()

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

def insert_section_row_before_first_ocur(sec , df) :
    df = df.reset_index(drop = True)

    print(sec)
    msk = df[c.sec].eq(sec)
    y = msk[msk].idxmin()

    _df0 = df.loc[: y].iloc[:-1]

    _df = pd.DataFrame({
            c.ty  : [ty.sec] ,
            c.cnt : [sec]
            })

    _df1 = df.loc[y :]

    return pd.concat([_df0 , _df , _df1])

def indent_fillna(df) :
    df[c.indnt] = df[c.indnt].fillna(1)
    return df

def add_time_to_cnt(df) :
    _df = df.copy()

    msk = df[c.th].notna()
    msk |= df[c.tm].notna()

    _df[[c.th , c.tm]] = _df[[c.th , c.tm]].fillna(0)

    h = _df.loc[msk , c.th].astype(int).astype(str)
    m = _df.loc[msk , c.tm].astype(int).astype(str)

    df.loc[msk , c.cnt] = df.loc[msk , c.cnt] + ' - ***' + h + ':' + m + '***'

    df = df.drop(columns = [c.th , c.tm])
    return df

def add_t_type_to_cnt(df) :
    msk = df[c.tty].notna()
    df.loc[msk , c.cnt] = df.loc[msk , c.cnt] + ' @' + df.loc[msk , c.tty]
    df = df.drop(columns = c.tty)
    return df

def fillna_priority(df) :
    msk = df[c.pri].isna()
    df.loc[msk , c.pri] = 4
    return df

def make_labels_list(df) :
    lbl_cols = {
            }

    if not lbl_cols :
        df[c.labels] = df[c.cnt].apply(lambda x : [])
        return df

    _fu = lambda x : [x] if x is not None else []
    df[c.labels] = df[list(lbl_cols.keys())[0]].apply(_fu)
    for col in list(lbl_cols.keys())[1 :] :
        df[c.labels] = df[c.labels] + df[col].apply(_fu)
    return df

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

def del_all_sections() :
    df = get_all_sections()

    msk = df['project_id'].eq(to.proj_id)
    df = df[msk]

    del_sections(df['id'])

def make_sections(df) :
    api = TodoistAPI(to.tok)

    for sec in df[c.sec].unique().tolist() :
        ose = api.add_section(sec , to.proj_id)

        msk = df[c.sec].eq(sec)
        df.loc[msk , c.sec_id] = ose.id

    return df

def make_tasks_with_the_indent(df , indent) :
    msk = df[c.indnt].eq(indent)
    df.loc[msk , c.par_id] = df[c.par_id].ffill()
    _df = df[msk]

    api = TodoistAPI(to.tok)
    for ind , row in _df.iterrows() :
        tsk = api.add_task(content = row[c.cnt] ,
                           section_id = row[c.sec_id] ,
                           priority = 5 - int(row[c.pri]) ,
                           parent_id = row[c.par_id] ,
                           labels = row[c.labels])
        df.at[ind , c.par_id] = tsk.id
    return df

def get_pgs(url , proxies = None) :
    r = requests.get(url , headers = no.hdrs , proxies = proxies)
    return str(r.json())

def main() :
    pass

    ##
    proxies = {
            'http'  : '172.31.0.235:8080' ,
            'https' : '172.31.0.235:8080' ,
            }

    if False :
        pass

        ##
        r = requests.post(no.db_url , headers = no.hdrs , proxies = proxies)

    ##
    r = requests.post(no.db_url , headers = no.hdrs)

    ##
    secs = r.json()['results']
    df = pd.DataFrame(secs)

    ##
    df = df[['id']]
    df['id'] = df['id'].str.replace('-' , '')
    df[c.url] = no.pg_url + df['id']

    ##
    if False :
        pass

        ##
        fu = partial(get_pgs , proxies = proxies)

        df[c.js] = df[c.url].apply(lambda x : fu(x))

    ##
    df[c.js] = df[c.url].apply(lambda x : get_pgs(x))

    ##
    df1 = df.copy()
    df1 = df1[c.js].apply(lambda x : pd.Series(eval(x)))
    df1 = df1[['id' , 'properties']]

    df1 = df1['properties'].apply(pd.Series)

    ##
    apply_dct = {
            c.th    : get_num_col_val ,
            c.tm    : get_num_col_val ,
            c.indnt : get_select_col_val ,
            c.srt   : get_num_col_val ,
            c.sec   : get_select_col_val ,
            c.pri   : get_select_col_val ,
            c.tty   : get_select_col_val ,
            c.cnt   : get_txt_content_fr_notion_name ,
            }

    for col , func in apply_dct.items() :
        df1[col] = df1[col].apply(func)

    ##
    df1[[c.secn , c.sec]] = df1[c.sec].str.split('-' , expand = True)

    ##
    df1[c.secn] = df1[c.secn].astype(int)

    ##
    df1 = df1.sort_values([c.secn , c.srt] , ascending = True)

    df1 = df1.drop(columns = [c.secn , c.srt])

    ##
    df1 = indent_fillna(df1)

    ##
    df1 = add_time_to_cnt(df1)

    ##
    df1 = fillna_priority(df1)

    ##
    df1 = make_labels_list(df1)

    ##
    df1 = add_t_type_to_cnt(df1)

    ##
    to.proj_id = get_daily_routine_project_id()

    ##
    print('Todoist Project ID: ' + to.proj_id)
    assert to.proj_id is not None

    ##
    del_all_sections()

    ##
    df1 = make_sections(df1)

    ##
    df1[c.par_id] = None

    for indnt in df1[c.indnt].unique().tolist() :
        df1 = make_tasks_with_the_indent(df1 , indnt)

##


if __name__ == "__main__" :
    main()
    print(f'{Path(__file__).name} Done!')

##

if False :
    pass

    ##

    ##

    ##
