from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Date, DateTime,JSON
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func

from .database import Base

class shell_Menus(Base):
    __tablename__ = "Shell_Menus"
    menu_id = Column(Integer, primary_key=True, autoincrement=True)
    menu_name=Column(String)
    menu_status=Column(Integer, default=1)
    _shell_menu_permission1 = relationship("shell_menu_permission", back_populates="_menus")

class user_Roles(Base):
    __tablename__ = "User_Roles"
    role_id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String)
    role_status = Column(Integer, default=1)
    _shell_menu_permission2 = relationship("shell_menu_permission", back_populates="_role")
    _shell_project_select_user_with_role1 = relationship("shell_Project_User_Role_table",back_populates="_role_table")


class shell_Demography(Base):
    __tablename__ = "Shell_Demography"
    demography_id = Column(Integer, primary_key=True, autoincrement=True)
    demography_name = Column(String)
    demography_status = Column(Integer, default=1)
    _shell_project1 = relationship("shell_Project_Creation_table", back_populates="_demography")

class shell_DataSource(Base):
    __tablename__ = "Shell_DataSource"
    datasource_id = Column(Integer, primary_key=True, autoincrement=True)
    datasource_type = Column(String)
    datasource_status = Column(Integer, default=1)
    _shell_project2 = relationship("shell_Project_Creation_table", back_populates="_datasource")

class shell_AnnotateMarker(Base):
    __tablename__ = "Shell_AnnotateMarker"
    annotatemarker_id = Column(Integer,primary_key=True,autoincrement=True)
    annotate_marker_shape_name = Column(String)
    annotate_marker_shape_colour = Column(String)
    annotate_marker_label_name = Column(String)
    annotate_marker_status = Column(Integer,default=1)
    _shell_selected_annotation = relationship("shell_Project_Selected_Annotation",back_populates="_annotate_marker")

class shell_menu_permission(Base):
    __tablename__ = "Shell_menu_permission"
    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey(user_Roles.role_id))
    menu_id = Column(Integer, ForeignKey(shell_Menus.menu_id))
    _menus = relationship("shell_Menus", back_populates="_shell_menu_permission1")
    _role = relationship("user_Roles", back_populates="_shell_menu_permission2")

class shell_User_table(Base):
    __tablename__ = "Shell_User_table"
    id = Column(Integer, primary_key=True, autoincrement=True)
    emp_id = Column(String, unique=True)
    name = Column(String)
    mobile = Column(String)
    working_location = Column(String)
    designation = Column(String)
    specialization = Column(String)
    user_status = Column(Integer, default=1)
    _shell_project_select_user_with_role2 = relationship("shell_Project_User_Role_table",back_populates="_user_table")

class shell_Project_Creation_table(Base):
    __tablename__ = "Shell_Project_Creation_Table"
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_name = Column(String)
    project_demography = Column(Integer, ForeignKey(shell_Demography.demography_id))
    project_input_type = Column(Integer, ForeignKey(shell_DataSource.datasource_id))
    project_status = Column(Integer,default=1)
    _demography = relationship("shell_Demography",back_populates="_shell_project1")
    _datasource = relationship("shell_DataSource", back_populates="_shell_project2")
    _project_select_Annotation = relationship("shell_Project_Selected_Annotation", back_populates="_shell_project3")
    _shell_project_select_user_with_role3 = relationship("shell_Project_User_Role_table",back_populates="_shell_project4")
    _cycle_table1 = relationship("shell_Project_Cycle_Creation",back_populates="_shell_project5")
    _tracking_sheet1 = relationship("shell_Tracking_Sheet",back_populates="_shell_project6")
    _store_image1 = relationship("shell_Store_Image",back_populates="_shell_project7")
    _planogram1 = relationship("shell_Planogram",back_populates="_shell_project8")

