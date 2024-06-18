"""


    """

import datetime
import time
from pathlib import Path

import pandas as pd

from .models import FILE as F
from .models import TODOIST as TO
from .models import TODOISTPROJECT as TP
from .models import TODOISTTASK as TSK
from .models import VAR as V
from .util import get_all_projects
from .util import get_all_sections
from .util import get_all_tasks

MAP = pd.DataFrame()

def make_or_read_tod_map() :
    fn = F.tod_map

    if Path(fn).exists() :
        with open(fn , 'r') as f :
            return f.read()

    return pd.DataFrame(columns = [V.not_in_plnd_tod_sec , V.plnd_tod_sec])

def get_all_tod_labled_tasks(df) :
    """ df: all tasks df """
    msk = df[TSK.labels].apply(lambda x : V.tod_lbl in x)
    return df[msk]

def filter_lbld_task_not_in_plnd_tod_section(df) :
    """ gives all tod labeled tasks that are not in plnd tod sec

    df: all tod labeled tasks df

    """
    msk = df[TSK.section_id].eq(TO.plnd_tod_sec_id)
    return df[~ msk]

def filter_all_new_tod_tasks(df , df_map) :
    """ gives newly tod leabeld from all other palces

    df: all tod labeled tasks df
    df_map: tod map df

    """
    ##

    ids = df_map[[V.not_in_plnd_tod_sec , V.plnd_tod_sec]].tolist()

    ##

    msk = df[TSK.id].isin([TOD_COL.other_sec])
    return all_not_plnd_tod_df[~ msk]

def get_name_only_before_emoji(df , col) :
    df[col] = df[col].str.extract(r'([\w\s_]+)')
    df[col] = df[col].str.strip()
    df[col] = df[col].str.replace(r'\s\s' , ' ' , regex = True)
    df[col] = df[col].str.replace(r'\s_\s' , '_' , regex = True)
    return df

def main() :
    pass

    ##
    global MAP

    MAP = make_or_read_tod_map()

    ##
    df_all = get_all_tasks()

    ##
    df_tod = get_all_tod_labled_tasks(df_all)

    ##
    df_not_tod = filter_out_all_tod_labeled_from_plnd_tod_sec(df_tod)

    ##
    df_new_not_tod = filter_out_all_already_in_plnd_tod_sec(df_not_tod , df_map)

    ##
    df_newly_lbld = df_new_not_tod.copy()

    ##
    df_prjs = get_all_projects()

    df_prjs = df_prjs[[TP.id , TP.name]]

    df_prjs = df_prjs.set_index(TP.id)

    ##
    nc = df_newly_lbld[TSK.project_id].map(df_prjs[TP.name])
    df_newly_lbld[V.proj_name] = nc

    ##
    df_newly_lbld = get_name_only_before_emoji(df_newly_lbld , V.proj_name)

    ##
    df_secs = get_all_sections()

    ##
    df_secs = df_secs[[TS.id , TS.name]]

    ##

    ##
    df_newly_lbld[TSK.project_id] = TO.inbox_id
    df_newly_lbld[TSK.section_id] = TO.plnd_tod_sec_id

    ##

    ##

    ##
    df = get_all_tasks()
    move_unsectioned_and_sort_plnd_tod_section(df)

    ##
    strt = datetime.datetime.now()

    while True :
        df = get_all_tasks()

        move_unsectioned_and_sort_plnd_tod_section(df)

        now = datetime.datetime.now()

        l = now - strt
        print(l)

        if l.seconds > 10 * 60 :
            break

        time.sleep(10)

##
if __name__ == '__main__' :
    main()
    print(Path(__file__).name , ' Done!')

##
def _test() :
    pass

    ##
    move_unsectioned_and_sort_plnd_tod_section()

    ##
    from src.todoist_auto.util import get_all_tasks

    df = get_all_tasks()

    ##

    global MAP

    MAP = pd.DataFrame({
            V.not_in_plnd_tod_sec : ['8045747085' , '8045747034'] ,
            V.plnd_tod_sec        : ['7984223687' , '8028305140']
            })

    ##
    MAP.to_parquet(F.tod_map , index = False)

    ##

    ##
