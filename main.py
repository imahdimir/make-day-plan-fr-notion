"""

    """

import asyncio
from functools import partial
from pathlib import Path

import pandas as pd
import requests
from mirutil import async_requests as areq
from mirutil import utils as mu


class Const :
    tok = 'secret_g148lkjdZGkHaQ9Q8MlxAumGNTcg5r1je67Jn3NxtrR'
    dbid = '60c2cf7059f8459fb7b56ce1dadd7677'
    dburl = f'https://api.notion.com/v1/databases/{dbid}/query'
    pgurl = 'https://api.notion.com/v1/pages/'
    hdrs = {
            'Authorization'  : f'Bearer {tok}' ,
            'Notion-Version' : '2022-06-28'
            }

ct = Const()

class ColName :
    th = 'T-[h]'
    tm = 'T-[m]'
    indnt = 'INDENT'
    srt = 'sort'
    sec = 'section'
    pri = 'PRIORITY'
    tt = 'T Type'
    cnt = 'CONTENT'
    ty = "TYPE"
    secn = 'secn'

c = ColName()

class Types :
    tsk = 'task'
    sec = 'section'

ty = Types()

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

def main() :
    pass

    ##
    r = requests.post(ct.dburl , headers = ct.hdrs)
    ##
    x = r.json()['results']
    df = pd.DataFrame(x)
    ##
    df = df[['id']]
    df['id'] = df['id'].str.replace('-' , '')
    df['url'] = ct.pgurl + df['id']
    ##
    url = df['url'][0]
    r = requests.get(url , headers = ct.hdrs)
    r.json()
    ##
    cis = mu.ret_clusters_indices(df)
    fu = partial(areq.get_reps_jsons_async ,
                 headers = ct.hdrs ,
                 trust_env = True ,
                 verify_ssl = False)
    ##
    for se in cis :
        si = se[0]
        ei = se[1]
        print(se)

        inds = df.index[si :ei]

        urls = df.loc[inds , 'url']

        out = asyncio.run(fu(urls))

        df.loc[inds , 'json'] = out

        # break

    ##
    df1 = df.copy()
    df1 = df1['json'].apply(pd.Series)
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
            c.tt    : get_select_col_val ,
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

    ##

    ##

##
if __name__ == "__main__" :
    main()
    print(f'{Path(__file__).name} Done!')
