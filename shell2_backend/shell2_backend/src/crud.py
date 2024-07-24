import ast
from sqlalchemy.orm import Session,joinedload
from . import models, schemas
from fastapi import UploadFile,HTTPException
import pandas as pd
import json
import os
from zipfile import ZipFile
import tracemalloc
import shutil
from sqlalchemy import or_,and_,func,Date,case
from sqlalchemy.sql import func as functr
from datetime import date,datetime,timedelta
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import A3
from reportlab.lib.colors import red
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from io import BytesIO
from collections import Counter
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
import os
import zipfile
import zipf
import io
from fastapi.responses import FileResponse
from fastapi.responses import StreamingResponse
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from fastapi.encoders import jsonable_encoder
import asyncio
from typing import Dict

#-------------------------------------------------------------------------------------------
resolution = 5
def login(db:Session,emp_id:str):
    total_data = []
    data_sum={}
    project_data=[]
    role_data=[]
    db_res = db.query(models.shell_Project_User_Role_table).filter(models.shell_Project_User_Role_table.user_id==emp_id).all()
    for row in db_res:
        data = {}
        
        db_res2 = db.query(models.shell_Project_Creation_table).filter(models.shell_Project_Creation_table.id==row.project_id).all()
        db_res3 = db.query(models.user_Roles).filter(models.user_Roles.role_id==row.role_id).all()
        data2 = {}
        for row2,row3 in zip(db_res2,db_res3):
            data2['project_id'] = row2.id
            data2['project_name'] = row2.project_name
            data2['role_id'] = row3.role_id
            data2['role_name'] = row3.role_name
            role_data.append(data2)
        data_sum["role_data"] = role_data

    return data_sum

#-------------------------------------------------------------------------------------------

def get_shell_Menus(db: Session):
    return db.query(models.shell_Menus).filter(models.shell_Menus.menu_status == 1).all()

#-------------------------------------------------------------------------------------------

def insert_user_Role(db:Session,user_roles:schemas.user_Roles):
    db_count = db.query(models.user_Roles).filter(models.user_Roles.role_name == user_roles.role_name).count()
    if db_count == 0:
        db_role = models.user_Roles(role_name = user_roles.role_name)
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return "Role Inserted"
    else:
        return "Already Role Exist"

def get_user_Role(db: Session):
    return db.query(models.user_Roles).filter(models.user_Roles.role_status == 1).all()

def delete_user_Role(db:Session,role_id):
    db.query(models.user_Roles).filter(models.user_Roles.role_id == role_id).delete()
    db.commit()
    return db.query(models.user_Roles).filter(models.user_Roles.role_status == 1).all()

def update_user_Role(db:Session,role_id,update_role_name):
    db.item = db.query(models.user_Roles).filter(models.user_Roles.role_id == role_id).first()
    db.item.role_name = update_role_name
    db.commit()
    return db.query(models.user_Roles).filter(models.user_Roles.role_status == 1).all()

#-------------------------------------------------------------------------------------------

def insert_Demography(db:Session,shell_Demography:schemas.shell_Demography):
    db_count = db.query(models.shell_Demography).filter(models.shell_Demography.demography_name == shell_Demography.demography_name).count()
    if db_count==0:
        db_role = models.shell_Demography(demography_name = shell_Demography.demography_name)
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return "Demography Inserted"
    else:
        return "Demography Already Exist"

def get_Demography(db: Session):
    return db.query(models.shell_Demography).filter(models.shell_Demography.demography_status == 1).all()

def delete_Demography(db:Session,demography_id):
    db.query(models.shell_Demography).filter(models.shell_Demography.demography_id == demography_id).delete()
    db.commit()
    return db.query(models.shell_Demography).filter(models.shell_Demography.demography_status == 1).all()

def update_Demography(db:Session,demography_id,demography_name):
    db.item = db.query(models.shell_Demography).filter(models.shell_Demography.demography_id == demography_id).first()
    db.item.demography_name = demography_name
    db.commit()
    return db.query(models.shell_Demography).filter(models.shell_Demography.demography_status == 1).all()

#-------------------------------------------------------------------------------------------

def insert_datasource_type(db:Session,shell_DataSource:schemas.shell_DataSource):
    db_count = db.query(models.shell_DataSource).filter(models.shell_DataSource.datasource_type == shell_DataSource.datasource_type).count()
    if db_count==0:
        db_datasource = models.shell_DataSource(datasource_type = shell_DataSource.datasource_type)
        db.add(db_datasource)
        db.commit()
        db.refresh(db_datasource)
        return "dataSource Added"
    else:
        return "Data Source Already Exists"

def get_dataSource_type(db:Session):
    return db.query(models.shell_DataSource).filter(models.shell_DataSource.datasource_status == 1).all()

def delete_dataSource_type(db:Session,datasource_id):
    db.query(models.shell_DataSource).filter(models.shell_DataSource.datasource_id == datasource_id).delete()
    db.commit()
    return db.query(models.shell_DataSource).filter(models.shell_DataSource.datasource_status == 1).all()

def update_dataSource_type(db:Session,datasource_id,datasoruce_type):
    db.item = db.query(models.shell_DataSource).filter(models.shell_DataSource.datasource_id == datasource_id).first()
    db.item.datasource_type = datasoruce_type
    db.commit()
    return db.query(models.shell_DataSource).filter(models.shell_DataSource.datasource_status == 1).all()

#-------------------------------------------------------------------------------------------

def insert_annotate_marker(db:Session,annotate_marker_schema : schemas.shell_annotateMarker):
    db_count = db.query(models.shell_AnnotateMarker).filter(models.shell_AnnotateMarker.annotate_marker_label_name == annotate_marker_schema.annotate_marker_label_name).count()
    if db_count==0:
        db_annotate_insert = models.shell_AnnotateMarker(annotate_marker_shape_name = annotate_marker_schema.annotate_marker_shape_name,annotate_marker_shape_colour = annotate_marker_schema.annotate_marker_shape_colour, annotate_marker_label_name = annotate_marker_schema.annotate_marker_label_name)
        db.add(db_annotate_insert)
        db.commit()
        db.refresh(db_annotate_insert)
        return "Annotation Marker Inserted"
    else:
        return "label_name already exist"


def get_annotate_marker(db:Session):
    return db.query(models.shell_AnnotateMarker).filter(models.shell_AnnotateMarker.annotate_marker_status == 1).all()

def delete_annotate_marker(db:Session, annotate_marker_id):
    db.query(models.shell_AnnotateMarker).filter(models.shell_AnnotateMarker.annotatemarker_id == annotate_marker_id).delete()
    db.commit()
    return db.query(models.shell_AnnotateMarker).filter(models.shell_AnnotateMarker.annotate_marker_status == 1).all()

def update_annotate_marker(db:Session,annotate_marker_schema:schemas.shell_annotateMarker_Full_Detail):
    db_item = db.query(models.shell_AnnotateMarker).filter(models.shell_AnnotateMarker.annotatemarker_id == annotate_marker_schema.annotatemarker_id).first()
    db_item.annotate_marker_shape_name = annotate_marker_schema.annotate_marker_shape_name
    db_item.annotate_marker_shape_colour = annotate_marker_schema.annotate_marker_shape_colour
    db_item.annotate_marker_label_name = annotate_marker_schema.annotate_marker_label_name
    db.commit()
    return db.query(models.shell_AnnotateMarker).filter(models.shell_AnnotateMarker.annotate_marker_status == 1).all()

#-------------------------------------------------------------------------------------------

def inser_menu_permission(db:Session,menu_permission_schema:schemas.shell_menu_permission):
     
    db_res = db.query(models.shell_menu_permission).filter(models.shell_menu_permission.role_id==menu_permission_schema.role_id).all()

    db_count = db.query(models.shell_menu_permission).filter(models.shell_menu_permission.role_id==menu_permission_schema.role_id).count()

    if db_count > 0:
        for first_row in db_res:
            if not menu_permission_schema.menu_id.__contains__(first_row.menu_id):
                db.query(models.shell_menu_permission).filter(models.shell_menu_permission.menu_id == first_row.menu_id,models.shell_menu_permission.role_id==menu_permission_schema.role_id).delete()
                db.commit()
            else:
                menu_permission_schema.menu_id.remove(first_row.menu_id)

        for _menu_id in menu_permission_schema.menu_id:
                    db_menu_permission_insert = models.shell_menu_permission(role_id=menu_permission_schema.role_id,menu_id=_menu_id)
                    db.add(db_menu_permission_insert)
                    db.commit()
                    db.refresh(db_menu_permission_insert)
    else:
        for _menu_id in menu_permission_schema.menu_id:
                    db_menu_permission_insert = models.shell_menu_permission(role_id=menu_permission_schema.role_id,menu_id=_menu_id)
                    db.add(db_menu_permission_insert)
                    db.commit()
                    db.refresh(db_menu_permission_insert)

    return "Success"

def get_menu_permission(db:Session):
    data_menu_list =[]
    db_res = db.query(models.shell_menu_permission).distinct(models.shell_menu_permission.role_id).all()
    for row in db_res:
        menu_list = [] 
        menu_list_id = [] 
        data = {}
        db_res2 = db.query(models.shell_menu_permission).filter(models.shell_menu_permission.role_id == row.role_id).all()
        data['role_name'] = row._role.role_name
        data['role_id'] = row._role.role_id
        for row2 in db_res2:
             menu_list.append(row2._menus.menu_name)
             menu_list_id.append(row2._menus.menu_id)
        data['menu_name'] = menu_list
        data['menu_id'] = menu_list_id
        data_menu_list.append(data)
    json_data = json.dumps(data_menu_list)
    return json.loads(json_data)

def get_menu_permission_for_role(db:Session,role_name):

    data_menu_list =[]
    
    db_get_role_id = db.query(models.user_Roles).filter(models.user_Roles.role_name == role_name).first()

    db_res = db.query(models.shell_menu_permission).filter(models.shell_menu_permission.role_id == db_get_role_id.role_id).all()
    for row in db_res:
        menu_list = [] 
        menu_list_id = [] 
        data = {}
        db_res2 = db.query(models.shell_menu_permission).filter(models.shell_menu_permission.role_id == row.role_id).all()
        data['role_name'] = row._role.role_name
        data['role_id'] = row._role.role_id
        for row2 in db_res2:
             menu_list.append(row2._menus.menu_name)
             menu_list_id.append(row2._menus.menu_id)
        data['menu_name'] = menu_list
        data['menu_id'] = menu_list_id
        data_menu_list.append(data)
    json_data = json.dumps(data_menu_list)
    return json.loads(json_data)

#-------------------------------------------------------------------------------------------

def insert_user_details(db:Session,user_detail_schema:schemas.shell_User_table_without_id):
     db_user = models.shell_User_table(emp_id=user_detail_schema.emp_id, name=user_detail_schema.name, mobile=user_detail_schema.mobile, working_location=user_detail_schema.working_location, designation=user_detail_schema.designation)
     db.add(db_user)
     db.commit()
     db.refresh(db_user)
     return db.query(models.shell_User_table).filter(models.shell_User_table.user_status==1).all()


