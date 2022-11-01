"""

    """

import asyncio
from functools import partial
from pathlib import Path

import pandas as pd
import requests
from mirutil.classs import return_not_special_variables_of_class as rnsvoc
from mirutil.df import df_apply_parallel as dfap
from mirutil.tok import get_token as get_tok
from todoist_api_python.api import TodoistAPI
from todoist_api_python.api_async import TodoistAPIAsync


class ColName :
    url = 'url'
    js = 'json'
    th = 'T-[h]'
    tm = 'T-[m]'
    indnt = 'INDENT'
    srt = 'sort'
    sec = 'section'
    pri = 'PRIORITY'
    tty = 'T Type'
    cnt = 'CONTENT'
    ty = "TYPE"
    secn = 'secn'
    sec_id = 'sec_id'
    par_id = 'par_id'
    labels = 'labels'

c = ColName()

class Types :
    tsk = 'task'
    sec = 'section'

ty = Types()

class Notion :
    tok = get_tok('Notion')
    db_id = '60c2cf7059f8459fb7b56ce1dadd7677'
    db_url = f'https://api.notion.com/v1/databases/{db_id}/query'
    pg_url = 'https://api.notion.com/v1/pages/'
    hdrs = {
            'Authorization'  : f'Bearer {tok}' ,
            'Notion-Version' : '2022-06-28' ,
            }

no = Notion()

class Todoist :
    tok = get_tok('Todoist')
    hdrs = {
            'Authorization' : f'Bearer {tok}'
            }
    proj_id = '2281475079'
    al_sec_url = f'https://api.todoist.com/rest/v2/sections?project_id={proj_id}'

to = Todoist()

class TodoistSection :
    id = 'id'
    name = 'name'
    order = 'order'
    project_id = 'project_id'

ts = TodoistSection()
tsd = rnsvoc(TodoistSection)

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

async def get_sections_async() :
    api = TodoistAPIAsync(to.tok)
    try :
        scs = await api.get_sections()
        return scs
    except Exception as error :
        print(error)

def get_all_sections() :
    secs = asyncio.run(get_sections_async())
    df = pd.DataFrame()
    for col in tsd :
        df[col] = [getattr(x , col) for x in secs]
    return df

def del_sections(id_list) :
    api = TodoistAPI(to.tok)
    for id in id_list :
        api.delete_section(id)

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

def main() :

    pass

    ##
    proxies = {
            'http'  : '192.168.75.57:8080' ,
            'https' : '192.168.75.57:8080' ,
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
    outmap = {
            c.js : None
            }

    def get_pgs(url , proxies = None) :
        r = requests.get(url , headers = no.hdrs , proxies = proxies)
        return str(r.json())

    ##
    if False :
        pass

        ##
        fu = partial(get_pgs , proxies = proxies)

        df = dfap(df , fu , [c.url] , outmap)

    ##
    df = dfap(df , get_pgs , [c.url] , outmap)

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

    del_all_sections()

    ##
    df1 = make_sections(df1)

    ##
    df1[c.par_id] = None

    ##
    for indnt in df1[c.indnt].unique().tolist() :
        df1 = make_tasks_with_the_indent(df1 , indnt)

##


if __name__ == "__main__" :
    main()
    print(f'{Path(__file__).name} Done!')
