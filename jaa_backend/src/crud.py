from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import UploadFile,HTTPException
import pandas as pd
import json
from datetime import date,datetime,timedelta
import os
from zipfile import ZipFile
import tracemalloc
import shutil
from sqlalchemy import cast, or_,and_,func,Date
import csv
from io import BytesIO
#-------------------------------------------------------------------------------------------

def insert_nature_of_work(db:Session,work_name_str:str):
   db_nature_of_work = models.Nature_Of_Work(work_name = work_name_str)
   db.add(db_nature_of_work)
   try:
        db.commit()
        return "Success"
   except :
       db.rollback()
       return "Failure"

def get_nature_of_work(db:Session):
    return db.query(models.Nature_Of_Work).filter(models.Nature_Of_Work.work_status==1).all()

def delete_nature_of_work(db:Session,work_id:int):
    db_res = db.query(models.Nature_Of_Work).filter(models.Nature_Of_Work.work_id==work_id).first()
    db_res.work_status = 0
    try:
        db.commit()
        return "Success"
    except:
        return "Failure"

def update_nature_of_work(db:Session,work_name:str,work_id:int):
    db_res = db.query(models.Nature_Of_Work).filter(models.Nature_Of_Work.work_id==work_id).first()
    db_res.work_name = work_name
    try:
        db.commit()
        return "Success"
    except:
        return "Failure"
    
#-------------------------------------------------------------------------------------------

def insert_user(db:Session,username:str,role:str,firstname:str,lastname:str,location:str):
   db_insert_user = models.User_table(username = username,role=role,firstname = firstname,lastname = lastname,location=location)
   db.add(db_insert_user)
   print(db)
   try:
        db.commit()
        return "Success"
   except :
       db.rollback()
       return "Failure"
   
def get_user(db:Session):
    return db.query(models.User_table).filter(models.User_table.user_status==1).all()

def delete_user(db:Session,user_id:int):
    db_res = db.query(models.User_table).filter(models.User_table.user_id==user_id).first()
    db_res.user_status = 0
    try:
        db.commit()
        return "Success"
    except:
        return "Failure"
    
def update_user(db:Session,user_id:int,username:str,user_role:str):
    db_res = db.query(models.User_table).filter(models.User_table.user_id==user_id).first()
    db_res.username = username
    db_res.role = user_role
    try:
        db.commit()
        return "Success"
    except:
        return "Failure"

#-------------------------------------------------------------------------------------------

def login_check(db:Session,username:str,password:str):
    db_count = db.query(models.User_table).filter(models.User_table.username==username,models.User_table.password==password,models.User_table.user_status==1).count()
    if db_count > 0:
        return db.query(models.User_table).filter(models.User_table.username==username,models.User_table.password==password,models.User_table.user_status==1).all()
    else:
        return []
    
#-------------------------------------------------------------------------------------------

def tl_insert(db:Session,name_of_entity:str,gst_or_tan:str,gst_tan:str,client_grade:str,Priority:str,Assigned_By:int,estimated_d_o_d:str,estimated_time:str,Assigned_To:int,Scope:str,nature_of_work:int,From:str,Actual_d_o_d:str):
    db_insert_tl = models.TL(name_of_entity=name_of_entity,gst_or_tan=gst_or_tan,gst_tan=gst_tan,client_grade=client_grade,Priority=Priority,Assigned_By=Assigned_By,estimated_d_o_d=estimated_d_o_d,estimated_time=estimated_time,Assigned_To=Assigned_To,Scope=Scope,nature_of_work=nature_of_work,From=From,Actual_d_o_d=Actual_d_o_d)
    db.add(db_insert_tl)
    try:
        db.commit()
        return "Success"
    except :
       db.rollback()
       return "Failure"
    
#-------------------------------------------------------------------------------------------

def tl_insert_bulk(db:Session,file1:UploadFile):
    tracemalloc.start()
    if file1.filename.endswith('.csv'):
        df1 = pd.read_csv(file1.file)
        print(df1.to_string())
    else:
        raise HTTPException(status_code=400, detail="File format not supported. Please upload CSV (.csv) files.")
    
    for index,row1 in df1.iterrows():

        nature_of_work = row1['nature_of_work']
        assigned_by = row1['Assigned_By']
        assigned_to = row1['Assigned_To']
        db_res_count = db.query(models.Nature_Of_Work).filter(models.Nature_Of_Work.work_name==nature_of_work,models.Nature_Of_Work.work_status==1).count()
        
        

        if db_res_count>0:
            db_res = db.query(models.Nature_Of_Work).filter(models.Nature_Of_Work.work_name==nature_of_work,models.Nature_Of_Work.work_status==1).first()
            nature_of_work_id = db_res.work_id
            db_res_count1 = db.query(models.User_table).filter(models.User_table.username==assigned_by,models.User_table.user_status==1).count()
            if db_res_count1>0:
                db_res = db.query(models.User_table).filter(models.User_table.username==assigned_by,models.User_table.user_status==1).first()
                assigned_by_id = db_res.user_id
                db_res_count2 = db.query(models.User_table).filter(models.User_table.username==assigned_to,models.User_table.user_status==1).count()
                if db_res_count2>0:
                    db_res = db.query(models.User_table).filter(models.User_table.username==assigned_to,models.User_table.user_status==1).first()
                    assigned_to_id = db_res.user_id
                    db_insert_tl = models.TL(name_of_entity=row1['name_of_entity'],gst_or_tan=row1['gst_or_tan'],gst_tan=row1['gst_tan'],client_grade=row1['client_grade'],Priority=row1['Priority'],Assigned_By=int(assigned_by_id),estimated_d_o_d=row1['estimated_d_o_d'],estimated_time=row1['estimated_time'],Assigned_To=int(assigned_to_id),Scope=row1['Scope'],nature_of_work=int(nature_of_work_id),From=row1['From'],Actual_d_o_d=row1['Actual_d_o_d'])
                    db.add(db_insert_tl)
                    try:
                        db.commit()
                    except :
                        db.rollback()
                else:
                    return "Failure"
            else:
                return "Failure"
        else:
            return "Failure"
    return "Success"
        
#-------------------------------------------------------------------------------------------