def insert_user_details_bulk(db:Session,file:UploadFile):
    
    if file.filename.endswith('.xlsx'):
        df = pd.read_excel(file.file)
    elif file.filename.endswith('.csv'):
        print(file.filename)
        df = pd.read_csv(file.file)
        print(df)
        print(file.file)
    else:
        raise HTTPException(status_code=400, detail="File format not supported. Please upload either Excel (.xlsx) or CSV (.csv) files.")
    
    for index,row in df.iterrows():
        db_user = models.shell_User_table(emp_id=row["emp_id"], name=row["name"], mobile=row["mobile"], working_location=row["working_location"], designation=row["designation"])
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    return db.query(models.shell_User_table).filter(models.shell_User_table.user_status==1).all()

 #-------------------------------------------------------------------------------------------

def insert_project_table(db:Session,pj_name:str,pj_demo:int,pj_input:int,file1:UploadFile,pj_anno):
    db_count = db.query(models.shell_Project_Creation_table).filter(models.shell_Project_Creation_table.project_name == pj_name).count()
    print(db_count)
    if db_count ==0:
        db_query = models.shell_Project_Creation_table(project_name=pj_name,project_demography=pj_demo,project_input_type=pj_input)
        db.add(db_query)
        db.commit()
        db.refresh(db_query)
        
        pj_anno_id = pj_anno.split(',')
        for val in pj_anno_id:
            print('Sum is '+val)
            db_query2 = models.shell_Project_Selected_Annotation(project_id=db_query.id,annotation_id=int(val))
            db.add(db_query2)
            db.commit()
            db.refresh(db_query2)

        if file1.filename.endswith('.xlsx'):
            df1 = pd.read_excel(file1.file)
        elif file1.filename.endswith('.csv'):
            df1 = pd.read_csv(file1.file)
        else:
            raise HTTPException(status_code=400, detail="File format not supported. Please upload either Excel (.xlsx) or CSV (.csv) files.")
                
        for index,row1 in df1.iterrows():  
            db_res = db.query(models.user_Roles).filter(models.user_Roles.role_name == row1["role_id"]).first()
            db_count = db.query(models.shell_Project_User_Role_table).filter(models.shell_Project_User_Role_table.project_id == int(db_query.id),models.shell_Project_User_Role_table.user_id == row1['user_id'],models.shell_Project_User_Role_table.role_id==int(db_res.role_id)).count()
            if db_count ==0:
                db_query3 = models.shell_Project_User_Role_table(user_id=row1['user_id'], project_id=int(db_query.id), role_id=int(db_res.role_id))
                db.add(db_query3)
                db.commit()
                db.refresh(db_query3)
            else:
                return "Duplicate Found in Employee id"
        
        return "Success"
    else:
        return "Project Name Already Exists"

def get_project(db:Session):  
    project_list =[]
    db_res = db.query(models.shell_Project_Creation_table).filter(models.shell_Project_Creation_table.project_status==1).all()
    for row in db_res: 
        data = {}
        selected_annotated_list = []
        selected_annotated_id = []
        data["project_id"] = row.id
        data["project_name"] = row.project_name
        data['project_demography_id'] = row._demography.demography_id
        data["project_demography"] = row._demography.demography_name
        data["project_datasource_id"] = row._datasource.datasource_id
        data["project_input_type"] = row._datasource.datasource_type
        db_res2 = db.query(models.shell_Project_Selected_Annotation).filter(models.shell_Project_Selected_Annotation.project_id == row.id).all()
        for row2 in db_res2:
            selected_annotated_list.append(row2._annotate_marker.annotate_marker_shape_name+","+row2._annotate_marker.annotate_marker_label_name+","+row2._annotate_marker.annotate_marker_shape_colour+","+str(row2._annotate_marker.annotatemarker_id))
            selected_annotated_id.append(row2._annotate_marker.annotatemarker_id)
        data["annotation_list"] = selected_annotated_list
        data["annotation_id"] = selected_annotated_id
        data["project_status"] = row.project_status
        project_list.append(data)
    json_data = json.dumps(project_list)
    return json.loads(json_data)

def get_project_user_list(db:Session,project_id:int):  
    db_res = db.query(models.shell_Project_Creation_table).filter(models.shell_Project_Creation_table.id==project_id).all()
    for row in db_res: 
        project_list =[]
        db_res3 = db.query(models.shell_Project_User_Role_table).filter(models.shell_Project_User_Role_table.project_id == row.id).all()
        for row3 in db_res3:
            user_role_map = {}
            print(str(row3.id)+'-'+row3._user_table.emp_id+"-"+row3._user_table.name+'-'+row3._role_table.role_name)
            user_role_map['user_unique_id'] = row3.id
            user_role_map['project_id'] = project_id
            user_role_map["user_id"] = row3._user_table.emp_id+"-"+row3._user_table.name
            user_role_map["role_name"] = row3._role_table.role_name
            project_list.append(user_role_map)
    json_data = json.dumps(project_list)
    return json.loads(json_data)

def update_project(db:Session,pid:int,pj_name:str,pj_demo:int,pj_ds:int):
    db_res = db.query(models.shell_Project_Creation_table).filter(models.shell_Project_Creation_table.id == pid).first()
    db_res.project_name = pj_name
    db_res.project_demography = pj_demo
    db_res.project_input_type = pj_ds
    db.commit()
    return "Success"

def add_more_users_to_project(db:Session,pj_id:int,file1:UploadFile):

    if file1.filename.endswith('.xlsx'):
        df1 = pd.read_excel(file1.file)
    elif file1.filename.endswith('.csv'):
        df1 = pd.read_csv(file1.file)
    else:
        raise HTTPException(status_code=400, detail="File format not supported. Please upload either Excel (.xlsx) or CSV (.csv) files.")
        
    for index,row1 in df1.iterrows():  
        db_res = db.query(models.user_Roles).filter(models.user_Roles.role_name == row1["role_id"]).first()
        db_count = db.query(models.shell_Project_User_Role_table).filter(models.shell_Project_User_Role_table.project_id == int(pj_id),models.shell_Project_User_Role_table.user_id == row1['user_id'],models.shell_Project_User_Role_table.role_id==int(db_res.role_id)).count()
        if db_count ==0:
            db_query3 = models.shell_Project_User_Role_table(user_id=row1['user_id'], project_id=int(pj_id), role_id=int(db_res.role_id))
            db.add(db_query3)
            db.commit()
            db.refresh(db_query3)
        else:
            return "Duplicate Found in Employee id"
        
    return "Success"

def add_more_annotation_to_project(db:Session,pj_id:int,annotate_str:str):
    db.query(models.shell_Project_Selected_Annotation).filter(models.shell_Project_Selected_Annotation.project_id == pj_id).delete()
    db.commit()
    values_list = [int(value) for value in annotate_str.split(",")]
    db_count = db.query(models.shell_Project_Selected_Annotation).filter(models.shell_Project_Selected_Annotation.project_id == pj_id , models.shell_Project_Selected_Annotation.annotation_id.in_(values_list)).count()
    print(db_count)
    if db_count == 0:
        pj_anno_id = annotate_str.split(',')
        for val in pj_anno_id:
            db_query2 = models.shell_Project_Selected_Annotation(project_id=pj_id,annotation_id=int(val))
            db.add(db_query2)
            db.commit()
            db.refresh(db_query2)
        return "Success"
    else:
        return "Duplicate Annotation Found"

#-------------------------------------------------------------------------------------------

def insert_cycle_creation(db:Session,cycle_creation_schema:schemas.shell_Project_Cycle_Creation):
    db_count = db.query(models.shell_Project_Cycle_Creation).filter(models.shell_Project_Cycle_Creation.project_id == cycle_creation_schema.project_id,models.shell_Project_Cycle_Creation.cycle_name == cycle_creation_schema.cycle_name).count()
    if db_count ==0:
        db_query = models.shell_Project_Cycle_Creation(project_id=cycle_creation_schema.project_id,cycle_name=cycle_creation_schema.cycle_name,cycle_start_date=cycle_creation_schema.cycle_start_date,cycle_end_date=cycle_creation_schema.cycle_end_date)
        db.add(db_query)
        db.commit()
        db.refresh(db_query)
        # print(db_query.id)
        return "Success"
    else:
        return "Cyclename Already Exists"

def get_list_of_cycles(db:Session,pro_id:int):
    cycle_list =[]
    db_res = db.query(models.shell_Project_Cycle_Creation).filter(models.shell_Project_Cycle_Creation.project_id == pro_id,models.shell_Project_Cycle_Creation.cycle_status ==1).all()
    for row in db_res:
        cycle_list_map = {}
        cycle_list_map['project_id_id'] = row.project_id
        cycle_list_map['project_name'] = row._shell_project5.project_name
        cycle_list_map['cycle_id'] = row.id
        cycle_list_map['cycle_name'] = row.cycle_name
        cycle_list_map['cycle_start_date'] = row.cycle_start_date.strftime("%d-%m-%Y")
        cycle_list_map['cycle_end_date'] = row.cycle_end_date.strftime("%d-%m-%Y")
        cycle_list_map['cycle_status'] = row.cycle_status
        cycle_list.append(cycle_list_map)
    json_data = json.dumps(cycle_list)
    return json.loads(json_data)

def update_cycle(db:Session,cycle_schema:schemas.cycle_update_schema):
    db_res = db.query(models.shell_Project_Cycle_Creation).filter(models.shell_Project_Cycle_Creation.id == cycle_schema.id).first()
    db_res.cycle_name = cycle_schema.cycle_name
    db_res.cycle_start_date = cycle_schema.cycle_start_date
    db_res.cycle_end_date = cycle_schema.cycle_end_date
    db.commit()
    return "Success"

def delete_cycle(db:Session,cycle_id:int):
    db_res = db.query(models.shell_Project_Cycle_Creation).filter(models.shell_Project_Cycle_Creation.id == cycle_id).first()
    db_res.cycle_status = 0
    db.commit()
    return "Success"

#-------------------------------------------------------------------------------------------

def tracking_sheet_upload(db:Session,file1:UploadFile,proj_id:int,cycl_id:int,uploaded_by:int):
    try:
        if file1.filename.endswith('.xlsx'):
            df1 = pd.read_excel(file1.file,encoding='latin1')
        elif file1.filename.endswith('.csv'):
            df1 = pd.read_csv(file1.file,encoding='latin1')
        else:
            raise HTTPException(status_code=400, detail="File format not supported. Please upload either Excel (.xlsx) or CSV (.csv) files.")
    except:
        if file1.filename.endswith('.xlsx'):
            df1 = pd.read_excel(file1.file)
        elif file1.filename.endswith('.csv'):
            df1 = pd.read_csv(file1.file)
        else:
            raise HTTPException(status_code=400, detail="File format not supported. Please upload either Excel (.xlsx) or CSV (.csv) files.")
    
    for index,row1 in df1.iterrows():
        db_query3 = models.shell_Tracking_Sheet(project_id=proj_id,cycle_id=cycl_id,store_number=row1['Store Number'], four_digit_store_number=row1['4 - Digit Store Number'], store_name=row1["Store Name"],department_name=row1["Department Name"],planogram_type=row1["Planogram Type"],planogram_name=row1["Planogram Name"],sku=row1["No. of SKUs"],priority=int(row1["Priroity"]),delivery_date=row1["Delivery_date"],created_by=uploaded_by)
        db.add(db_query3)
        db.commit()
        db.refresh(db_query3)
    
    return "Success"