class shell_Project_Selected_Annotation(Base):
    __tablename__ = "Shell_Project_Selected_Annotation"
    id = Column(Integer,primary_key=True,autoincrement=True)
    project_id = Column(Integer, ForeignKey(shell_Project_Creation_table.id))
    annotation_id = Column(Integer, ForeignKey(shell_AnnotateMarker.annotatemarker_id))
    annotate_marker_status = Column(Integer, default=1)
    _annotate_marker = relationship("shell_AnnotateMarker", back_populates="_shell_selected_annotation")
    _shell_project3 = relationship("shell_Project_Creation_table", back_populates="_project_select_Annotation")

class shell_Project_User_Role_table(Base):
    __tablename__ = "Shell_Project_User_Role_table"
    id = Column(Integer,primary_key=True,autoincrement=True)
    user_id = Column(String, ForeignKey(shell_User_table.emp_id))
    project_id = Column(Integer, ForeignKey(shell_Project_Creation_table.id))
    role_id = Column(Integer, ForeignKey(user_Roles.role_id))
    status = Column(Integer, default=1)
    _user_table = relationship("shell_User_table",back_populates="_shell_project_select_user_with_role2")
    _shell_project4 = relationship("shell_Project_Creation_table", back_populates="_shell_project_select_user_with_role3")
    _role_table = relationship("user_Roles",back_populates="_shell_project_select_user_with_role1")

class shell_Project_Cycle_Creation(Base):
    __tablename__ = "Shell_Project_Cycle_Creation"
    id = Column(Integer,autoincrement=True,primary_key=True)
    project_id = Column(Integer,ForeignKey(shell_Project_Creation_table.id))
    cycle_name = Column(String)
    cycle_start_date = Column(Date)
    cycle_end_date = Column(Date)
    cycle_status = Column(Integer,default=1)
    _shell_project5 = relationship("shell_Project_Creation_table",back_populates="_cycle_table1")
    _tracking_sheet2 = relationship("shell_Tracking_Sheet",back_populates="_cycle_table2")
    _store_image2 = relationship("shell_Store_Image",back_populates="_cycle_table3")
    _planogram2 = relationship("shell_Planogram",back_populates="_cycle_table4")

class shell_Tracking_Sheet(Base):
    __tablename__ = "Shell_Tracking_Sheet"
    id = Column(Integer,primary_key=True,autoincrement=True)
    project_id = Column(Integer,ForeignKey(shell_Project_Creation_table.id))
    cycle_id = Column(Integer,ForeignKey(shell_Project_Cycle_Creation.id))
    store_number = Column(String)
    four_digit_store_number = Column(String)
    store_name = Column(String)
    department_name = Column(String)
    planogram_type = Column(String)
    planogram_name = Column(String)
    sku = Column(String)
    priority = Column(Integer)
    delivery_date = Column(String)
    status = Column(Integer,default=1)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Integer)
    workable_status = Column(String)
    Image_Qualified_for_Compliance = Column(String)
    No_of_Missing_SKUs = Column(String)
    Incorrectly_placed_SKUs = Column(String)
    Remarks = Column(String)
    No_of_Bays = Column(String)
    No_of_Shelves = Column(String)
    Size_of_Bays = Column(String)
    green_count = Column(String)
    red_count = Column(String)
    blue_count = Column(String)
    audit_green_count = Column(String)
    audit_red_count = Column(String)
    audit_blue_count = Column(String)
    picked_status = Column(String,default='Open')
    audit_status = Column(String,default='Open')
    picked_user_id = Column(Integer,ForeignKey(shell_User_table.id))
    audit_user_id = Column(Integer)
    open_time = Column(DateTime(timezone=True))
    close_time = Column(DateTime(timezone=True))
    audit_open_time = Column(DateTime(timezone=True))
    audit_close_time = Column(DateTime(timezone=True))
    _shell_project6 = relationship("shell_Project_Creation_table",back_populates="_tracking_sheet1")
    _cycle_table2 = relationship("shell_Project_Cycle_Creation",back_populates="_tracking_sheet2")
    _user_table1 = relationship("shell_User_table")

