"""

    Removes empty sections from the routine project.

    """

from pathlib import Path

from .models import TODOIST as TO
from .models import TODOISTSECTION as TS
from .util import del_sections
from .util import get_all_sections

def main() :
    pass

    ##
    df = get_all_sections()

    ##
    # keep only routine project sections
    msk = df[TS.project_id].eq(TO.routine_proj_id)
    df = df[msk]

    ##
    del_sections(df[TS.id])

##
if __name__ == '__main__' :
    main()
    print(Path(__file__).name , ' Done!')