#-------------------------------------------------------------------------------------------
progress_data: Dict[str, float] = {}

async def event_generator(session_id: str):
        while True:
            progress = progress_data.get(session_id, 0)
            print(progress)
            yield f"data: {progress}\n\n"
            await asyncio.sleep(1)

async def store_image_upload(db:Session,file1:UploadFile,proj_id:int,cycl_id:int,uploaded_by:int):
    tracemalloc.start()
    db_res = db.query(models.shell_Tracking_Sheet).filter(models.shell_Tracking_Sheet.project_id==proj_id,models.shell_Tracking_Sheet.cycle_id==cycl_id).count()
    if(int(db_res)>0):

        os.makedirs("upload_image", exist_ok=True)
        extraction_path2 = os.path.join("upload_image",str(cycl_id))
        os.makedirs(extraction_path2,exist_ok=True)
        
        # Save the uploaded zip file
        file_path = os.path.join(extraction_path2, file1.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file1.read())

        # Extract the zip file
        with ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extraction_path2)

        # remove zip and Macosx Directory
        try:
            shutil.rmtree(extraction_path2+'/__MACOSX')
        except:
            print("no macosx")
        try:
            files = os.listdir(extraction_path2)
            for file in files:
                if file.endswith(".zip"):
                    file_path = os.path.join(extraction_path2, file)
                    os.remove(file_path)
        except:
            print("no macosX")

        store_image_file_info = zip_ref.infolist()
        total_files = len(store_image_file_info)
        processed_files = 0

        session_id = f"{1}_{1}"
        progress_data[session_id] = 0
        
        try:
            for store_image_file_name in store_image_file_info:
                if not store_image_file_name.filename.startswith('__MACOSX'):
                    if store_image_file_name.filename.endswith(('.jpg', '.jpeg', '.png', '.bmp', '.tiff')):
                        db_query3 = models.shell_Store_Image(project_id=proj_id,cycle_id=cycl_id,image_path_name=extraction_path2+'\\'+store_image_file_name.filename,created_by=uploaded_by)
                        db.add(db_query3)
                        db.commit()
                        db.refresh(db_query3)
                    processed_files += 1
                    progress = (processed_files / total_files) * 100
                    progress_data[session_id] = progress
                    print("HIHIHIIHIH",progress_data)
                    await asyncio.sleep(0)
        finally:
            progress_data[session_id] = 100
            await asyncio.sleep(1)  # Allow time for the last progress update to be sent
            del progress_data[session_id]
        return JSONResponse(content={"message": "Files uploaded and processed successfully"})
    else:
        return JSONResponse(content={"detail": "No Tracking Sheet Upload"}, status_code=400)
    


#---------------------------------------------------------------------------------------------
    
async def planogram_upload(db:Session,file1:UploadFile,proj_id:int,cycl_id:int,uploaded_by:int):
    tracemalloc.start()
    db_res = db.query(models.shell_Tracking_Sheet).filter(models.shell_Tracking_Sheet.project_id==proj_id,models.shell_Tracking_Sheet.cycle_id==cycl_id).count()
    if(int(db_res)>0):

        os.makedirs("upload_pdf", exist_ok=True)
        extraction_path2 = os.path.join("upload_pdf",str(cycl_id))
        os.makedirs(extraction_path2,exist_ok=True)

        # Save the uploaded zip file
        file_path = os.path.join(extraction_path2, file1.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file1.read())

        # Extract the zip file
        with ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extraction_path2)

        #remove zip and Macosx Directory
        try:
            shutil.rmtree(extraction_path2+'/__MACOSX')
        except:
            print("no macosx")
        try:
            files = os.listdir(extraction_path2)
            for file in files:
                if file.endswith(".zip"):
                    file_path = os.path.join(extraction_path2, file)
                    os.remove(file_path)
        except:
            print("no macosX")

        pdf_file_info = zip_ref.infolist()
        
        for pdf_file_name in pdf_file_info:
            if not pdf_file_name.filename.startswith('__MACOSX'):
                if pdf_file_name.filename.endswith(('.pdf')):
                    db_query3 = models.shell_Planogram(project_id=proj_id,cycle_id=cycl_id,pdf_path_name=extraction_path2+'\\'+pdf_file_name.filename,created_by=uploaded_by)
                    db.add(db_query3)
                    db.commit()
                    db.refresh(db_query3)
        
        
        
        return "Yes"
    
    else:
        return "No Tracking Sheet Upload"
    
#--------------------------------------------------------------------------------------------------

def get_all_project(db:Session):
    project_list =[]
    db_res = db.query(models.shell_Tracking_Sheet).distinct(models.shell_Tracking_Sheet.cycle_id).all()
    for row in db_res:
        project_list_map = {}
        project_list_map['project_id'] = row.project_id

        project_list_map['project_name'] = row._shell_project6.project_name
        project_list_map['cycle_name'] = row._cycle_table2.cycle_name

        db_tracking_sheet_count = db.query(models.shell_Tracking_Sheet).filter(models.shell_Tracking_Sheet.project_id==row.project_id).count()
        
        project_list_map['tracking_sheet_count'] = db_tracking_sheet_count
        project_list_map['t_created_at'] = row.created_at.strftime("%d-%m-%Y")

        db_res_temp = db.query(models.shell_User_table).filter(models.shell_User_table.id==row.created_by).first()
        project_list_map['t_name'] = db_res_temp.emp_id+'-'+db_res_temp.name
       
        db_str_img_count = db.query(models.shell_Store_Image).filter(models.shell_Store_Image.project_id == row.project_id).count()
        db_str_img_details = db.query(models.shell_Store_Image).filter(models.shell_Store_Image.project_id == row.project_id).first()
        
        if db_str_img_count >0:
            project_list_map['str_img_count'] = db_str_img_count
            project_list_map['i_created_at'] = db_str_img_details.created_at.strftime("%d-%m-%Y")
            project_list_map['i_name'] = db_str_img_details._user_table2.emp_id+'-'+db_str_img_details._user_table2.name
        else:
            project_list_map['str_img_count'] = 0
            project_list_map['i_created_at'] = ""
            project_list_map['i_name'] = ""

        db_str_plan_count = db.query(models.shell_Planogram).filter(models.shell_Planogram.project_id == row.project_id).count()
        db_str_plan_details = db.query(models.shell_Planogram).filter(models.shell_Planogram.project_id == row.project_id).first()
        
        if db_str_plan_count >0:
            project_list_map['str_plano_count'] = db_str_plan_count
            project_list_map['p_created_at'] = db_str_plan_details.created_at.strftime("%d-%m-%Y")
            project_list_map['p_name'] = db_str_plan_details._user_table3.emp_id+'-'+db_str_plan_details._user_table3.name
        else:
            project_list_map['str_plano_count'] = 0
            project_list_map['p_created_at'] = ""
            project_list_map['p_name'] = ""

        project_list.append(project_list_map)
    
    json_data = json.dumps(project_list)
    return json.loads(json_data)

#--------------------------------------------------------------------------------------------------

