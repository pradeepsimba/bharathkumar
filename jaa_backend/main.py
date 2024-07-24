from fastapi import Depends,FastAPI,HTTPException,Form,UploadFile,Response
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated
import pandas as pd
from src import crud, models, schemas
from src.database import SessionLocal, engine
from fastapi.responses import StreamingResponse
import json
import io
from io import BytesIO
import csv
import uuid

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "" with the origins you want to allow
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Add other HTTP methods as needed
    allow_headers=["*"],  # Allow all headers
)
# ----------------------------------------------------------------------------------------

@app.post("/insert_nature_of_work",response_model=str)
def nature_of_work(work_name:Annotated[str,Form()],db: Session = Depends(get_db)):
     return crud.insert_nature_of_work(db,work_name)

@app.get("/get_nature_of_work",response_model=list[schemas.Nature_Of_Work])
def nature_of_work(db: Session = Depends(get_db)):
     return crud.get_nature_of_work(db)

@app.delete("/delete_nature_of_work",response_model=str)
def nature_of_work(work_id:Annotated[int,Form()],db: Session = Depends(get_db)):
     return crud.delete_nature_of_work(db,work_id)

@app.put("/update_nature_of_work",response_model=str)
def nature_of_work(work_id:Annotated[int,Form()],work_name:Annotated[str,Form()],db: Session = Depends(get_db)):
     return crud.update_nature_of_work(db,work_name,work_id)

# ----------------------------------------------------------------------------------------

@app.post("/insert_user",response_model=str)
def insert_user(username:Annotated[str,Form()],role:Annotated[str,Form()],firstname:Annotated[str,Form()],lastname:Annotated[str,Form()],location:Annotated[str,Form()],db:Session=Depends(get_db)):
     return crud.insert_user(db,username,role,firstname,lastname,location)

@app.get("/get_user",response_model=list[schemas.User_table])
def nature_of_work(db:Session = Depends(get_db)):
     return crud.get_user(db)

@app.delete("/delete_user",response_model=str)
def nature_of_work(user_id:Annotated[int,Form()],db: Session = Depends(get_db)):
     return crud.delete_user(db,user_id)

@app.put("/update_user",response_model=str)
def nature_of_work(user_id:Annotated[int,Form()],user_name:Annotated[str,Form()],user_role:Annotated[str,Form()],db: Session = Depends(get_db)):
     return crud.update_user(db,user_id,user_name,user_role)

# ----------------------------------------------------------------------------------------

@app.post("/login_user",response_model=list[schemas.User_table])
def login_user(username:Annotated[str,Form()],password:Annotated[str,Form()],db:Session=Depends(get_db)):
     return crud.login_check(db,username,password)

# ----------------------------------------------------------------------------------------

@app.post("/tl_insert",response_model=str)
def tl (name_of_entity:Annotated[str,Form()],gst_or_tan:Annotated[str,Form()],gst_tan:Annotated[str,Form()],client_grade:Annotated[str,Form()],Priority:Annotated[str,Form()],Assigned_By:Annotated[int,Form()],estimated_d_o_d:Annotated[str,Form()],estimated_time:Annotated[str,Form()],Assigned_To:Annotated[int,Form()],Scope:Annotated[str,Form()],nature_of_work:Annotated[int,Form()],From:Annotated[str,Form()],Actual_d_o_d:Annotated[str,Form()],db:Session=Depends(get_db)):
     return crud.tl_insert(db,name_of_entity,gst_or_tan,gst_tan,client_grade,Priority,Assigned_By,estimated_d_o_d,estimated_time,Assigned_To,Scope,nature_of_work,From,Actual_d_o_d)

@app.post("/tl_insert_bulk",response_model=str)
def tl_insert_bulk(file:UploadFile,db:Session=Depends(get_db)):
     return crud.tl_insert_bulk(db,file)

# ----------------------------------------------------------------------------------------