class shell_Tracking_Sheet_UPC(Base):
    __tablename__ = "Shell_Tracking_Sheet_UPC"
    id = Column(Integer,autoincrement=True,primary_key=True)
    production_id = Column(Integer,ForeignKey(shell_Tracking_Sheet.id))
    product_name = Column(String)
    product_upc = Column(String)
    product_distrubtor = Column(String)
    _t_sheet = relationship("shell_Tracking_Sheet")

class shell_Tracking_Sheet_Axis_Points(Base):
    __tablename__ = "shell_Tracking_Sheet_axis_points"
    id = Column(Integer,autoincrement=True,primary_key=True)
    production_id = Column(Integer,ForeignKey(shell_Tracking_Sheet.id))
    axis_points = Column(JSON)

class shell_Tracking_Sheet_Audit_UPC(Base):
    __tablename__ = "Shell_Tracking_Sheet_Audit_UPC"
    id = Column(Integer,autoincrement=True,primary_key=True)
    production_id = Column(Integer,ForeignKey(shell_Tracking_Sheet.id))
    product_name = Column(String)
    product_upc = Column(String)
    product_distrubtor = Column(String)
    _t_sheet2 = relationship("shell_Tracking_Sheet")

class shell_Tracking_Sheet_Audit_Axis_Points(Base):
    __tablename__ = "shell_Tracking_Sheet_Audit_axis_points"
    id = Column(Integer,autoincrement=True,primary_key=True)
    production_id = Column(Integer,ForeignKey(shell_Tracking_Sheet.id))
    axis_points = Column(JSON)

class shell_Store_Image(Base):
    __tablename__ = "Shell_Store_Image"
    id = Column(Integer,autoincrement=True,primary_key=True)
    project_id = Column(Integer,ForeignKey(shell_Project_Creation_table.id))
    cycle_id = Column(Integer,ForeignKey(shell_Project_Cycle_Creation.id))
    image_path_name = Column(String)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Integer,ForeignKey(shell_User_table.id))
    _shell_project7 = relationship("shell_Project_Creation_table",back_populates="_store_image1")
    _cycle_table3 = relationship("shell_Project_Cycle_Creation",back_populates="_store_image2")
    _user_table2 = relationship("shell_User_table")

class shell_Planogram(Base):
    __tablename__ = "Shell_Planogram"
    id = Column(Integer,primary_key=True,autoincrement=True)
    project_id = Column(Integer,ForeignKey(shell_Project_Creation_table.id))
    cycle_id = Column(Integer,ForeignKey(shell_Project_Cycle_Creation.id))
    pdf_path_name = Column(String)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Integer,ForeignKey(shell_User_table.id))
    _shell_project8 = relationship("shell_Project_Creation_table",back_populates="_planogram1")
    _cycle_table4 = relationship("shell_Project_Cycle_Creation",back_populates="_planogram2")
    _user_table3 = relationship("shell_User_table")

class duplicate_table(Base):
    __tablename__ = "Duplicate_table"
    id = Column(Integer,primary_key=True,autoincrement=True)
    cycle_id = Column(Integer,ForeignKey(shell_Project_Cycle_Creation.id))
    duplicate_cycle_id = Column(Integer)
    original_image_path = Column(String)
    duplicate_image_path = Column(String)
    _ttt = relationship("shell_Project_Cycle_Creation")

# class dupicatedata(Base):
#     __tablename__ = "Dupicatedata"
#     id = Column(Integer,autoincrement=True,primary_key=True)
#     original = Column(String)
#     duplicate = Column(String)
#     cycle_id = Column(Integer,ForeignKey(shell_Project_Cycle_Creation.id))
#     project_id = Column(Integer,ForeignKey(shell_Project_Creation_table.id))
#     cyclename = Column(String)
    
# class comparestatus(Base):
#     __tablename__ = "Comparestatus"
#     id = Column(Integer,autoincrement=True,primary_key=True)
#     cycle =  Column(String,unique=True)
#     cycle_id = Column(Integer,ForeignKey(shell_Project_Cycle_Creation.id))
#     project_id = Column(Integer,ForeignKey(shell_Project_Creation_table.id))
#     status = Column(Integer,default=0)


    