def get_work(db:Session,user_id:int):
    task_list = []
    db_res = db.query(models.TL).filter(models.TL.Assigned_To==user_id,models.TL.status==1).all()
    
    for row in db_res:
        data = {}
        data['service_id'] = row.Service_ID
        data['name_of_entity'] = row.name_of_entity
        data['gst_or_tan'] = row.gst_or_tan
        data['gst_tan'] = row.gst_tan
        data['client_grade'] = row.client_grade   
        data['Priority'] = row.Priority
        data['Scope'] = row.Scope
       
        # Fetch Assigned_By details
        db_user = db.query(models.User_table).filter(models.User_table.user_id==row.Assigned_By).first()
        if db_user:
            data['Assigned_By'] = db_user.username
            data['Assigned_By_Id'] = db_user.user_id
        else:
            data['Assigned_By'] = '-'
            data['Assigned_By_Id'] = None

        data['Assigned_Date'] = row.Assigned_Date.strftime("%d-%m-%Y %H:%M:%S")
        data['estimated_d_o_d'] = row.estimated_d_o_d
        data['estimated_time'] = row.estimated_time

        # Fetch Assigned_To details
        db_user = db.query(models.User_table).filter(models.User_table.user_id==row.Assigned_To).first()
        if db_user:
            data['Assigned_To'] = db_user.username
            data['Assigned_To_Id'] = db_user.user_id
        else:
            data['Assigned_To'] = '-'
            data['Assigned_To_Id'] = None

        data['nature_of_work'] = row._nature_of_work.work_name
        data['nature_of_work_id'] = row.nature_of_work
        data['From'] = row.From
        data['Actual_d_o_d'] = row.Actual_d_o_d
        data['created_on'] = row.created_on.strftime("%d-%m-%Y ")
        data['type_of_activity'] = row.type_of_activity
        data['work_status'] = row.work_status
        data['no_of_items'] = row.no_of_items
        data['remarks'] = row.remarks
        data['working_time'] = row.working_time
        data['completed_time'] = row.completed_time
        data['reallocated_time'] = row.reallocated_time
        task_list.append(data)
    json_data = json.dumps(task_list)
    return json.loads(json_data)

def commonfunction_get_work_tl(db, db_res):
    task_list = []
    for row in db_res:
        data = {}
        data['service_id'] = row.Service_ID
        data['name_of_entity'] = row.name_of_entity
        data['gst_or_tan'] = row.gst_or_tan
        data['gst_tan'] = row.gst_tan
        data['client_grade'] = row.client_grade
        data['Priority'] = row.Priority
        data['Scope'] = row.Scope    
        # data['created_on'] = row.created_on
        # print(data['created_on'] , "5555555555555555555555555555555555555555555555555")
       
        # data['created_on'] = row.created_on.date()
       
        # Fetch Assigned_By details
        db_user = db.query(models.User_table).filter(models.User_table.user_id==row.Assigned_By).first()
        if db_user:
            data['Assigned_By'] = db_user.username
            data['Assigned_By_Id'] = db_user.user_id
        else:
            data['Assigned_By'] = '-'
            data['Assigned_By_Id'] = None

        data['Assigned_Date'] = row.Assigned_Date.strftime("%d-%m-%Y %H:%M:%S")
        data['estimated_d_o_d'] = row.estimated_d_o_d
        data['estimated_time'] = row.estimated_time

        # Fetch Assigned_To details
        db_user = db.query(models.User_table).filter(models.User_table.user_id==row.Assigned_To).first()
        if db_user:
            data['Assigned_To'] = db_user.username
            data['Assigned_To_Id'] = db_user.user_id
        else:
            data['Assigned_To'] = '-'
            data['Assigned_To_Id'] = None

        data['nature_of_work'] = row._nature_of_work.work_name
        data['nature_of_work_id'] = row.nature_of_work
        data['From'] = row.From
        data['Actual_d_o_d'] = row.Actual_d_o_d
        data['created_on'] = row.created_on.strftime("%d-%m-%Y ")
        data['type_of_activity'] = row.type_of_activity
        data['work_status'] = row.work_status
        data['no_of_items'] = row.no_of_items
        data['remarks'] = row.remarks
        data['working_time'] = row.working_time
        data['completed_time'] = row.completed_time
        data['reallocated_time'] = row.reallocated_time

        task_list.append(data)

    return json.dumps(task_list)

def get_work_tl(db:Session,user_id:int):
    user_roles = db.query(models.User_table).filter(models.User_table.user_id==user_id,models.User_table.user_status==1).all()
    role = [role.role for role in user_roles]
    if 'TL' in role:
        db_res = db.query(models.TL).filter(models.TL.Assigned_By==user_id,models.TL.status==1).all()
        json_data = commonfunction_get_work_tl(db, db_res)
        return json.loads(json_data)
    else:
        db_res = db.query(models.TL).filter(models.TL.status==1).all()
        json_data = commonfunction_get_work_tl(db, db_res)
        return json.loads(json_data)


#-------------------------------------------------------------------------------------------

def start(db:Session,service_id:int,type_of_activity:str,no_of_items:str):
    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    db_res.type_of_activity = type_of_activity
    db_res.no_of_items = no_of_items
    db_res.work_status = "Work in Progress"
    if db_res.working_time == '':
        current_datetime = datetime.now()
        current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        db_res.working_time = current_datetime_str
    db.commit()
    return "Success"

#-------------------------------------------------------------------------------------------

def reallocated(db:Session,service_id:int,remarks:str,user_id:int):
    # db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    # db_res.work_status = "Reallocated"
    # db_res.remarks = remarks
    # current_datetime = datetime.now()
    # current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    # db_res.reallocated_time = current_datetime_str
    # db.commit()


    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    if db_res:
        # Update the record's fields
        db_res.work_status = "Reallocated_user"
        # db_res.Assigned_To = None
        db_res = db.query(models.TL).filter(models.TL.Assigned_To==user_id,models.TL.status==1).all()
    
        for row in db_res:
            
            # data['service_id'] = row.Service_ID
            name_of_entity = row.name_of_entity
            gst_or_tan = row.gst_or_tan
            gst_tan = row.gst_tan
            client_grade = row.client_grade   
            Priority = row.Priority
            Scope = row.Scope
            nature_of_work = row._nature_of_work.work_name
            nature_of_work_id = row.nature_of_work
            From = row.From
            Actual_d_o_d = row.Actual_d_o_d
            created_on = row.created_on.strftime("%d-%m-%Y ")
            type_of_activity = row.type_of_activity
            work_status = "Reallocated"
            no_of_items = row.no_of_items
            remarks_new = row.remarks
            working_time = row.working_time
            completed_time = row.completed_time
            reallocated_time = row.reallocated_time
            Assigned_By = row.Assigned_By
            estimated_d_o_d = row.estimated_d_o_d
            estimated_time = row.estimated_time

            db_insert = models.TL(name_of_entity=name_of_entity,gst_or_tan=gst_or_tan,gst_tan=gst_tan,client_grade=client_grade,Priority=Priority,Assigned_By=Assigned_By,estimated_d_o_d=estimated_d_o_d,work_status = work_status ,estimated_time=estimated_time,Assigned_To=None,Scope=Scope,nature_of_work=nature_of_work,From=From,Actual_d_o_d=Actual_d_o_d)

        
        db_insert.commit()
        current_datetime = datetime.now()
        current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        db_insert = models.REALLOCATED(Service_ID = service_id,user_id=user_id,re_time_start = current_datetime_str,remarks=remarks)
        db.add(db_insert)
        db.commit()

        return "Success"