@app.post("/tm_get",response_model=list)
def tm_get(user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.get_work(db,user_id)

@app.post("/tl_get",response_model=list)
def tm_get(user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.get_work_tl(db,user_id)

# ----------------------------------------------------------------------------------------

@app.post("/start")
def start(service_id:Annotated[int,Form()],type_of_activity:Annotated[str,Form()],no_of_items:Annotated[str,Form()],db:Session=Depends(get_db)):
     return crud.start(db,service_id,type_of_activity,no_of_items)

@app.post("/reallocated")
def reallocated(service_id:Annotated[int,Form()],remarks:Annotated[str,Form()],user_id:Annotated[str,Form()],db:Session=Depends(get_db)):
     return crud.reallocated(db,service_id,remarks,user_id)

# ----------------------------------------------------------------------------------------

@app.post("/get_count",response_model=list)
def get_count(user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.get_count(db,user_id)

@app.post("/get_count_tl",response_model=list)
def get_count_tl(user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.get_count_tl(db,user_id)

# ----------------------------------------------------------------------------------------

# @app.get("/break_check")
# def break_check(db:Session=Depends(get_db)):
#      return crud.get_break_time_info(db)

# ----------------------------------------------------------------------------------------

@app.post("/get_reports")
async def get_reports(response:Response,fields:Annotated[str,Form()],db:Session=Depends(get_db)):
     df = await crud.get_reports(db,fields)
     excel_output = BytesIO()
     with pd.ExcelWriter(excel_output, engine='xlsxwriter') as writer:
          df.to_excel(writer, index=False, sheet_name='Sheet1')
     excel_output.seek(0)
     response.headers["Content-Disposition"] = "attachment; filename=data.xlsx"
     response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
     return Response(content=excel_output.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@app.post("/break_start")
def break_start(service_id:Annotated[int,Form()],remarks:Annotated[str,Form()],user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.break_start(db,service_id,remarks,user_id)

@app.post("/break_end")
def break_end(service_id:Annotated[int,Form()],user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.break_end(db,service_id,user_id)

@app.post("/call_start")
def call_start(service_id:Annotated[int,Form()],remarks:Annotated[str,Form()],user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.call_start(db,service_id,remarks,user_id)

@app.post("/call_end")
def call_end(service_id:Annotated[int,Form()],user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.call_end(db,service_id,user_id)

@app.post("/end_of_day_start")
def end_of_day_start(service_id:Annotated[int,Form()],remarks:Annotated[str,Form()],user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.end_of_day_start(db,service_id,remarks,user_id)

@app.post("/end_of_day_end")
def end_of_day_end(service_id:Annotated[int,Form()],user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.end_of_day_end(db,service_id,user_id)

@app.post("/hold_start")
def hold_start(service_id:Annotated[int,Form()],remarks:Annotated[str,Form()],user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.hold_start(db,service_id,remarks,user_id)

@app.post("/hold_end")
def hold_end(service_id:Annotated[int,Form()],user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.hold_end(db,service_id,user_id)

@app.post("/meeting_start")
def meeting_start(service_id:Annotated[int,Form()],remarks:Annotated[str,Form()],user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.meeting_start(db,service_id,remarks,user_id)

@app.post("/meeting_end")
def meeting_end(service_id:Annotated[int,Form()],user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.meeting_end(db,service_id,user_id)

@app.post("/Completed")
def Completed(service_id:Annotated[int,Form()],remarks:Annotated[str,Form()],count:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.Completed(db,service_id,remarks,count)

@app.post("/User_Wise_Day_Wise_Part_1")
def User_Wise_Day_Wise_Part_1(picked_date:Annotated[str,Form()],to_date:Annotated[str,Form()],db:Session=Depends(get_db)):
     return crud.User_Wise_Day_Wise_Part_1(db,picked_date,to_date)

@app.post("/insert_tds",response_model=str)
def tds(tds:Annotated[str,Form()],db: Session = Depends(get_db)):
     return crud.insert_tds(db,tds)

@app.get("/get_tds",response_model=list[schemas.tds])
def tds(db: Session = Depends(get_db)):
     return crud.get_tds(db)

@app.delete("/delete_tds",response_model=str)
def tds(tds_id:Annotated[int,Form()],db: Session = Depends(get_db)):
     return crud.delete_tds(db,tds_id)

@app.put("/update_tds",response_model=str)
def tds(tds_id:Annotated[int,Form()],tds:Annotated[str,Form()],db: Session = Depends(get_db)):
     return crud.update_tds(db,tds,tds_id)

@app.post("/insert_gst",response_model=str)
def gst(gst:Annotated[str,Form()],db: Session = Depends(get_db)):
     return crud.insert_gst(db,gst)

@app.get("/get_gst",response_model=list[schemas.gst])
def gst(db: Session = Depends(get_db)):
     return crud.get_gst(db)

@app.delete("/delete_gst",response_model=str)
def gst(gst_id:Annotated[int,Form()],db: Session = Depends(get_db)):
     return crud.delete_gst(db,gst_id)

@app.put("/update_gst",response_model=str)
def gst(gst_id:Annotated[int,Form()],gst:Annotated[str,Form()],db: Session = Depends(get_db)):
     return crud.update_gst(db,gst,gst_id)

@app.delete("/delete_entity",response_model=str)
def delete_entity(record_service_id:Annotated[int,Form()],db: Session = Depends(get_db)):
     return crud.delete_entity(db,record_service_id)

@app.post("/reallocated_end")
def reallocated_end(service_id:Annotated[int,Form()],user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.reallocated_end(db,service_id,user_id)