def get_question_answer(db:Session,emp_id:str):
    production_list = []
    db_user_spl = db.query(models.shell_User_table).filter(models.shell_User_table.emp_id==emp_id).first()
    # print(db_user_spl.specialization)
    spl = db_user_spl.specialization.split(",")
    # print(spl)
    # print("\n")

    when_clauses = [(models.shell_Tracking_Sheet.planogram_type == planogram_type, index) for index, planogram_type in enumerate(spl)]
    for row in when_clauses:
        print(row)
    ordering = case(*[clause for clause in when_clauses], else_=len(spl))

    # print(ordering)

    db_count = db.query(models.shell_User_table).filter(models.shell_User_table.emp_id==emp_id).count()
    if db_count > 0 :
        db_res = db.query(models.shell_User_table).filter(models.shell_User_table.emp_id==emp_id).first()
        db_employee_id = db_res.id
        db_res2 = db.query(models.shell_Project_Cycle_Creation).filter(models.shell_Project_Cycle_Creation.cycle_status==1).first()
        db_cycle_id = db_res2.id
        db_project_id = db_res2.project_id
        print("project_id",db_project_id,"cycle_id: ",db_cycle_id)
        count = db.query(models.shell_Tracking_Sheet).filter(
            models.shell_Tracking_Sheet.project_id == int(db_project_id),
            models.shell_Tracking_Sheet.cycle_id==int(db_cycle_id),
            or_(models.shell_Tracking_Sheet.picked_status == "Picked",
                models.shell_Tracking_Sheet.picked_status == "Open")
            ).count()
        if count > 0:
            db_res3 = db.query(models.shell_Tracking_Sheet).filter(
            models.shell_Tracking_Sheet.project_id == int(db_project_id),
            models.shell_Tracking_Sheet.cycle_id==int(db_cycle_id),
            or_(
                and_(models.shell_Tracking_Sheet.picked_status == "Picked",models.shell_Tracking_Sheet.picked_user_id == db_employee_id),
                models.shell_Tracking_Sheet.picked_status == "Open")
            ).order_by(
                ordering,
                models.shell_Tracking_Sheet.picked_status.desc(),
                models.shell_Tracking_Sheet.four_digit_store_number.asc(),
                models.shell_Tracking_Sheet.priority.asc(),
                # models.shell_Tracking_Sheet.planogram_type
            ).first()
            try:
                data = {}
                data['unique_id'] = db_res3.id
                data['project_id'] = db_project_id
                data['project_name'] = db_res3._shell_project6.project_name
                data['cycle_id'] = db_cycle_id
                data['cycle_name'] = db_res3._cycle_table2.cycle_name
                data['demography_id'] = db_res3._shell_project6.project_demography
                data['demography_name'] = db_res3._shell_project6._demography.demography_name
                data['store_number'] = db_res3.four_digit_store_number
                data['eight_digit_store_number'] = db_res3.store_number
                data['department_name'] = db_res3.department_name
                data['planogram_type'] = db_res3.planogram_type
                data['planogram_name'] = db_res3.planogram_name
                data['total_no_of_sku'] = db_res3.sku

                temp = db_res3.department_name+"/"+db_res3.planogram_type+"/"+db_res3.four_digit_store_number

                
                db_res4 = db.query(models.shell_Planogram).filter(models.shell_Planogram.project_id == db_project_id,models.shell_Planogram.cycle_id == db_cycle_id,models.shell_Planogram.pdf_path_name.like(f'%{db_res3.planogram_name}%')).all()
                pdf_list = []
                for row in db_res4:
                    pdf_list.append(str(row.pdf_path_name).replace("\\","/"))
                data['pdf_path_name'] = pdf_list

                # print(temp)
                db_res5 = db.query(models.shell_Store_Image).filter(
                    models.shell_Store_Image.project_id == db_project_id,
                    models.shell_Store_Image.cycle_id == db_cycle_id,
                    models.shell_Store_Image.image_path_name.like(f'%{temp}%')
                ).order_by(models.shell_Store_Image.image_path_name.asc()).all()
                image_list = []
                for row in db_res5:
                    image_list.append(str(row.image_path_name).replace("\\",'/'))
                data['image_path_name'] = image_list

                db_res6 = db.query(models.shell_Project_Selected_Annotation).filter(
                    models.shell_Project_Selected_Annotation.project_id == db_project_id
                ).all()
                data2 = {}
                annotation_id = []
                annotate_shape_name = []
                annotate_color_name = []
                annotate_label_name = []
                for row in db_res6:
                    annotation_id.append(row._annotate_marker.annotatemarker_id)
                    annotate_shape_name.append(row._annotate_marker.annotate_marker_shape_name)
                    annotate_color_name.append(row._annotate_marker.annotate_marker_shape_colour)
                    annotate_label_name.append(row._annotate_marker.annotate_marker_label_name)
                
                data2['annotation_id'] = annotation_id
                data2['annotate_shape_name'] = annotate_shape_name
                data2['annotate_color_name'] = annotate_color_name
                data2['annotate_label_name'] = annotate_label_name

                data['annotation'] = data2

                db_update = db.query(models.shell_Tracking_Sheet).filter(
                    models.shell_Tracking_Sheet.id == db_res3.id
                ).first()
                db_update.picked_status = "Picked"
                db_update.picked_user_id = db_employee_id
                db_update.open_time = datetime.now()
                try:
                    db.commit()
                except :
                    db.rollback()
                    return "Failure"
                
                total_counter = db.query(models.shell_Tracking_Sheet).filter(
                    models.shell_Tracking_Sheet.project_id==int(db_project_id),
                    models.shell_Tracking_Sheet.cycle_id == int(db_cycle_id),
                    models.shell_Tracking_Sheet.picked_status == 'Open'
                ).count()

                # print(total_counter)

                total_counter_today = db.query(models.shell_Tracking_Sheet).filter(
                    models.shell_Tracking_Sheet.project_id==int(db_project_id),
                    models.shell_Tracking_Sheet.cycle_id == int(db_cycle_id),
                    models.shell_Tracking_Sheet.picked_status == 'Completed',
                    models.shell_Tracking_Sheet.picked_user_id == db_employee_id,
                    func.cast(models.shell_Tracking_Sheet.close_time,Date) == datetime.now().date()
                ).count()

                # print(total_counter_today)

                skipped_counter = db.query(models.shell_Tracking_Sheet).filter(
                    models.shell_Tracking_Sheet.project_id==int(db_project_id),
                    models.shell_Tracking_Sheet.cycle_id == int(db_cycle_id),
                    models.shell_Tracking_Sheet.picked_status == 'Skipped',
                    models.shell_Tracking_Sheet.picked_user_id == db_employee_id,
                    func.cast(models.shell_Tracking_Sheet.close_time,Date) == datetime.now().date()
                ).count()

                data['skiped_count'] = skipped_counter
                data['completed'] = total_counter_today
                data['total'] = total_counter
                
                production_list.append(data)

                return production_list

            except:
                data = {}

                total_counter = db.query(models.shell_Tracking_Sheet).filter(
                        models.shell_Tracking_Sheet.project_id==int(db_project_id),
                        models.shell_Tracking_Sheet.cycle_id == int(db_cycle_id),
                        models.shell_Tracking_Sheet.picked_status == 'Open'
                    ).count()

                # print(total_counter)

                total_counter_today = db.query(models.shell_Tracking_Sheet).filter(
                        models.shell_Tracking_Sheet.project_id==int(db_project_id),
                        models.shell_Tracking_Sheet.cycle_id == int(db_cycle_id),
                        models.shell_Tracking_Sheet.picked_status == 'Completed',
                        models.shell_Tracking_Sheet.picked_user_id == db_employee_id,
                        func.cast(models.shell_Tracking_Sheet.close_time,Date) == datetime.now().date()
                    ).count()

                # print(total_counter_today)

                skipped_counter = db.query(models.shell_Tracking_Sheet).filter(
                        models.shell_Tracking_Sheet.project_id==int(db_project_id),
                        models.shell_Tracking_Sheet.cycle_id == int(db_cycle_id),
                        models.shell_Tracking_Sheet.picked_status == 'Skipped',
                        models.shell_Tracking_Sheet.picked_user_id == db_employee_id,
                        func.cast(models.shell_Tracking_Sheet.close_time,Date) == datetime.now().date()
                    ).count()
                data['skiped_count'] = skipped_counter
                data['completed'] = total_counter_today
                data['total'] = total_counter
                    
                production_list.append(data)
                return production_list
    
    
    else:
        data = {}

        total_counter = db.query(models.shell_Tracking_Sheet).filter(
                models.shell_Tracking_Sheet.project_id==int(db_project_id),
                models.shell_Tracking_Sheet.cycle_id == int(db_cycle_id),
                models.shell_Tracking_Sheet.picked_status == 'Open'
            ).count()

        # print(total_counter)

        total_counter_today = db.query(models.shell_Tracking_Sheet).filter(
                models.shell_Tracking_Sheet.project_id==int(db_project_id),
                models.shell_Tracking_Sheet.cycle_id == int(db_cycle_id),
                models.shell_Tracking_Sheet.picked_status == 'Completed',
                models.shell_Tracking_Sheet.picked_user_id == db_employee_id,
                func.cast(models.shell_Tracking_Sheet.close_time,Date) == datetime.now().date()
            ).count()

        # print(total_counter_today)

        skipped_counter = db.query(models.shell_Tracking_Sheet).filter(
                models.shell_Tracking_Sheet.project_id==int(db_project_id),
                models.shell_Tracking_Sheet.cycle_id == int(db_cycle_id),
                models.shell_Tracking_Sheet.picked_status == 'Skipped',
                models.shell_Tracking_Sheet.picked_user_id == db_employee_id,
                func.cast(models.shell_Tracking_Sheet.close_time,Date) == datetime.now().date()
            ).count()
        data['skiped_count'] = skipped_counter
        data['completed'] = total_counter_today
        data['total'] = total_counter
            
        production_list.append(data)
        return production_list
    
#--------------------------------------------------------------------------------------------------

def add_markers_to_pdf(db:Session,input_path, output_path, marker_positions, html_width, html_height, pdf_width, pdf_height, area_x, area_y, area_width, area_height,production_id):
    with open(input_path, 'rb') as input_file:
        pdf_reader = PdfReader(input_file)
        pdf_writer = PdfWriter()
        page = pdf_reader.pages[0]
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=A3)
        can.setFillColor(red)

        #---------------------------------------SAVING AXIS POINTS-----------------------------------------------------------

        db_query = models.shell_Tracking_Sheet_Axis_Points(production_id=production_id,axis_points=marker_positions)
        db.add(db_query)
        db.commit()
        db.refresh(db_query)

        for marker_position in marker_positions:
            print(marker_position)
            html_width = marker_position['ht_width']
            html_height = marker_position['ht_height']
            pdf_x, pdf_y = convert_html_to_pdf_coordinates(marker_position['x'], marker_position['y'], html_width, html_height, pdf_width, pdf_height)
            
            print(pdf_x, pdf_y)
            if marker_position['label'] == "annotation-marker3":
                can.setStrokeColor(red)
                can.setLineWidth(2)
                can.setFont("Helvetica", 12)
                can.setFillColorRGB(1, 0, 0)
                can.drawString(pdf_x+5, pdf_y-18, "X")
            elif marker_position['label'] == "annotation-marker2":
                can.setStrokeColor(colors.blue)
                can.setLineWidth(2)
                can.setFont("Helvetica", 12)
                can.setFillColorRGB(0, 0, 1)
                can.drawString(pdf_x+5, pdf_y-18, "X")
            
            elif marker_position['label'] == "annotation-marker1":
                can.setStrokeColor(colors.green)
                can.setLineWidth(2)
                can.setFont("Helvetica", 12)
                can.setFillColorRGB(0, 0.6, 0)
                can.drawString(pdf_x+2, pdf_y-18, "✓")  
            
         
        can.save()
        packet.seek(0)
        overlay = PdfReader(packet)
        for overlay_page in overlay.pages:
            page.merge_page(overlay_page)
        pdf_writer.add_page(page)

        for page in pdf_reader.pages[1:]:
            pdf_writer.add_page(page)

        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)

def convert_html_to_pdf_coordinates(html_x, html_y, html_width, html_height, pdf_width, pdf_height):
    html_x = float(html_x)/resolution
    html_y = float(html_y)/resolution
    # scale_x = float(pdf_width) / float(html_width) + 0.5999
    # scale_y = float(pdf_height) / float(html_height) + 0.70
    # pdf_x = (float(html_x) * (float(scale_x) * float(1.19)) - 2)
    # pdf_y = float(pdf_height) - (float(html_y) * (float(scale_y) * 1.002) - 18)
    scale_x = float(pdf_width) / float(html_width/resolution)
    scale_y = float(pdf_height) / float(html_height/resolution)
    pdf_x = float(html_x) * float(scale_x)
    pdf_y = float(pdf_height) - (float(html_y) * (float(scale_y)))
    pdf_y = pdf_y + 10
    return pdf_x, pdf_y

#--------------------------------------------------------------------------------------------------

def add_upc(db:Session,upc_json:str,production_id:int):
    temp = upc_json.replace("'", '"')
    upc = json.loads(temp)
    for list_of_upc in upc:
        db_query = models.shell_Tracking_Sheet_UPC(production_id=production_id,product_name=list_of_upc['product_name'],product_upc=list_of_upc['product_upc'],product_distrubtor=list_of_upc['product_distrubtor'])
        db.add(db_query)
        db.commit()

#--------------------------------------------------------------------------------------------------

def add_count(db:Session,production_id:int,g_count:str,b_count:str,r_count:str):
    db_res = db.query(models.shell_Tracking_Sheet).filter(models.shell_Tracking_Sheet.id == production_id).first()
    db_res.green_count = g_count
    db_res.blue_count = b_count
    db_res.red_count = r_count
    db.commit()

#--------------------------------------------------------------------------------------------------