def reallocated_end(db:Session,service_id:int,user_id:int):
    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    db_res.work_status = "Not Picked"
    db_res.Assigned_To = user_id
    
    db.commit()
    # current_datetime = datetime.now()
    # current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    # db_res2 = db.query(models.REALLOCATED).filter(
    #     models.REALLOCATED.Service_ID == service_id,
    #     models.REALLOCATED.user_id == user_id
    # ).order_by(
    #     models.REALLOCATED.id.desc()
    # ).first()
    # db_res2.re_time_end = current_datetime_str
    # db.commit()
    return "Success"

#-------------------------------------------------------------------------------------------

def get_count(db:Session,user_id:int):
    count_list = []
    data = {}
    db_completed_count = db.query(models.TL).filter(models.TL.Assigned_To==user_id,models.TL.work_status=="Completed",models.TL.status==1).count()
    data['completed_count'] = db_completed_count

    db_reallocated_count = db.query(models.TL).filter(models.TL.Assigned_To==user_id,models.TL.work_status=="Reallocated",models.TL.status==1).count()
    data['reallocated_count'] = db_reallocated_count

    db_not_picked_count = db.query(models.TL).filter(models.TL.Assigned_To==user_id,models.TL.work_status=="Not Picked",models.TL.status==1).count()
    data['not_picked_count'] = db_not_picked_count

    db_wip_count = db.query(models.TL).filter(models.TL.Assigned_To==user_id,models.TL.work_status=="Work in Progress",models.TL.status==1).count()
    data['wip_count'] = db_wip_count

    db_chargable_count = db.query(models.TL).filter(models.TL.Assigned_To==user_id,models.TL.type_of_activity=="CHARGABLE",models.TL.status==1).count()
    data['chargable_count'] = db_chargable_count

    db_non_chargable_count = db.query(models.TL).filter(models.TL.Assigned_To==user_id,models.TL.type_of_activity=="Non-Charchable",models.TL.status==1).count()
    data['non_chargable_count'] = db_non_chargable_count

    db_hold_count = db.query(models.TL).filter(models.TL.Assigned_To==user_id,models.TL.work_status=="Hold",models.TL.status==1).count()
    data['hold'] = db_hold_count

    db_training = db.query(models.TL).filter(models.TL.Assigned_To==user_id,models.TL.work_status=="End Of Day",models.TL.status==1).count()
    data['Training'] = db_training

    count_list.append(data)
    return count_list

def get_count_tl(db:Session,user_id:int):
    count_list = []
    data = {}
    get_role = db.query(models.User_table).filter(models.User_table.user_id==user_id).all()
    user_role = ''
    if get_role:
        user_role = get_role[0].role
    else:
        print(f"No user found with user_id {user_id}")
    if (user_role == "TL"):
        db_completed_count = db.query(models.TL).filter(models.TL.Assigned_By==user_id,models.TL.work_status=="Completed",models.TL.status==1).count()
        data['completed_count'] = db_completed_count

        db_reallocated_count = db.query(models.TL).filter(models.TL.Assigned_By==user_id,models.TL.work_status=="Reallocated",models.TL.status==1).count()
        data['reallocated_count'] = db_reallocated_count

        db_not_picked_count = db.query(models.TL).filter(models.TL.Assigned_By==user_id,models.TL.work_status=="Not Picked",models.TL.status==1).count()
        data['not_picked_count'] = db_not_picked_count

        db_wip_count = db.query(models.TL).filter(models.TL.Assigned_By==user_id,models.TL.work_status=="Work in Progress",models.TL.status==1).count()
        data['wip_count'] = db_wip_count

        db_chargable_count = db.query(models.TL).filter(models.TL.Assigned_By==user_id,models.TL.type_of_activity=="CHARGABLE",models.TL.status==1).count()
        data['chargable_count'] = db_chargable_count

        db_non_chargable_count = db.query(models.TL).filter(models.TL.Assigned_By==user_id,models.TL.type_of_activity=="Non-Charchable",models.TL.status==1).count()
        data['non_chargable_count'] = db_non_chargable_count

        db_hold_count = db.query(models.TL).filter(models.TL.Assigned_By==user_id,models.TL.work_status=="Hold",models.TL.status==1).count()
        data['hold'] = db_hold_count

        db_training = db.query(models.TL).filter(models.TL.Assigned_By==user_id,models.TL.work_status=="End Of Day",models.TL.status==1).count()
        data['Training'] = db_training

        count_list.append(data)
        return count_list
    elif (user_role == "Admin"):
        db_completed_count = db.query(models.TL).filter(models.TL.work_status=="Completed",models.TL.status==1).count()
        data['completed_count'] = db_completed_count

        db_reallocated_count = db.query(models.TL).filter(models.TL.work_status=="Reallocated",models.TL.status==1).count()
        data['reallocated_count'] = db_reallocated_count

        db_not_picked_count = db.query(models.TL).filter(models.TL.work_status=="Not Picked",models.TL.status==1).count()
        data['not_picked_count'] = db_not_picked_count

        db_wip_count = db.query(models.TL).filter(models.TL.work_status=="Work in Progress",models.TL.status==1).count()
        data['wip_count'] = db_wip_count

        db_chargable_count = db.query(models.TL).filter(models.TL.type_of_activity=="CHARGABLE",models.TL.status==1).count()
        data['chargable_count'] = db_chargable_count

        db_non_chargable_count = db.query(models.TL).filter(models.TL.type_of_activity=="Non-Charchable",models.TL.status==1).count()
        data['non_chargable_count'] = db_non_chargable_count

        db_hold_count = db.query(models.TL).filter(models.TL.work_status=="Hold",models.TL.status==1).count()
        data['hold'] = db_hold_count

        db_training = db.query(models.TL).filter(models.TL.work_status=="End Of Day",models.TL.status==1).count()
        data['Training'] = db_training

        count_list.append(data)
        return count_list

