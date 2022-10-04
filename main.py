"""

    """

import asyncio
from pathlib import Path

import pandas as pd
import requests
from todoist_api_python.api import TodoistAPI
from todoist_api_python.api_async import TodoistAPIAsync

from make_csv import add_time_to_cnt
from make_csv import ColName
from make_csv import fillna_priority
from make_csv import get_num_col_val
from make_csv import get_select_col_val
from make_csv import get_txt_content_fr_notion_name
from make_csv import indent_fillna
from make_csv import Notion
from make_csv import Types


no = Notion()
ty = Types()

class Todoist :
    tok = 'f612bda91f36f389c4c4d4132f53761e6c7a8514'
    hdrs = {
            'Authorization' : f'Bearer {tok}'
            }
    proj_id = '2281475079'
    al_sec_url = f'https://api.todoist.com/rest/v2/sections?project_id={proj_id}'

to = Todoist()

class ColName1(ColName) :
    sec_id = 'sec_id'
    par_id = 'par_id'
    labels = 'labels'

c = ColName1()

def make_labels_list(df) :
    lbl_cols = {
            c.tty : None
            }
    _fu = lambda x : [x] if x is not None else []
    df[c.labels] = df[list(lbl_cols.keys())[0]].apply(_fu)
    for col in list(lbl_cols.keys())[1 :] :
        df[c.labels] = df[c.labels] + df[col].apply(_fu)
    return df

async def get_sections_async() :
    api = TodoistAPIAsync(to.tok)
    try :
        tasks = await api.get_sections()
        print(tasks)
        return tasks
    except Exception as error :
        print(error)

def del_section(id_list) :
    api = TodoistAPI(to.tok)
    for id in id_list :
        api.delete_section(id)

def del_all_sections() :
    secs = asyncio.run(get_sections_async())

    df = pd.DataFrame(secs)
    df['id'] = df[0].apply(lambda x : x.id)
    df['project_id'] = df[0].apply(lambda x : x.project_id)

    msk = df['project_id'].eq(to.proj_id)
    df = df[msk]

    del_section(df['id'].tolist())

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
    r = requests.post(no.dburl , headers = no.hdrs)
    ##
    secs = r.json()['results']
    df = pd.DataFrame(secs)
    ##
    df = df[['id']]
    df['id'] = df['id'].str.replace('-' , '')
    df[c.url] = no.pgurl + df['id']
    ##
    for ind , row in df.iterrows() :
        r = requests.get(row[c.url] , headers = no.hdrs)
        df.at[ind , c.js] = str(r.json())
    ##
    df1 = df.copy()
    df1 = df1[c.js].apply(lambda x : pd.Series(eval(x)))
    df1 = df1[['id' , 'properties']]
    ##
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

    del_all_sections()

    ##
    df1 = make_sections(df1)

    ##
    df1[c.par_id] = None
    ##
    for indnt in df1[c.indnt].unique().tolist() :
        df1 = make_tasks_with_the_indent(df1 , indnt)

    ##

##
if __name__ == "__main__" :
    main()
    print(f'{Path(__file__).name} Done!')