def single_production_completed(db:Session,production_id:int,production_res:str):
    temp = production_res.replace("'", '"')
    production_res_arr = json.loads(temp)
    list_of_pro =  production_res_arr[0]
    print(list_of_pro['workable_status'])
    db_res = db.query(models.shell_Tracking_Sheet).filter(models.shell_Tracking_Sheet.id == production_id).first()
    db_res.workable_status = list_of_pro['workable_status']
    db_res.Image_Qualified_for_Compliance = list_of_pro['Image_Qualified_for_Compliance']
    db_res.No_of_Missing_SKUs = list_of_pro['No_of_Missing_SKUs']
    db_res.Incorrectly_placed_SKUs = list_of_pro['Incorrectly_placed_SKUs']
    db_res.Remarks = list_of_pro['Remarks']
    db_res.No_of_Bays = list_of_pro['No_of_Bays']
    db_res.No_of_Shelves = list_of_pro['No_of_Shelves']
    db_res.Size_of_Bays = list_of_pro['Size_of_Bays']
    db_res.picked_status = "Completed"
    db_res.close_time = datetime.now()
    db.commit()

def skip_production(db:Session,production_id:int):
    db_res = db.query(models.shell_Tracking_Sheet).filter(models.shell_Tracking_Sheet.id == production_id).first()
    db_res.picked_status = "Skipped"
    db_res.close_time = datetime.now()
    db.commit()

#----------------------------------------------AUDIT----------------------------------------------------

def get_audit_question_answer(db:Session,emp_id:str):
    production_list = []
    db_count = db.query(models.shell_User_table).filter(models.shell_User_table.emp_id==emp_id).count()
    if db_count > 0 :
        db_res = db.query(models.shell_User_table).filter(models.shell_User_table.emp_id==emp_id).first()
        db_employee_id = db_res.id
        db_res2 = db.query(models.shell_Project_Cycle_Creation).filter(models.shell_Project_Cycle_Creation.cycle_status=="1").first()
        db_cycle_id = db_res2.id
        db_project_id = db_res2.project_id
        count = db.query(models.shell_Tracking_Sheet).filter(
            models.shell_Tracking_Sheet.project_id == int(db_project_id),
            models.shell_Tracking_Sheet.cycle_id==int(db_cycle_id),
            models.shell_Tracking_Sheet.picked_status == "Completed",
            or_(models.shell_Tracking_Sheet.audit_status == "Picked",
                models.shell_Tracking_Sheet.audit_status == "Open")
            ).count()
        if count > 0:
            db_res3 = db.query(models.shell_Tracking_Sheet).filter(
            models.shell_Tracking_Sheet.project_id == int(db_project_id),
            models.shell_Tracking_Sheet.cycle_id==int(db_cycle_id),
            models.shell_Tracking_Sheet.picked_status == "Completed",
            or_(models.shell_Tracking_Sheet.audit_status == "Picked",
                models.shell_Tracking_Sheet.audit_status == "Open")
            ).order_by(
                models.shell_Tracking_Sheet.picked_status.desc(),
                models.shell_Tracking_Sheet.four_digit_store_number.asc()
            ).first()
            data = {}
            data['unique_id'] = db_res3.id
            data['project_id'] = db_project_id
            data['project_name'] = db_res3._shell_project6.project_name
            data['cycle_id'] = db_cycle_id
            data['cycle_name'] = db_res3._cycle_table2.cycle_name
            data['demography_id'] = db_res3._shell_project6.project_demography
            data['demography_name'] = db_res3._shell_project6._demography.demography_name
            data['store_number'] = db_res3.four_digit_store_number
            data['eight_digit_store_number'] = db_res3.store_number
            data['department_name'] = db_res3.department_name
            data['planogram_type'] = db_res3.planogram_type
            data['planogram_name'] = db_res3.planogram_name
            data['total_no_of_sku'] = db_res3.sku
            data['workable_status'] = db_res3.workable_status
            data['Image_Qualified_for_Compliance'] = db_res3.Image_Qualified_for_Compliance
            data['No_of_Missing_SKUs'] = db_res3.No_of_Missing_SKUs
            data['Incorrectly_placed_SKUs'] = db_res3.Incorrectly_placed_SKUs
            data['Remarks'] = db_res3.Remarks
            data['No_of_Bays'] = db_res3.No_of_Bays
            data['No_of_Shelves'] = db_res3.No_of_Shelves
            data['Size_of_Bays'] = db_res3.Size_of_Bays
            data['green_count'] = db_res3.green_count
            data['red_count'] = db_res3.red_count
            data['blue_count'] = db_res3.blue_count

            total_counter = db.query(models.shell_Tracking_Sheet).filter(
                models.shell_Tracking_Sheet.project_id==int(db_project_id),
                models.shell_Tracking_Sheet.cycle_id == int(db_cycle_id),
                models.shell_Tracking_Sheet.picked_status == 'Completed'
            ).count()

            print(total_counter)

            total_counter_today = db.query(models.shell_Tracking_Sheet).filter(
                models.shell_Tracking_Sheet.project_id==int(db_project_id),
                models.shell_Tracking_Sheet.cycle_id == int(db_cycle_id),
                models.shell_Tracking_Sheet.audit_status == 'Completed',
                models.shell_Tracking_Sheet.audit_user_id == db_employee_id,
                func.cast(models.shell_Tracking_Sheet.close_time,Date) == datetime.now().date()
            ).count()

            print(total_counter_today)

            skipped_counter = db.query(models.shell_Tracking_Sheet).filter(
                models.shell_Tracking_Sheet.project_id==int(db_project_id),
                models.shell_Tracking_Sheet.cycle_id == int(db_cycle_id),
                models.shell_Tracking_Sheet.audit_status == 'Skipped',
                models.shell_Tracking_Sheet.audit_user_id == db_employee_id,
                func.cast(models.shell_Tracking_Sheet.close_time,Date) == datetime.now().date()
            ).count()

            data['skiped_count'] = skipped_counter
            data['completed'] = total_counter_today
            data['total'] = total_counter



            temp = db_res3.department_name+"/"+db_res3.planogram_type+"/"+db_res3.four_digit_store_number

            
            db_res4 = db.query(models.shell_Planogram).filter(models.shell_Planogram.pdf_path_name.like(f'%{db_res3.planogram_name}%')).all()
            pdf_list = []
            for row in db_res4:
                temppr = str(row.pdf_path_name).replace("\\","/")
                temppr2 = temppr.split(".")
                temppr3 = temppr2[0]+"_output."+temppr2[1]
                pdf_list.append(temppr)

            data['pdf_path_name'] = pdf_list

            db_res5 = db.query(models.shell_Store_Image).filter(
                models.shell_Store_Image.image_path_name.like(f'%{temp}%')
            ).all()
            image_list = []
            for row in db_res5:
                image_list.append(str(row.image_path_name).replace("\\",'/'))
            data['image_path_name'] = image_list

            db_res6 = db.query(models.shell_Project_Selected_Annotation).filter(
                models.shell_Project_Selected_Annotation.project_id == db_project_id
            ).all()
            data2 = {}
            annotation_id = []
            annotate_shape_name = []
            annotate_color_name = []
            annotate_label_name = []
            for row in db_res6:
                annotation_id.append(row._annotate_marker.annotatemarker_id)
                annotate_shape_name.append(row._annotate_marker.annotate_marker_shape_name)
                annotate_color_name.append(row._annotate_marker.annotate_marker_shape_colour)
                annotate_label_name.append(row._annotate_marker.annotate_marker_label_name)
            
            data2['annotation_id'] = annotation_id
            data2['annotate_shape_name'] = annotate_shape_name
            data2['annotate_color_name'] = annotate_color_name
            data2['annotate_label_name'] = annotate_label_name

            data['annotation'] = data2

            db_update = db.query(models.shell_Tracking_Sheet).filter(
                models.shell_Tracking_Sheet.id == db_res3.id
            ).first()
            db_update.audit_status = "Picked"
            db_update.audit_user_id = db_employee_id
            db_update.audit_open_time = datetime.now()
            try:
                db.commit()
            except :
                db.rollback()
                return "Failure"
            
            production_list.append(data)

        return production_list
    
    else:
        data = {}
        data['status'] = "No Completed Production"
        production_list.append(data)
        return production_list
    
#--------------------------------------------------------------------------------------------------

def get_productioned_upc(db:Session,production_id:int):
    upc_list = []
    db_res = db.query(models.shell_Tracking_Sheet_UPC).filter(
        models.shell_Tracking_Sheet_UPC.production_id == production_id
    ).all()

    for row in db_res:
        data = {}
        data['id'] = row.id
        data['production_name'] = row.product_name
        data['production_upc'] = row.product_upc
        data['production_distrubutor'] = row.product_distrubtor
        upc_list.append(data)
    
    return upc_list

#--------------------------------------------------------------------------------------------------

def add_audit_upc(db:Session,upc_json:str,production_id:int):
    temp = upc_json.replace("'", '"')
    upc = json.loads(temp)
    for list_of_upc in upc:
        db_query = models.shell_Tracking_Sheet_Audit_UPC(production_id=production_id,product_name=list_of_upc['product_name'],product_upc=list_of_upc['product_upc'],product_distrubtor=list_of_upc['product_distrubtor'])
        db.add(db_query)
        db.commit()

#--------------------------------------------------------------------------------------------------

def add_audit_count(db:Session,production_id:int,g_count:str,b_count:str,r_count:str):
    db_res = db.query(models.shell_Tracking_Sheet).filter(models.shell_Tracking_Sheet.id == production_id).first()
    db_res.audit_green_count = g_count
    db_res.audit_blue_count = b_count
    db_res.audit_red_count = r_count
    db.commit()

#--------------------------------------------------------------------------------------------------

def single_audit_completed(db:Session,production_id:int,production_res:str):
    temp = production_res.replace("'", '"')
    production_res_arr = json.loads(temp)
    list_of_pro =  production_res_arr[0]
    db_res = db.query(models.shell_Tracking_Sheet).filter(models.shell_Tracking_Sheet.id == production_id).first()
    db_res.workable_status = list_of_pro['workable_status']
    db_res.Image_Qualified_for_Compliance = list_of_pro['Image_Qualified_for_Compliance']
    db_res.No_of_Missing_SKUs = list_of_pro['No_of_Missing_SKUs']
    db_res.Incorrectly_placed_SKUs = list_of_pro['Incorrectly_placed_SKUs']
    db_res.Remarks = list_of_pro['Remarks']
    db_res.No_of_Bays = list_of_pro['No_of_Bays']
    db_res.No_of_Shelves = list_of_pro['No_of_Shelves']
    db_res.Size_of_Bays = list_of_pro['Size_of_Bays']
    db_res.audit_status = "Completed"
    db_res.audit_close_time = datetime.now()
    db.commit()

#--------------------------------------------------------------------------------------------------