#-------------------------------------------------------------------------------------------

def get_break_time_info(db:Session):
    db_res = db.query(models.TL).all()
    user_list = []
    for row in db_res:
        data = {}
        time_format = "%Y-%m-%d %H:%M:%S"
        time = datetime.strptime(row.break_time_str, time_format) 
        if time.hour > 1:
            data['user_name'] = row._user_table1.username
            data['user_id']=row.Assigned_To
            data['break_time'] = row.break_time_str
            user_list.append(data)
            return user_list
        elif time.hour ==1:
            if time.minute>0:
                data['user_name'] = row._user_table1.username
                data['user_id']=row.Assigned_To
                data['break_time'] = row.break_time_str
                user_list.append(data)
                return user_list
            else:
                return []         
        else:
            return user_list
#-------------------------------------------------------------------------------------------

async def get_reports(db:Session,fields:str):
    column_set = fields.split(",")
    db_res = db.query(models.TL).all()
    df = pd.DataFrame([r.__dict__ for r in db_res])
    new_df = df[column_set]
    return new_df

#-------------------------------------------------------------------------------------------

def break_start(db:Session,service_id:int,remarks:str,user_id:int):
    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    db_res.work_status = "Break"
    db.commit()
    current_datetime = datetime.now()
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    db_insert = models.BREAK(Service_ID = service_id,user_id=user_id,break_time_start = current_datetime_str,remarks=remarks)
    db.add(db_insert)
    db.commit()
    return "Success"

def break_end(db:Session,service_id:int,user_id:int):
    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    db_res.work_status = "Work in Progress"
    db.commit()
    current_datetime = datetime.now()
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    db_res2 = db.query(models.BREAK).filter(
        models.BREAK.Service_ID == service_id,
        models.BREAK.user_id == user_id
    ).order_by(
        models.BREAK.id.desc()
    ).first()
    db_res2.break_time_end = current_datetime_str
    db.commit()
    return "Success"


def call_start(db:Session,service_id:int,remarks:str,user_id:int):
    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    db_res.work_status = "Clarification Call"
    db.commit()
    current_datetime = datetime.now()
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    db_insert = models.CALL(Service_ID = service_id,user_id=user_id,call_time_start = current_datetime_str,remarks=remarks)
    db.add(db_insert)
    db.commit()
    return "Success"

def call_end(db:Session,service_id:int,user_id:int):
    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    db_res.work_status = "Work in Progress"
    db.commit()
    current_datetime = datetime.now()
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    db_res2 = db.query(models.CALL).filter(
        models.CALL.Service_ID == service_id,
        models.CALL.user_id == user_id
    ).order_by(
        models.CALL.id.desc()
    ).first()
    db_res2.call_time_end = current_datetime_str
    db.commit()
    return "Success"


def end_of_day_start(db:Session,service_id:int,remarks:str,user_id:int):
    
    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    db_res.work_status = "End Of Day"
    db.commit()

    current_datetime = datetime.now()
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    
    db_insert = models.END_OF_DAY(Service_ID = service_id,user_id=user_id,end_time_start = current_datetime_str,remarks=remarks)
    db.add(db_insert)
    db.commit()
    
    return "Success"

def end_of_day_end(db:Session,service_id:int,user_id:int):
    
    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    db_res.work_status = "Work in Progress"
    current_datetime = datetime.now()
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    # db_res.reallocated_time = current_datetime_str
    db.commit()
    
    db_res2 = db.query(models.END_OF_DAY).filter(
        models.END_OF_DAY.Service_ID == service_id,
        models.END_OF_DAY.user_id == user_id
    ).order_by(
        models.END_OF_DAY.id.desc()
    ).first()
    db_res2.end_time_end = current_datetime_str
    db.commit()
    return "Success"


def hold_start(db:Session,service_id:int,remarks:str,user_id:int):
    
    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    db_res.work_status = "Hold"
    db.commit()

    current_datetime = datetime.now()
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    
    db_insert = models.HOLD(Service_ID = service_id,user_id=user_id,hold_time_start=current_datetime_str,remarks=remarks)
    db.add(db_insert)
    db.commit()
    
    return "Success"

def hold_end(db:Session,service_id:int,user_id:int):
    
    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    db_res.work_status = "Work in Progress"
    db.commit()
    
    current_datetime = datetime.now()
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    
    db_res2 = db.query(models.HOLD).filter(
        models.HOLD.Service_ID == service_id,
        models.HOLD.user_id == user_id
    ).order_by(
        models.HOLD.id.desc()
    ).first()
    db_res2.hold_time_end = current_datetime_str
    db.commit()
    return "Success"


def meeting_start(db:Session,service_id:int,remarks:str,user_id:int):
    
    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    db_res.work_status = "Meeting"
    db.commit()

    current_datetime = datetime.now()
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    
    db_insert = models.MEETING(Service_ID = service_id,user_id=user_id,meeting_time_start=current_datetime_str,remarks=remarks)
    db.add(db_insert)
    db.commit()
    
    return "Success"

def meeting_end(db:Session,service_id:int,user_id:int):
    
    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    db_res.work_status = "Work in Progress"
    db.commit()
    
    current_datetime = datetime.now()
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    
    db_res2 = db.query(models.MEETING).filter(
        models.MEETING.Service_ID == service_id,
        models.MEETING.user_id == user_id
    ).order_by(
        models.MEETING.id.desc()
    ).first()
    db_res2.meeting_time_end = current_datetime_str
    db.commit()
    return "Success"

def Completed(db:Session,service_id:int,remarks:str,count:str):
    
    current_datetime = datetime.now()
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    db_res.work_status = "Completed"
    db_res.no_of_items = count
    db_res.completed_time = current_datetime_str
    db_res.remarks = remarks
    db.commit()
    return "Success"


