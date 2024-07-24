from pydantic import BaseModel
import json
from datetime import date
from typing import Optional

class shell_Menus(BaseModel):
    menu_id:int
    menu_name:str
    menu_status:int

class user_Roles(BaseModel):
    role_name:str

class user_Roles_Full_Detail(user_Roles):
    role_id:int
    role_status:int

class shell_Demography(BaseModel):
    demography_name:str

class shell_Demography_Full_Detail(shell_Demography):
    demography_id:int
    demography_status:int

class shell_DataSource(BaseModel):
    datasource_type:str

class shell_DataSource_Full_Detail(shell_DataSource):
    datasource_id:int
    datasource_status:int

class shell_annotateMarker(BaseModel):
    annotate_marker_shape_name:str
    annotate_marker_shape_colour:str
    annotate_marker_label_name:str

class shell_annotateMarker_Full_Detail(shell_annotateMarker):
    annotatemarker_id:int
    annotate_marker_status:int

class shell_menu_permission(BaseModel):
    role_id:int
    menu_id:list[int]

class shell_menu_permission_in_row_wise(BaseModel):
    id:int
    role_id:int
    menu_id:int

class shell_User_table(BaseModel):
    id:int
    emp_id:str
    name:str
    mobile:str
    working_location:str
    designation:str
    user_status:int

class shell_User_table_without_id(BaseModel):
    emp_id:str
    name:str
    mobile:str
    working_location:str
    designation:str

class shell_Project_Creation_table(BaseModel):
    id:int
    project_name:str
    project_demography:int
    project_input_type:int
    project_status:int

class shell_Project_Cycle_Creation(BaseModel):
    project_id:int
    cycle_name:str
    cycle_start_date:date
    cycle_end_date:date

class cycle_update_schema(BaseModel):
    id:int
    cycle_name:str
    cycle_start_date:date
    cycle_end_date:date