def add_markers_to_pdf_for_audit(db:Session,input_path, output_path, marker_positions, html_width, html_height, pdf_width, pdf_height, area_x, area_y, area_width, area_height,production_id):
    with open(input_path, 'rb') as input_file:
        pdf_reader = PdfReader(input_file)
        pdf_writer = PdfWriter()
        page = pdf_reader.pages[0]
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=A3)
        can.setFillColor(red)

        #---------------------------------------SAVING AXIS POINTS-----------------------------------------------------------

        db_query = models.shell_Tracking_Sheet_Audit_Axis_Points(production_id=production_id,axis_points=marker_positions)
        db.add(db_query)
        db.commit()
        db.refresh(db_query)

        for marker_position in marker_positions:
            html_width = marker_position['ht_width']
            html_height = marker_position['ht_height']
            pdf_x, pdf_y = convert_html_to_pdf_coordinates_audit(marker_position['x'], marker_position['y'], html_width, html_height, pdf_width, pdf_height)
            
            print(pdf_x, pdf_y)
            if marker_position['label'] == "annotation-marker3":
                can.setStrokeColor(red)
                can.setLineWidth(2)
                can.setFont("Helvetica", 12)
                can.setFillColorRGB(1, 0, 0)
                can.drawString(pdf_x+5, pdf_y-18, "X")
            elif marker_position['label'] == "annotation-marker2":
                can.setStrokeColor(colors.blue)
                can.setLineWidth(2)
                can.setFont("Helvetica", 12)
                can.setFillColorRGB(0, 0, 1)
                can.drawString(pdf_x+5, pdf_y-18, "X")
            
            elif marker_position['label'] == "annotation-marker1":
                can.setStrokeColor(colors.green)
                can.setLineWidth(2)
                can.setFont("Helvetica", 12)
                can.setFillColorRGB(0, 0.6, 0)
                can.drawString(pdf_x+3, pdf_y-18, "✓")  
            
         
        can.save()
        packet.seek(0)
        overlay = PdfReader(packet)
        for overlay_page in overlay.pages:
            page.merge_page(overlay_page)
        pdf_writer.add_page(page)

        for page in pdf_reader.pages[1:]:
            pdf_writer.add_page(page)

        with open(output_path, 'wb') as output_file:
            pdf_writer.write(output_file)

def convert_html_to_pdf_coordinates_audit(html_x, html_y, html_width, html_height, pdf_width, pdf_height):
    html_x = float(html_x)/resolution
    html_y = float(html_y)/resolution
    scale_x = float(pdf_width) / float(html_width/resolution)
    scale_y = float(pdf_height) / float(html_height/resolution)
    pdf_x = float(html_x) * float(scale_x)
    pdf_y = float(pdf_height) - (float(html_y) * (float(scale_y)))
    pdf_y = pdf_y + 10
    return pdf_x, pdf_y

#--------------------------------------------------------------------------------------------------

def get_axis_points_for_audit(db:Session,production_id:int):
    db_res = db.query(models.shell_Tracking_Sheet_Axis_Points).filter(
        models.shell_Tracking_Sheet_Axis_Points.production_id == production_id
        ).first()
    temp = db_res.axis_points
    return temp

def skip_audit(db:Session,production_id:int):
    db_res = db.query(models.shell_Tracking_Sheet).filter(models.shell_Tracking_Sheet.id == production_id).first()
    db_res.audit_status = "Skipped"
    db_res.audit_close_time = datetime.now()
    db.commit()
#--------------------------------------------END OF AUDIT------------------------------------------------------

def planogram_type_category(db:Session):
    planogram_type=[]
    db_res = db.query(models.shell_Tracking_Sheet).distinct(models.shell_Tracking_Sheet.planogram_type).all()
    for row in db_res:
        planogram_type.append(row.planogram_type)
    return planogram_type

def employee_specialisation(db:Session,emp_id_str:str,specialization_str:str):
    try:
        emp_id_arr = emp_id_str.split(",")
        for row in emp_id_arr:
            db_res = db.query(models.shell_User_table).filter(models.shell_User_table.emp_id == row).first()
            db_res.specialization = specialization_str
            db.commit()
        return "Success"
    except:
        return "Failure"
    
def employee_list(db:Session):
    db_res = db.query(models.shell_User_table).filter(models.shell_User_table.user_status==1).all()
    return db_res

def retrieve_picked(db:Session,project_id:int,cycle_id:int,retrieve_type:str):
    if retrieve_type == "Production":
        db_res = db.query(models.shell_Tracking_Sheet).join(models.shell_User_table,models.shell_Tracking_Sheet.picked_user_id==models.shell_User_table.id).options(joinedload(models.shell_Tracking_Sheet._user_table1)).filter(
            models.shell_Tracking_Sheet.picked_status=="Picked",
            models.shell_Tracking_Sheet.audit_status=="Open",
            models.shell_Tracking_Sheet.project_id==project_id,
            models.shell_Tracking_Sheet.cycle_id==cycle_id).all()
        return db_res
    elif retrieve_type == "Audit":
        db_res = db.query(models.shell_Tracking_Sheet).join(models.shell_User_table,models.shell_Tracking_Sheet.picked_user_id==models.shell_User_table.id).options(joinedload(models.shell_Tracking_Sheet._user_table1)).filter(
            models.shell_Tracking_Sheet.picked_status=="Completed",
            models.shell_Tracking_Sheet.audit_status=="Picked",
            models.shell_Tracking_Sheet.project_id==project_id,
            models.shell_Tracking_Sheet.cycle_id==cycle_id).all()
        return db_res
    
def reallocation(db:Session,production_id:str,user_id:str,reallocate_type:str):
    production_id_list = production_id.split(",")
    if user_id == 0:
        if reallocate_type == "Production":
            db_query = db.query(models.shell_Tracking_Sheet).filter(models.shell_Tracking_Sheet.id.in_(production_id_list)).all()
            for db_res in db_query:
                db_res.picked_user_id = None
                db_res.picked_status = "Open"
                db.commit()

        elif reallocate_type == "Audit":
            db_query = db.query(models.shell_Tracking_Sheet).filter(models.shell_Tracking_Sheet.id.in_(production_id_list)).all()
            for db_res in db_query:
                db_res.audit_user_id = None
                db_res.audit_status = "Open"
                db.commit()
    else:
        if reallocate_type == "Production":
            db_query = db.query(models.shell_Tracking_Sheet).filter(models.shell_Tracking_Sheet.id.in_(production_id_list)).all()
            for db_res in db_query:
                db_res.picked_user_id = user_id
                db_res.picked_status = "Picked"
                db.commit()

        elif reallocate_type == "Audit":
            db_query = db.query(models.shell_Tracking_Sheet).filter(models.shell_Tracking_Sheet.id.in_(production_id_list)).all()
            for db_res in db_query:
                db_res.audit_user_id = user_id
                db_res.audit_status = "Picked"
                db.commit()

    return "Success"

def production_report(db:Session,Project_id:int,Cycle_id:int,from_date:str,to_date:str):
    query = db.query(models.shell_Project_Creation_table.project_name,models.shell_Project_Cycle_Creation.cycle_name,models.shell_Tracking_Sheet,models.shell_User_table.emp_id).filter(
        models.shell_Tracking_Sheet.picked_user_id == models.shell_User_table.id,
        models.shell_Tracking_Sheet.project_id == models.shell_Project_Creation_table.id,
        models.shell_Tracking_Sheet.cycle_id == models.shell_Project_Cycle_Creation.id,
        models.shell_Tracking_Sheet.project_id==Project_id,
        models.shell_Tracking_Sheet.cycle_id==Cycle_id,
        models.shell_Tracking_Sheet.picked_status=="Completed",
        models.shell_Tracking_Sheet.audit_status=='Open',
        func.DATE(models.shell_Tracking_Sheet.close_time) >= datetime.strptime(from_date, "%Y-%m-%d").date(),
        func.DATE(models.shell_Tracking_Sheet.close_time) <= datetime.strptime(to_date, "%Y-%m-%d").date()
        ).order_by(models.shell_Tracking_Sheet.id.asc())
    
    df = pd.read_sql(query.statement,db.bind)

    columns_to_remove = ['project_id','cycle_id','id','created_at','created_by','picked_user_id','status','audit_green_count','audit_red_count','audit_blue_count','audit_status','audit_user_id','audit_open_time','audit_close_time']
    df.drop(columns=columns_to_remove,inplace=True)
    df.rename(columns={"picked_status":"Production_status"},inplace=True)
    return df

def production_report_zip_file(db:Session,Project_id:int,Cycle_id:int,from_date:str,to_date:str):
    res = db.query(models.shell_Tracking_Sheet).filter(
        models.shell_Tracking_Sheet.project_id==Project_id,
        models.shell_Tracking_Sheet.cycle_id==Cycle_id,
        models.shell_Tracking_Sheet.picked_status=="Completed",
        models.shell_Tracking_Sheet.audit_status=='Open',
        func.DATE(models.shell_Tracking_Sheet.close_time) >= datetime.strptime(from_date, "%Y-%m-%d").date(),
        func.DATE(models.shell_Tracking_Sheet.close_time) <= datetime.strptime(to_date, "%Y-%m-%d").date()
        ).order_by(models.shell_Tracking_Sheet.id.asc()).all()

    s = io.BytesIO()
    zip_name = "production_"+from_date+"_"+to_date+".zip"
    with zipfile.ZipFile(s, 'w') as zipf:
        for row in res:
            file_path = os.path.join("upload_pdf/"+str(row.cycle_id), row.planogram_name+"_"+row.store_number+"_output.pdf")
            print(file_path)
            if os.path.isfile(file_path):
                arcname = os.path.join(zip_name, row.planogram_name+"_"+row.store_number+"_output.pdf")
                zipf.write(file_path, arcname)
            else:
                continue
    s.seek(0)
    response = StreamingResponse(s, media_type="application/x-zip-compressed")
    response.headers["Content-Disposition"] = f"attachment; filename="+zip_name
    return response

def audit_report_zip_file(db:Session,Project_id:int,Cycle_id:int,from_date:str,to_date:str):
    res = db.query(models.shell_Tracking_Sheet).filter(
        models.shell_Tracking_Sheet.project_id==Project_id,
        models.shell_Tracking_Sheet.cycle_id==Cycle_id,
        models.shell_Tracking_Sheet.picked_status=="Completed",
        models.shell_Tracking_Sheet.audit_status=='Completed',
        func.DATE(models.shell_Tracking_Sheet.close_time) >= datetime.strptime(from_date, "%Y-%m-%d").date(),
        func.DATE(models.shell_Tracking_Sheet.close_time) <= datetime.strptime(to_date, "%Y-%m-%d").date()
        ).order_by(models.shell_Tracking_Sheet.id.asc()).all()
    s = io.BytesIO()
    zip_name = "audit_"+from_date+"_"+to_date+".zip"
    with zipfile.ZipFile(s, 'w') as zipf:
        for row in res:
            file_path = os.path.join("upload_pdf/"+str(row.cycle_id), row.planogram_name+"_"+row.store_number+"_audit.pdf")
            print(file_path)
            if os.path.isfile(file_path):
                arcname = os.path.join(zip_name, row.planogram_name+"_"+row.store_number+"_audit.pdf")
                zipf.write(file_path, arcname)
            else:
                continue
    s.seek(0)
    response = StreamingResponse(s, media_type="application/x-zip-compressed")
    response.headers["Content-Disposition"] = f"attachment; filename="+zip_name
    return response