#----------------------------------------------------------------------------
def User_Wise_Day_Wise_Part_1(db: Session, picked_date: str, to_date: str):
    date_time_formate_string = '%Y-%m-%d %H:%M:%S'
    list_data = []

    date_time1 = datetime.now()
    todatedd = datetime.strptime(to_date, "%Y-%m-%d")

    db_res = db.query(models.TL).filter(models.TL.status == 1,
        or_(
            models.TL.working_time.between(picked_date, to_date),
            models.TL.reallocated_time.between(picked_date, to_date),
            
        )
    ).all()

    for row in db_res:
        data = {}
        data["date"] = datetime.strptime(row.working_time, date_time_formate_string).date()
        data["user"] = row._user_table1.username
        data["Service_ID"] = row.Service_ID
        data["scope"] = row.Scope
        data["subscopes"] = row.From
        data["entity"] = row.name_of_entity
        data["status"] = row.work_status
        data["type_of_activity"] = row.type_of_activity
        data["Nature_of_Work"] = row._nature_of_work.work_name
        data["gst_tan"] = row.gst_tan
        data["estimated_d_o_d"] =  row.estimated_d_o_d
        data["estimated_time"] =  row.estimated_time
        # username = db.query(User_table).filter(User.user_id == row.Assigned_To).first()
        data["member_name"] = row._user_table1.firstname +' '+ row._user_table1.lastname
        
        date_time2 = datetime.strptime(row.working_time, date_time_formate_string)
        time_diff = date_time1 - date_time2
        work_hour_hours_diff = time_diff


        # -----end of the day
        # db_res2 = db.query(models.END_OF_DAY).filter(
        #     models.END_OF_DAY.Service_ID == row.Service_ID,
        #     cast(models.END_OF_DAY.end_time_start, Date) >= todatedd
        # ).all()

        
        
        
        # end_hour_diff = timedelta(hours=0)
        # date_time_format_string = '%Y-%m-%d %H:%M:%S'
        # for row2 in db_res2:
        #     if row2.end_time_end and row2.end_time_start:

        #         print(row.working_time,row2.end_time_end,row2.end_time_start)
                

        #         datetime_obj1 = datetime.strptime(row2.end_time_start, "%Y-%m-%d %H:%M:%S")
        #         datetime_obj2 = datetime.strptime(row2.end_time_end, "%Y-%m-%d %H:%M:%S")

        #         # Calculate the difference
        #         time_difference = datetime_obj2 - datetime_obj1

        #         print(time_difference,'tttttttttttttttttttttttttttttttttttttt')
        #         current_datetime = datetime.now()
        #         current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")


        #         date_time11 = datetime.strptime(row2.end_time_end, date_time_format_string)
        #         date_time22 = datetime.strptime(row2.end_time_start, date_time_format_string)
        #         time_diff = date_time11 - date_time22
        #         end_hour_diff += time_diff
        #         print(time_diff,'tttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt')
        #     else:
        #         if not (row.work_status == "Completed" or (row.work_status == "in_progress" or row.work_status == "End Of Day")):
        #             print(row.working_time,row2.end_time_end,row2.end_time_start)
                    

        #             datetime_obj1 = datetime.strptime(row2.end_time_start, "%Y-%m-%d %H:%M:%S")
        #             datetime_obj2 = datetime.strptime(row2.end_time_end, "%Y-%m-%d %H:%M:%S")

        #             # Calculate the difference
        #             time_difference = datetime_obj2 - datetime_obj1

        #             print(time_difference,'tttttttttttttttttttttttttttttttttttttt')
        #             current_datetime = datetime.now()
        #             current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

        #             print(current_datetime_str,'####################################################')

        #             print(row.working_time)

        #             datetime_obj1 = datetime.strptime(row2.end_time_start, "%Y-%m-%d %H:%M:%S")
        #             minus = datetime.now()
        #             minus_datetime_str = minus.strftime("%Y-%m-%d %H:%M:%S")

        #             time_difference =  datetime_obj1 - minus_datetime_str


        #             end_hour_diff += time_difference


       
        a = timedelta(hours=0)
        b = timedelta(hours=0)
        if row.work_status == "Reallocated":
            db_res2 = db.query(models.REALLOCATED).filter(
                models.REALLOCATED.Service_ID == row.Service_ID,
                models.REALLOCATED.re_time_start >= picked_date,
                models.REALLOCATED.re_time_end <= to_date
            ).all()

            re_hour_diff = timedelta(hours=0)

            for row2 in db_res2:
                if row2.re_time_start and row2.re_time_end:
                    date_time2r = datetime.strptime(row2.re_time_start, date_time_formate_string)
                    re_time_diff = date_time1 - date_time2r
                    re_hour_diff += re_time_diff
                    data["reallocated"] = re_hour_diff
            a = work_hour_hours_diff
        if row.work_status == "Completed":
            a = work_hour_hours_diff
        else:
            b = work_hour_hours_diff

        # ----- Hold Hour ------
        db_res2 = db.query(models.HOLD).filter(
            models.HOLD.Service_ID == row.Service_ID,
            models.HOLD.hold_time_start >= picked_date,
            models.HOLD.hold_time_end <= to_date
        ).all()

        hold_hour_diff = timedelta(hours=0)

        for row2 in db_res2:
            if row2.hold_time_end and row2.hold_time_start:
                date_time11 = datetime.strptime(row2.hold_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.hold_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                hold_hour_diff += time_diff
            else :
                if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                    time1 =  datetime.now() - datetime.strptime(row2.hold_time_start, date_time_formate_string)
                    hold_hour_diff +=  time1

        data["hold"] = hold_hour_diff

        # ----- Meeting Hour ------
        db_res2 = db.query(models.MEETING).filter(
            models.MEETING.Service_ID == row.Service_ID,
            models.MEETING.meeting_time_start >= picked_date,
            models.MEETING.meeting_time_end <= to_date
        ).all()

        meet_hour_diff = timedelta(hours=0)

        for row2 in db_res2:
            if row2.meeting_time_end and row2.meeting_time_start:
                date_time11 = datetime.strptime(row2.meeting_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.meeting_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                meet_hour_diff += time_diff
            else :
                if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                    time1 =  datetime.now() - datetime.strptime(row2.meeting_time_start, date_time_formate_string)
                    meet_hour_diff +=   time1



        data["meeting"] = meet_hour_diff

        # ----- Break Hour ------
        db_res2 = db.query(models.BREAK).filter(
            models.BREAK.Service_ID == row.Service_ID,
            models.BREAK.break_time_start >= picked_date,
            models.BREAK.break_time_end <= to_date
        ).all()

        break_hour_diff = timedelta(hours=0)

        for row2 in db_res2:
            if row2.break_time_end and row2.break_time_start:
                date_time11 = datetime.strptime(row2.break_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.break_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                break_hour_diff += time_diff
            else :
                if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                    time1 =  datetime.now() - datetime.strptime(row2.break_time_start, date_time_formate_string)
                 
                    break_hour_diff += time1

        data["break"] = break_hour_diff

        # ----- Call Hour ------
        db_res2 = db.query(models.CALL).filter(
            models.CALL.Service_ID == row.Service_ID,
            models.CALL.call_time_start >= picked_date,
            models.CALL.call_time_end <= to_date
        ).all()

        call_hour_diff = timedelta(hours=0)

        for row2 in db_res2:
            if row2.call_time_end and row2.call_time_start:
                date_time11 = datetime.strptime(row2.call_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.call_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                call_hour_diff += time_diff
            else :
                if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                    time1 =  datetime.now() - datetime.strptime(row2.call_time_start, date_time_formate_string)
                   
                    call_hour_diff += time1

        data["call"] = call_hour_diff


        # -----end of the day
        temp = ''
        
        db_res2 = db.query(models.END_OF_DAY).filter(
            models.END_OF_DAY.Service_ID == row.Service_ID,
            models.END_OF_DAY.end_time_start>=picked_date,
            models.END_OF_DAY.end_time_start<=to_date
        ).all()

        count = db.query(models.END_OF_DAY).filter(
            models.END_OF_DAY.Service_ID == row.Service_ID,
            models.END_OF_DAY.end_time_start>=picked_date
        ).count()

        time_diff = timedelta(hours=0)
        if count >= 1 :
            for rom in db_res2:
                if rom.end_time_end == "":
                    temp = rom.end_time_start
                    parsed_date = datetime.strptime(str(temp), '%Y-%m-%d %H:%M:%S')
                    date_time22 = date_time1
                    time_diff += date_time22 - parsed_date
                else:
                    temp = rom.end_time_start
                    parsed_date = datetime.strptime(str(temp), '%Y-%m-%d %H:%M:%S')
                    date_time11 = datetime.strptime(rom.end_time_end, date_time_formate_string)
                    time_diff += date_time11 - parsed_date
        data["end_of_day"] = time_diff
        
        if row.work_status == "Completed":
            e_o_d = data["end_of_day"]
            data["in_progress"] = timedelta(hours=0)
            data["completed"] = (datetime.strptime(row.completed_time, date_time_formate_string) - datetime.strptime(row.working_time, date_time_formate_string)) - (call_hour_diff + break_hour_diff + meet_hour_diff + hold_hour_diff + e_o_d)
            # data["completed"] = (a + b) - (call_hour_diff + break_hour_diff + meet_hour_diff + hold_hour_diff + e_o_d)
        else:
            e_o_d = data["end_of_day"]
            data["completed"] = timedelta(hours=0)
            if row.work_status != "End Of Day":
                data["in_progress"] = (a + b) - (call_hour_diff + break_hour_diff + meet_hour_diff + hold_hour_diff + e_o_d)
            else:
                data["in_progress"] = (a + b) - (call_hour_diff + break_hour_diff + meet_hour_diff + hold_hour_diff + e_o_d)
            print("in progress - ",data["in_progress"])

        # data["total_time_taken"] = call_hour_diff + break_hour_diff + meet_hour_diff + hold_hour_diff + data["completed"] + data["in_progress"]

        data["total_time_taken"] =  (data["in_progress"] + data["completed"] )
        # data["second_report_data"] = call_hour_diff + hold_hour_diff + data["completed"] + data["in_progress"]
        data["second_report_data"] =  data["completed"] + data["in_progress"]

        
#--------------------------------------------------------------------------------------------------------------------------------------
        # ----- HOLD Hour ------
        holdchargable = db.query(models.HOLD).join(
            models.TL, models.HOLD.Service_ID == models.TL.Service_ID
        ).filter(
            models.HOLD.Service_ID == row.Service_ID,
            models.HOLD.hold_time_start >= picked_date,
            models.HOLD.hold_time_end <= to_date,
            models.TL.type_of_activity == 'CHARGABLE'
        ).all()

        holdchargable_hour_diff = timedelta(hours=0)

        for row2 in holdchargable:
            if row2.hold_time_end and row2.hold_time_start:
                date_time11 = datetime.strptime(row2.hold_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.hold_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                holdchargable_hour_diff += time_diff
            else :
                if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                    time1 =  datetime.now() - datetime.strptime(row2.hold_time_start, date_time_formate_string)
                   
                    holdchargable_hour_diff += time1


        
        
        # ----- Meeting Hour ------
        Meetingchargable = db.query(models.MEETING).join(
            models.TL, models.MEETING.Service_ID == models.TL.Service_ID
        ).filter(
            models.MEETING.Service_ID == row.Service_ID,
            models.MEETING.meeting_time_start >= picked_date,
            models.MEETING.meeting_time_end <= to_date,
            models.TL.type_of_activity == 'CHARGABLE'
        ).all()

        meetch_hour_diff = timedelta(hours=0)

        for row2 in Meetingchargable:
            if row2.meeting_time_end and row2.meeting_time_start:
                date_time11 = datetime.strptime(row2.meeting_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.meeting_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                meetch_hour_diff += time_diff
            else :
                if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                    time1 =  datetime.now() - datetime.strptime(row2.meeting_time_start, date_time_formate_string)
                    
                    meetch_hour_diff += time1


        
        
        # ----- Break Hour ------
        Breakchargable = db.query(models.BREAK).join(
            models.TL, models.BREAK.Service_ID == models.TL.Service_ID
        ).filter(
            models.BREAK.Service_ID == row.Service_ID,
            models.BREAK.break_time_start >= picked_date,
            models.BREAK.break_time_end <= to_date,
            models.TL.type_of_activity == 'CHARGABLE'
        ).all()

        breakch_hour_diff = timedelta(hours=0)

        for row2 in Breakchargable:
            if row2.break_time_end and row2.break_time_start:
                date_time11 = datetime.strptime(row2.break_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.break_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                breakch_hour_diff += time_diff
            else :
                if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                    time1 =  datetime.now() - datetime.strptime(row2.break_time_start, date_time_formate_string)
                  
                    breakch_hour_diff += time1


        
        
        # ----- Call Hour ------
        Callchargable = db.query(models.CALL).join(
            models.TL, models.CALL.Service_ID == models.TL.Service_ID
        ).filter(
            models.CALL.Service_ID == row.Service_ID,
            models.CALL.call_time_start >= picked_date,
            models.CALL.call_time_end <= to_date,
            models.TL.type_of_activity == 'CHARGABLE'
        ).all()

        callch_hour_diff = timedelta(hours=0)

        for row2 in Callchargable:
            if row2.call_time_end and row2.call_time_start:
                date_time11 = datetime.strptime(row2.call_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.call_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                callch_hour_diff += time_diff
            else :
                if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                    time1 =  datetime.now() - datetime.strptime(row2.call_time_start, date_time_formate_string)
                 
                    callch_hour_diff += time1

        # -----end of the day
        endch = db.query(models.END_OF_DAY).join(
            models.TL, models.END_OF_DAY.Service_ID == models.TL.Service_ID
        ).filter(
            models.END_OF_DAY.Service_ID == row.Service_ID,
            models.END_OF_DAY.end_time_start >= picked_date,
            models.END_OF_DAY.end_time_end <= to_date,
            models.TL.type_of_activity == 'CHARGABLE'
        ).all()

        endch_hour_diff = timedelta(hours=0)

        for row2 in endch:
            if row2.end_time_end and row2.end_time_start:
                date_time11 = datetime.strptime(row2.end_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.end_time_start, date_time_formate_string)
                time_diff = date_time22 - date_time11
                endch_hour_diff += time_diff
            else :
                if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                    time1 =  datetime.now() - datetime.strptime(row2.end_time_start, date_time_formate_string)
                   
                    endch_hour_diff += time1

        data["endch_hour_diff"] = endch_hour_diff
        if row.type_of_activity == "CHARGABLE":
            data["chargable_time"] = data["in_progress"] + data["completed"]
        else:
            data["chargable_time"] = timedelta(hours=0)

        parsed_time = datetime.strptime(data["estimated_time"], '%H:%M')
        time_delta = timedelta(hours=parsed_time.hour, minutes=parsed_time.minute)

        data["difference_a_b"] = time_delta - data["chargable_time"]
#--------------------------------------------------------------------------------------------------------------------------------------	



#--------------------------------------------------------------------------------------------------------------------------------------
        # ----- HOLD Hour ------
        holdchargable = db.query(models.HOLD).join(
            models.TL, models.HOLD.Service_ID == models.TL.Service_ID
        ).filter(
            models.HOLD.Service_ID == row.Service_ID,
            models.HOLD.hold_time_start >= picked_date,
            models.HOLD.hold_time_end <= to_date,
            models.TL.type_of_activity == 'Non-Charchable'
        ).all()

        holdchargable_hour_diff = timedelta(hours=0)

        for row2 in holdchargable:
            if row2.hold_time_end and row2.hold_time_start:
                date_time11 = datetime.strptime(row2.hold_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.hold_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                holdchargable_hour_diff += time_diff
            else :
                if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                    time1 =  datetime.now() - datetime.strptime(row2.hold_time_start, date_time_formate_string)
                   
                    holdchargable_hour_diff += time1

        
        
        # ----- Meeting Hour ------
        Meetingchargable = db.query(models.MEETING).join(
            models.TL, models.MEETING.Service_ID == models.TL.Service_ID
        ).filter(
            models.MEETING.Service_ID == row.Service_ID,
            models.MEETING.meeting_time_start >= picked_date,
            models.MEETING.meeting_time_end <= to_date,
            models.TL.type_of_activity == 'Non-Charchable'
        ).all()

        meetch_hour_diff = timedelta(hours=0)

        for row2 in Meetingchargable:
            if row2.meeting_time_end and row2.meeting_time_start:
                date_time11 = datetime.strptime(row2.meeting_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.meeting_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                meetch_hour_diff += time_diff
            else :
                if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                    time1 =  datetime.now() - datetime.strptime(row2.meeting_time_start, date_time_formate_string)
                   
                    meetch_hour_diff += time1

        
        
        # ----- Break Hour ------
        Breakchargable = db.query(models.BREAK).join(
            models.TL, models.BREAK.Service_ID == models.TL.Service_ID
        ).filter(
            models.BREAK.Service_ID == row.Service_ID,
            models.BREAK.break_time_start >= picked_date,
            models.BREAK.break_time_end <= to_date,
            models.TL.type_of_activity == 'Non-Charchable'
        ).all()

        breakch_hour_diff = timedelta(hours=0)

        for row2 in Breakchargable:
            if row2.break_time_end and row2.break_time_start:
                date_time11 = datetime.strptime(row2.break_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.break_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                breakch_hour_diff += time_diff
            else :
                if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                    time1 =  datetime.now() - datetime.strptime(row2.break_time_start, date_time_formate_string)
                    
                    breakch_hour_diff += time1


        
        
        # ----- Call Hour ------
        Callchargable = db.query(models.CALL).join(
            models.TL, models.CALL.Service_ID == models.TL.Service_ID
        ).filter(
            models.CALL.Service_ID == row.Service_ID,
            models.CALL.call_time_start >= picked_date,
            models.CALL.call_time_end <= to_date,
            models.TL.type_of_activity == 'Non-Charchable'
        ).all()

        callch_hour_diff = timedelta(hours=0)

        for row2 in Callchargable:
            if row2.call_time_end and row2.call_time_start:
                date_time11 = datetime.strptime(row2.call_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.call_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                callch_hour_diff += time_diff
            else :
                if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                    time1 =  datetime.now() - datetime.strptime(row2.call_time_start, date_time_formate_string)
                  
                    callch_hour_diff += time1




        # -----end of the day
        endch = db.query(models.END_OF_DAY).join(
            models.TL, models.END_OF_DAY.Service_ID == models.TL.Service_ID
        ).filter(
            models.END_OF_DAY.Service_ID == row.Service_ID,
            models.END_OF_DAY.end_time_start >= picked_date,
            models.END_OF_DAY.end_time_end <= to_date,
            models.TL.type_of_activity == 'Non-Charchable'
        ).all()

        endch_hour_diff = timedelta(hours=0)

        for row2 in endch:
            if row2.end_time_end and row2.end_time_start:
                date_time11 = datetime.strptime(row2.end_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.end_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                endch_hour_diff += time_diff
            else :
                if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                    time1 =  datetime.now() - datetime.strptime(row2.end_time_start, date_time_formate_string)
                    endch_hour_diff += time1
	    

        data["endch_hour_diff"] = endch_hour_diff
        if row.type_of_activity == "Non-Charchable":
            data["Non_Charchable_time"] = endch_hour_diff 
        else:
            data["Non_Charchable_time"] = timedelta(hours=0)
        data["chargable_and_non_chargable"] = data["Non_Charchable_time"] + data["chargable_time"]
#--------------------------------------------------------------------------------------------------------------------------------------	


        str_temp = ""
        str_temper = ""

        if row.work_status == "Work in Progress":
            data["third_report_data"] = ""
        elif row.work_status == "Hold":
            db_res3 = db.query(models.HOLD).filter(
                models.HOLD.Service_ID == row.Service_ID,
                models.HOLD.hold_time_start >= picked_date,
                models.HOLD.hold_time_end <= to_date
            ).order_by(models.HOLD.id.desc()).first()
            data["third_report_data"] = db_res3.remarks
            str_temper = db_res3.remarks
        elif row.work_status == "Meeting":
            db_res3 = db.query(models.MEETING).filter(
                models.MEETING.Service_ID == row.Service_ID,
                models.MEETING.meeting_time_start >= picked_date,
                models.MEETING.meeting_time_end <= to_date
            ).order_by(models.MEETING.id.desc()).first()
            data["third_report_data"] = db_res3.remarks
        elif row.work_status == "Break":
            db_res3 = db.query(models.BREAK).filter(
                models.BREAK.Service_ID == row.Service_ID,
                models.BREAK.break_time_start >= picked_date,
                models.BREAK.break_time_end <= to_date
            ).order_by(models.BREAK.id.desc()).first()
            data["third_report_data"] = db_res3.remarks
        elif row.work_status == "Clarification Call":
            db_res3 = db.query(models.CALL).filter(
                models.CALL.Service_ID == row.Service_ID,
                models.CALL.call_time_start >= picked_date,
                models.CALL.call_time_end <= to_date
            ).order_by(models.CALL.id.desc()).first()
            data["third_report_data"] = db_res3.remarks
        elif row.work_status == "Completed":
            data["third_report_data"] = row.remarks

        if row.work_status == "Completed":
            try:
                db_res3 = db.query(models.HOLD).filter(
                    models.HOLD.Service_ID == row.Service_ID,
                    models.HOLD.hold_time_start >= picked_date,
                    models.HOLD.hold_time_end <= to_date
                ).order_by(models.HOLD.id.desc()).first()
                str_temp = str_temp + db_res3.remarks + ","
            except:
                str_temp = ""
            try:
                db_res3 = db.query(models.MEETING).filter(
                    models.MEETING.Service_ID == row.Service_ID,
                    models.MEETING.meeting_time_start >= picked_date,
                    models.MEETING.meeting_time_end <= to_date
                ).order_by(models.MEETING.id.desc()).first()
                str_temp = str_temp + db_res3.remarks + ","
            except:
                str_temp = ""
            try:
                db_res3 = db.query(models.BREAK).filter(
                    models.BREAK.Service_ID == row.Service_ID,
                    models.BREAK.break_time_start >= picked_date,
                    models.BREAK.break_time_end <= to_date
                ).order_by(models.BREAK.id.desc()).first()
                str_temp = str_temp + db_res3.remarks + ","
            except:
                str_temp = ""
            try:
                db_res3 = db.query(models.CALL).filter(
                    models.CALL.Service_ID == row.Service_ID,
                    models.CALL.call_time_start >= picked_date,
                    models.CALL.call_time_end <= to_date
                ).order_by(models.CALL.id.desc()).first()
                str_temp = str_temp + db_res3.remarks + ","
                str_temp = str_temp + row.remarks + ","
            except:
                str_temp = ""

        data["fourth_report"] = row.no_of_items
        data["fourth_report2"] = str_temp
        data["fifth_report"] = str_temper
        list_data.append(data)
    def convert_values(d):
        return dict(map(lambda item: (item[0], str(item[1]).split('.')[0] if not isinstance(item[1], (dict, list)) else item[1]), d.items()))

    converted_list_of_dicts = [convert_values(d) for d in list_data]
    return converted_list_of_dicts

#-------------------------------------------------------------------------------------------

def insert_tds(db:Session,tds_str:str):
   db_tds = models.tds(tds = tds_str)
   db.add(db_tds)
   try:
        db.commit()
        return "Success"
   except :
       db.rollback()
       return "Failure"

def get_tds(db:Session):
    return db.query(models.tds).filter(models.tds.tds_status==1).all()

def delete_tds(db:Session,tds_id:int):
    db_res = db.query(models.tds).filter(models.tds.tds_id==tds_id).first()
    db_res.tds_status = 0
    try:
        db.commit()
        return "Success"
    except:
        return "Failure"

def update_tds(db:Session,tds_name:str,tds_id:int):
    db_res = db.query(models.tds).filter(models.tds.tds_id==tds_id).first()
    db_res.tds = tds_name
    try:
        db.commit()
        return "Success"
    except:
        return "Failure"
    
#-------------------------------------------------------------------------------------------

def insert_gst(db:Session,gst_str:str):
   db_gst = models.gst(gst = gst_str)
   db.add(db_gst)
   try:
        db.commit()
        return "Success"
   except :
       db.rollback()
       return "Failure"

def get_gst(db:Session):
    return db.query(models.gst).filter(models.gst.gst_status==1).all()

def delete_gst(db:Session,gst_id:int):
    db_res = db.query(models.gst).filter(models.gst.gst_id==gst_id).first()
    db_res.gst_status = 0
    try:
        db.commit()
        return "Success"
    except:
        return "Failure"

def update_gst(db:Session,gst:str,gst_id:int):
    db_res = db.query(models.gst).filter(models.gst.gst_id==gst_id).first()
    db_res.gst = gst
    try:
        db.commit()
        return "Success"
    except:
        return "Failure"
    
#-------------------------------------------------------------------------------------------


def delete_entity(db:Session,record_service_id:int):
    db_res = db.query(models.TL).filter(models.TL.Service_ID==record_service_id).first()
    db_res.status = 0
    try:
        db.commit()
        return "Success"
    except:
        return "Failure"
    
#-------------------------------------------------------------------------------------------
