import gspread
from google.oauth2.service_account import Credentials
from mtok import get_token

class Var :
    indnt = 'INDENT'
    sec = 'section'
    pri = 'PRIORITY'
    cnt = 'CONTENT'
    sec_id = 'sec_id'
    par_id = 'par_id'
    excl = 'Exclude'
    rm_sec = 'remove_section'
    id = 'ID'
    dsc = 'Description'
    l1 = 'L1'
    l2 = 'L2'
    l3 = 'L3'
    l4 = 'L4'
    tsk_id = 'task_id'

VAR = Var()

class TodoistTask :
    assignee_id = 'assignee_id'
    assigner_id = 'assigner_id'
    comment_count = 'comment_count'
    is_completed = 'is_completed'
    content = 'content'
    created_at = 'created_at'
    creator_id = 'creator_id'
    description = 'description'
    due = 'due'
    id = 'id'
    labels = 'labels'
    order = 'order'
    parent_id = 'parent_id'
    priority = 'priority'
    project_id = 'project_id'
    section_id = 'section_id'
    url = 'url'

TODOISTTASK = TodoistTask()

class TodoistSection :
    id = 'id'
    name = 'name'
    order = 'order'
    project_id = 'project_id'

TODOISTSECTION = TodoistSection()

class TodoistProject :
    color = 'color'
    comment_count = 'comment_count'
    id = 'id'
    is_favorite = 'is_favorite'
    is_inbox_project = 'is_inbox_project'
    is_shared = 'is_shared'
    is_team_inbox = 'is_team_inbox'
    name = 'name'
    order = 'order'
    parent_id = 'parent_id'
    url = 'url'
    view_style = 'view_style'

TODOISTPROJECT = TodoistProject()

class Todoist :
    tok = get_token('Todoist')
    hdrs = {
            'Authorization' : f'Bearer {tok}'
            }
    routine_proj_id = '2312505898'
    inbox_id = '2266805950'

TODOIST = Todoist()

class GSheet :
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    tok_key = "Routine_GSheet"
    creds = get_token(tok_key)

    creds = Credentials.from_service_account_info(creds , scopes = scopes)
    client = gspread.authorize(creds)

    sheet_id = "1PdUFy37_4pC8rZDFIxRkaakC5q_Do8xZjOw1Xai-51c"
    workbook = client.open_by_key(sheet_id)
    sheet_1 = workbook.worksheet("Sheet1")

GSHEET = GSheet()