def audit_report(db:Session,Project_id:int,Cycle_id:int,from_date:str,to_date:str):
    query = db.query(models.shell_Project_Creation_table.project_name,models.shell_Project_Cycle_Creation.cycle_name,models.shell_Tracking_Sheet,models.shell_User_table.emp_id).filter(
        models.shell_Tracking_Sheet.picked_user_id == models.shell_User_table.id,
        models.shell_Tracking_Sheet.project_id == models.shell_Project_Creation_table.id,
        models.shell_Tracking_Sheet.cycle_id == models.shell_Project_Cycle_Creation.id,
        models.shell_Tracking_Sheet.project_id==Project_id,
        models.shell_Tracking_Sheet.cycle_id==Cycle_id,
        models.shell_Tracking_Sheet.picked_status=="Completed",
        models.shell_Tracking_Sheet.audit_status=='Completed',
        func.DATE(models.shell_Tracking_Sheet.close_time) >= datetime.strptime(from_date, "%Y-%m-%d").date(),
        func.DATE(models.shell_Tracking_Sheet.close_time) <= datetime.strptime(to_date, "%Y-%m-%d").date()
        ).order_by(models.shell_Tracking_Sheet.id.asc())
    
    df = pd.read_sql(query.statement,db.bind)
    columns_to_remove = ['project_id','cycle_id','id','created_at','created_by','picked_user_id','status','green_count','red_count','blue_count','Production_status','Production_user_id','open_time','close_time']
    df.drop(columns=columns_to_remove)
    return df
    
def upc_report(db:Session,project_id:int,cycle_id:int):
    query = db.query(models.shell_Tracking_Sheet).filter(
        models.shell_Tracking_Sheet.project_id == project_id,
        models.shell_Tracking_Sheet.cycle_id == cycle_id,
        models.shell_Tracking_Sheet.picked_status == "Completed"
    ).all()

    upc_list = []
    for row in query:
        db_res = db.query(models.shell_Tracking_Sheet_UPC).filter(
            models.shell_Tracking_Sheet_UPC.production_id == row.id
        ).all()
        for row2 in db_res:
            data = {}
            data["Project name"] = row._shell_project6.project_name
            data["Cycle Name"] = row._cycle_table2.cycle_name
            data["Product UPC"] = row2.product_upc
            data["Product Name"] = row2.product_name
            data["Store Number"] = row.store_number
            data["Planogram Name"] = row.planogram_name
            upc_list.append(data)

    print(upc_list)
            
    df = pd.DataFrame(upc_list)
    return df

def audit_report(db:Session,Project_id:int,Cycle_id:int,from_date:str,to_date:str):
    query = db.query(models.shell_Tracking_Sheet,models.shell_User_table.emp_id).filter(
        models.shell_Tracking_Sheet.picked_user_id == models.shell_User_table.id,
        models.shell_Tracking_Sheet.project_id==Project_id,
        models.shell_Tracking_Sheet.cycle_id==Cycle_id,
        models.shell_Tracking_Sheet.picked_status=="Completed",
        models.shell_Tracking_Sheet.audit_status=='Completed',
        func.DATE(models.shell_Tracking_Sheet.close_time) >= datetime.strptime(from_date, "%Y-%m-%d").date(),
        func.DATE(models.shell_Tracking_Sheet.close_time) <= datetime.strptime(to_date, "%Y-%m-%d").date()
        ).order_by(models.shell_Tracking_Sheet.id.asc())
    
    df = pd.read_sql(query.statement,db.bind)
    df.rename(columns={"picked_status":"Production_status","picked_user_id":"Production_user_id"},inplace=True)
    return df
    
def audit_upc_report(db:Session,project_id:int,cycle_id:int):
    query = db.query(models.shell_Tracking_Sheet).filter(
        models.shell_Tracking_Sheet.project_id == project_id,
        models.shell_Tracking_Sheet.cycle_id == cycle_id,
        models.shell_Tracking_Sheet.picked_status == "Completed",
        models.shell_Tracking_Sheet.audit_status == "Completed"
    ).all()

    upc_list = []
    for row in query:
        db_res = db.query(models.shell_Tracking_Sheet_UPC).filter(
            models.shell_Tracking_Sheet_UPC.production_id == row.id
        ).all()
        for row2 in db_res:
            data = {}
            data["Project name"] = row._shell_project6.project_name
            data["Cycle Name"] = row._cycle_table2.cycle_name
            data["Product UPC"] = row2.product_upc
            data["Product Name"] = row2.product_name
            data["Store Number"] = row.store_number
            data["Planogram Name"] = row.planogram_name
            upc_list.append(data)

    print(upc_list)
            
    df = pd.DataFrame(upc_list)
    return df


def pro_hourly_report(db:Session,dater:str,project_id:int,cycle_id:int):
    hourly_list = []
    all_possible_time_slot = []
    
    count = db.query(models.shell_Tracking_Sheet).filter(
        models.shell_Tracking_Sheet.project_id == project_id,
        models.shell_Tracking_Sheet.cycle_id == cycle_id,
        models.shell_Tracking_Sheet.picked_status == "Completed",
        func.DATE(models.shell_Tracking_Sheet.close_time) == datetime.strptime(dater, "%Y-%m-%d").date()
    ).distinct(models.shell_Tracking_Sheet.picked_user_id).count()
    if count >0:
        db_res_dis = db.query(models.shell_Tracking_Sheet).filter(
            models.shell_Tracking_Sheet.project_id == project_id,
            models.shell_Tracking_Sheet.cycle_id == cycle_id,
            models.shell_Tracking_Sheet.picked_status == "Completed",
            func.DATE(models.shell_Tracking_Sheet.close_time) == datetime.strptime(dater, "%Y-%m-%d").date()
        ).distinct(models.shell_Tracking_Sheet.picked_user_id).all()
        for row_user_id in db_res_dis:
            data = {}
            db_get_emp_id = db.query(models.shell_User_table).filter(models.shell_User_table.id==row_user_id.picked_user_id).first()
            data['user_id'] = db_get_emp_id.emp_id
            db_res = db.query(models.shell_Tracking_Sheet).filter(
                models.shell_Tracking_Sheet.project_id == project_id,
                models.shell_Tracking_Sheet.cycle_id == cycle_id,
                models.shell_Tracking_Sheet.picked_user_id == row_user_id.picked_user_id,
                models.shell_Tracking_Sheet.picked_status == "Completed",
                func.DATE(models.shell_Tracking_Sheet.close_time) == datetime.strptime(dater, "%Y-%m-%d").date()
            ).all()
            time_list = []
            finished_list = []
            for row in db_res:
                adjusted_date = row.close_time + timedelta(hours=5,minutes=30)
                end_hour  = adjusted_date.hour
                start_hour = adjusted_date.hour - 1
                temp = str(start_hour)+'-'+str(end_hour)
                time_list.append(temp)
                all_possible_time_slot.append(temp)
            slot_counts = Counter(time_list)
            for slot, count in slot_counts.items():
                finished_list.append(count)
            distinct_time_slots = []
            [distinct_time_slots.append(slot) for slot in time_list if slot not in distinct_time_slots]
            data['time_slot'] = distinct_time_slots
            data['finished_list'] = finished_list
            hourly_list.append(data)

        distinct_time_slots = set(all_possible_time_slot)
        all_time_slots = list(distinct_time_slots)
        df = pd.DataFrame(hourly_list)
        df["time_slot"] = df["time_slot"].apply(lambda x: x + list(set(all_time_slots) - set(x)))
        def get_finished_list(row, slot):
            index = row["time_slot"].index(slot) if slot in row["time_slot"] else None
            return row["finished_list"][index] if index is not None and index < len(row["finished_list"]) else 0
        for slot in all_time_slots:
            df[slot] = df.apply(lambda row: get_finished_list(row, slot), axis=1)
        df.drop(columns=["time_slot", "finished_list"], inplace=True)
        df.sort_values(by="user_id", inplace=True)
        transformed_data = df.to_dict(orient="records")
        df1 = pd.DataFrame(transformed_data)
        df1.set_index("user_id", inplace=True)
        df1.reset_index(inplace=True)
        sorted_columns = sorted(df1.columns[1:])
        df1 = df1.reindex(columns=['user_id'] + sorted_columns)
        df1["overall count"] = df1.iloc[:, 1:].sum(axis=1)
        print(df1)
        return df1
    
    else:
        return ""


def audit_hourly_report(db:Session,dater:str,project_id:int,cycle_id:int):
    hourly_list = []
    all_possible_time_slot = []
    
    count = db.query(models.shell_Tracking_Sheet).filter(
        models.shell_Tracking_Sheet.project_id == project_id,
        models.shell_Tracking_Sheet.cycle_id == cycle_id,
        models.shell_Tracking_Sheet.audit_status == "Completed",
        func.DATE(models.shell_Tracking_Sheet.audit_close_time) == datetime.strptime(dater, "%Y-%m-%d").date()
    ).distinct(models.shell_Tracking_Sheet.audit_user_id).count()
    if count >0:
        db_res_dis = db.query(models.shell_Tracking_Sheet).filter(
            models.shell_Tracking_Sheet.project_id == project_id,
            models.shell_Tracking_Sheet.cycle_id == cycle_id,
            models.shell_Tracking_Sheet.audit_status == "Completed",
            func.DATE(models.shell_Tracking_Sheet.audit_close_time) == datetime.strptime(dater, "%Y-%m-%d").date()
        ).distinct(models.shell_Tracking_Sheet.audit_user_id).all()
        for row_user_id in db_res_dis:
            data = {}
            db_get_emp_id = db.query(models.shell_User_table).filter(models.shell_User_table.id==row_user_id.picked_user_id).first()
            data['user_id'] = db_get_emp_id.emp_id
            db_res = db.query(models.shell_Tracking_Sheet).filter(
                models.shell_Tracking_Sheet.project_id == project_id,
                models.shell_Tracking_Sheet.cycle_id == cycle_id,
                models.shell_Tracking_Sheet.audit_user_id == row_user_id.audit_user_id,
                models.shell_Tracking_Sheet.audit_status == "Completed",
                func.DATE(models.shell_Tracking_Sheet.audit_close_time) == datetime.strptime(dater, "%Y-%m-%d").date()
            ).all()
            time_list = []
            finished_list = []
            for row in db_res:
                adjusted_date = row.audit_close_time + timedelta(hours=5,minutes=30)
                end_hour  = adjusted_date.hour
                start_hour = adjusted_date.hour - 1
                temp = str(start_hour)+'-'+str(end_hour)
                time_list.append(temp)
                all_possible_time_slot.append(temp)
            slot_counts = Counter(time_list)
            for slot, count in slot_counts.items():
                finished_list.append(count)
            distinct_time_slots = []
            [distinct_time_slots.append(slot) for slot in time_list if slot not in distinct_time_slots]
            data['time_slot'] = distinct_time_slots
            data['finished_list'] = finished_list
            hourly_list.append(data)

        distinct_time_slots = set(all_possible_time_slot)
        all_time_slots = list(distinct_time_slots)
        df = pd.DataFrame(hourly_list)
        df["time_slot"] = df["time_slot"].apply(lambda x: x + list(set(all_time_slots) - set(x)))
        def get_finished_list(row, slot):
            index = row["time_slot"].index(slot) if slot in row["time_slot"] else None
            return row["finished_list"][index] if index is not None and index < len(row["finished_list"]) else 0
        for slot in all_time_slots:
            df[slot] = df.apply(lambda row: get_finished_list(row, slot), axis=1)
        df.drop(columns=["time_slot", "finished_list"], inplace=True)
        df.sort_values(by="user_id", inplace=True)
        transformed_data = df.to_dict(orient="records")
        df1 = pd.DataFrame(transformed_data)
        df1.set_index("user_id", inplace=True)
        df1.reset_index(inplace=True)
        sorted_columns = sorted(df1.columns[1:])
        df1 = df1.reindex(columns=['user_id'] + sorted_columns)
        df1["overall count"] = df1.iloc[:, 1:].sum(axis=1)
        print(df1)
        return df1
    else:
        return ""

