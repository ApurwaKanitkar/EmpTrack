import streamlit as st
import mysql.connector as mys
import pandas as pd

# Connect to the database
mydb = mys.connect(
    host="localhost", 
    user="root", 
    password="L3arn@11t",
    database="Emp_DBMS"
)
mc = mydb.cursor(dictionary=True)

def get_employee_details(emp_id):
    mc.execute("""
    SELECT b.*, p.department, p.organisational_level, p.address, p.designation
    FROM employee_basic_info b
    JOIN employee_professional_info p ON b.emp_id = p.emp_id
    WHERE b.emp_id = %s
    """, (emp_id,))
    return mc.fetchone()

def get_department_employees(department):
    mc.execute("""
    SELECT b.emp_id, b.emp_name, p.department, b.date_of_joining, b.city, b.phone_no, b.email_id, 
           p.organisational_level, p.address, p.designation
    FROM employee_basic_info b
    JOIN employee_professional_info p ON b.emp_id = p.emp_id
    WHERE p.department = %s
    """, (department,))
    return mc.fetchall()

def get_all_departments():
    mc.execute("SELECT DISTINCT department FROM employee_professional_info")
    return [row['department'] for row in mc.fetchall()]

def update_employee_field(emp_id, field, value, table):
    try:
        query = f"UPDATE {table} SET {field} = %s WHERE emp_id = %s"
        mc.execute(query, (value, emp_id))
        mydb.commit()
    except mys.Error as e:
        st.error(f"An error occurred while updating {field}: {e}")