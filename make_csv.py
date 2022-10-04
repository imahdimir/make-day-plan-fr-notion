"""

    """

from pathlib import Path

import pandas as pd
import requests


class Notion :
    tok = 'secret_g148lkjdZGkHaQ9Q8MlxAumGNTcg5r1je67Jn3NxtrR'
    dbid = '60c2cf7059f8459fb7b56ce1dadd7677'
    dburl = f'https://api.notion.com/v1/databases/{dbid}/query'
    pgurl = 'https://api.notion.com/v1/pages/'
    hdrs = {
            'Authorization'  : f'Bearer {tok}' ,
            'Notion-Version' : '2022-06-28'
            }

no = Notion()

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
    df1[c.ty] = ty.tsk
    ##
    df2 = df1.copy()
    for el in df1[c.sec].unique() :
        fu = insert_section_row_before_first_ocur
        df2 = fu(el , df2)

    df2 = df2.drop(columns = [c.sec])
    ##
    df2 = indent_fillna(df2)
    ##
    df2 = add_time_to_cnt(df2)
    ##
    df2 = add_t_type_to_cnt(df2)
    ##
    df2 = fillna_priority(df2)
    ##
    df2.to_csv('out.csv' , index = False)

    ##

##
if __name__ == "__main__" :
    main()
    print(f'{Path(__file__).name} Done!')