def load_images(image_paths):
    images = []
    for path in image_paths:
        path = str(path).replace("\\",'/')
        img = cv2.imread(path)
        if img is not None:
            images.append((path, img))
        else:
            print(f"Warning: Couldn't open/read file: {path}")
    return images


def resize_image(img, size=(100, 100)):
    return cv2.resize(img, size)

def compute_similarity(img1, img2):
    # Resize images to a common dimension
    img1_resized = resize_image(img1)
    img2_resized = resize_image(img2)
    
    # Convert images to grayscale
    gray1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2GRAY)
    
    # Compute SSIM between two images
    score, _ = ssim(gray1, gray2, full=True)
    return score

def find_duplicates(image_list, threshold=0.9):
    duplicates = []
    for i in range(len(image_list)):
        for j in range(i + 1, len(image_list)):
            score = compute_similarity(image_list[i][1], image_list[j][1])
            if score > threshold:
                duplicates.append((image_list[i][0], image_list[j][0], score))
    return duplicates


def finding_duplicates(db:Session):
    ramp = []
    project_id = []
    cycle_id = []
    dupli = []
    try:
        db.query(models.duplicate_table).delete()
        db.commit()
        db_res = db.query(models.shell_Store_Image).distinct(models.shell_Store_Image.project_id).all()
        for res in db_res:
            project_id.append(res.project_id)
            db_res_cycle = db.query(models.shell_Store_Image).filter(models.shell_Store_Image.project_id==res.project_id).distinct(models.shell_Store_Image.project_id).all()
            for res_cycle in db_res_cycle:
                cycle_id.append(res_cycle.cycle_id)

        db_res3 = db.query(models.shell_Tracking_Sheet).filter(
        models.shell_Tracking_Sheet.project_id.in_(project_id),
        models.shell_Tracking_Sheet.cycle_id.in_(cycle_id)).all()
        for row3 in db_res3:
            data = {}
            temp = row3.department_name+"/"+row3.planogram_type+"/"+row3.four_digit_store_number
            db_res4 = db.query(models.shell_Store_Image).filter(
            models.shell_Store_Image.image_path_name.like(f'%{temp}%')
            ).order_by(models.shell_Store_Image.image_path_name.asc()).all()
            image_path_array = []
            for row4 in db_res4:
                image_path_array.append(row4.image_path_name)
            data["image_path"] = image_path_array  
            ramp.append(data)

        # # image_paths = [path.replace("\\", "/") for item in data for path in item["image_path"]]
        for res_array in ramp:
            image_paths = res_array['image_path']
            images = load_images(image_paths)
            duplicates = find_duplicates(images)
            for dup in duplicates:
                dupli.append(dup[0]+"---"+dup[1])
                print(f"Duplicate images: {dup[0]} and {dup[1]} with similarity score: {dup[2]}")
        my_set = set(dupli)
        for z in my_set:
            two_images = str(z).split("---")
            cycle_id = str(two_images[0]).split("/")[1]
            duplicate_cycle_id = str(two_images[1]).split("/")[1]
            db_duplicate_add = models.duplicate_table(cycle_id=cycle_id,duplicate_cycle_id=duplicate_cycle_id,original_image_path=two_images[0],duplicate_image_path=two_images[1])
            db.add(db_duplicate_add)
            db.commit()
        return "Success"
    except:
        return "Failure"

def getting_duplicates(db:Session):
    list_data = []
    db_res = db.query(models.duplicate_table).all()
    for row in db_res:
        data = {}
        data["cycle_id"] = row.cycle_id
        data["duplicate_cycle_id"] = row.duplicate_cycle_id
        db_cycle = db.query(models.shell_Project_Cycle_Creation).filter(models.shell_Project_Cycle_Creation.id == row.cycle_id).first()
        data["cycle_name"] =  db_cycle.cycle_name
        db_project = db.query(models.shell_Project_Creation_table).filter(models.shell_Project_Creation_table.id == db_cycle.project_id).first()
        data["project_name"] =  db_project.project_name

        db_cycle1 = db.query(models.shell_Project_Cycle_Creation).filter(models.shell_Project_Cycle_Creation.id == row.duplicate_cycle_id).first()
        data["dupli_cycle_name"] =  db_cycle1.cycle_name
        db_project1 = db.query(models.shell_Project_Creation_table).filter(models.shell_Project_Creation_table.id == db_cycle1.project_id).first()
        data["dupli_project_name"] =  db_project1.project_name

        data["original_image_path"] = row.original_image_path
        data["duplicate_image_path"] = row.duplicate_image_path

        list_data.append(data)

    return list_data        

def get_list_of_project_cycles(db:Session):
    cycle_list =[]
    db_res = db.query(models.shell_Project_Cycle_Creation).all()
    for row in db_res:
        cycle_list_map = {}
        cycle_list_map['project_id_id'] = row.project_id
        cycle_list_map['project_name'] = row._shell_project5.project_name
        cycle_list_map['cycle_id'] = row.id
        cycle_list_map['cycle_name'] = row.cycle_name
        cycle_list_map['cycle_start_date'] = row.cycle_start_date.strftime("%d-%m-%Y")
        cycle_list_map['cycle_end_date'] = row.cycle_end_date.strftime("%d-%m-%Y")
        cycle_list_map['cycle_status'] = row.cycle_status
        cycle_list.append(cycle_list_map)
    json_data = json.dumps(cycle_list)
    return json.loads(json_data)

def activate_cycle(db:Session,project_id:int,cycle_id:int):
    try:
        db.query(models.shell_Project_Cycle_Creation).update({models.shell_Project_Cycle_Creation.cycle_status : 0})
        db.commit()
        db_res = db.query(models.shell_Project_Cycle_Creation).filter(models.shell_Project_Cycle_Creation.project_id == project_id,models.shell_Project_Cycle_Creation.id==cycle_id).first()
        db_res.cycle_status = 1
        db.commit()
        return "Success"
    except:
        return "Failure"
    

def pro_store_hourly_report(db:Session,dater:str,picked_to_date,project_id:int,cycle_id:int):

    date_list = []

    res = db.query(models.shell_Tracking_Sheet).filter(
        models.shell_Tracking_Sheet.project_id == project_id,
        models.shell_Tracking_Sheet.cycle_id == cycle_id,
        func.DATE(models.shell_Tracking_Sheet.close_time) >= datetime.strptime(dater, "%Y-%m-%d").date(),
        func.DATE(models.shell_Tracking_Sheet.close_time) <= datetime.strptime(picked_to_date, "%Y-%m-%d").date()
    ).distinct(models.shell_Tracking_Sheet.four_digit_store_number).order_by(
        models.shell_Tracking_Sheet.four_digit_store_number.asc()
    ).all()

    try:

        for row in res:
            row.four_digit_store_number
            res2 = db.query(models.shell_Tracking_Sheet).filter(
            models.shell_Tracking_Sheet.four_digit_store_number == row.four_digit_store_number
            ).count()
            
            res3 = db.query(models.shell_Tracking_Sheet).filter(
            models.shell_Tracking_Sheet.project_id == project_id,
            models.shell_Tracking_Sheet.cycle_id == cycle_id,
            models.shell_Tracking_Sheet.picked_status == "Completed",
            models.shell_Tracking_Sheet.four_digit_store_number == row.four_digit_store_number,
            ).count()

            if(res==res3):
                res4 = db.query(models.shell_Tracking_Sheet).filter(
                models.shell_Tracking_Sheet.project_id == project_id,
                models.shell_Tracking_Sheet.cycle_id == cycle_id,
                models.shell_Tracking_Sheet.four_digit_store_number == row.four_digit_store_number,
                or_(
                    models.shell_Tracking_Sheet.picked_status=="Completed",
                    models.shell_Tracking_Sheet.picked_status == "Skipped"
                )
                ).order_by(
                models.shell_Tracking_Sheet.close_time.desc()
                ).first()
                
                adjusted_date = row.close_time + timedelta(hours=5,minutes=30)
                end_hour  = adjusted_date.hour
                start_hour = adjusted_date.hour - 1
                temp = str(start_hour)+'-'+str(end_hour)
                
                data = {}
                
                date_only = row.close_time.date()
                date_str = date_only.strftime("%Y-%m-%d")
                
                data["date"] = date_str
                data["store_number"] = row.four_digit_store_number
                data["time"] = temp

                date_list.append(data)

        df = pd.DataFrame(date_list)

        pivot_df = df.groupby(['date', 'time']).size().unstack(fill_value=0)

        print(pivot_df)

        return pivot_df
    except:
        return "No Data"


    #         empty_set = set()

    #         qa_lister = []
    #         counter = 1
            
    #         for i in range(len(date_list)):
    #             if date_list[i]['store_number'] in empty_set:
    #                 continue
    #             for j in range(i+1,len(date_list)):
    #                 if(date_list[i]['date']==date_list[j]['date']and date_list[i]['time']==date_list[j]['time']):
    #                         empty_set.add(date_list[i]['store_number'])
    #                         empty_set.add(date_list[j]['store_number'])
    #                         counter = counter +1
    #                 else:
    #                     continue

    #             data_temp = {}
    #             data_temp["date"] = date_list[i]['date']
    #             data_temp["time"] = date_list[i]['time']
    #             data_temp["counter"] = counter
    #             qa_lister.append(data_temp)
    #             counter = 1



    # df = pd.DataFrame(qa_lister)
    # pivot_df = df.pivot(index='date', columns='time', values='counter').fillna(0)
    # pivot_df = pivot_df.sort_index(axis=1)
    # print(pivot_df)
    # return pivot_df

