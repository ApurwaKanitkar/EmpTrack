import streamlit as st
import mysql.connector as mys
import pandas as pd
from hr import *
from other_dept import *
from my_details import *
from login_logout import *

# Connect to the database
mydb = mys.connect(
    host="localhost", 
    user="root", 
    password="L3arn@11t",
    database="Emp_DBMS"
)
mc = mydb.cursor(dictionary=True)

# Set the page configuration
st.set_page_config(page_title="EmpTrack", layout="wide")

# Initialize session state
if 'loggedIn' not in st.session_state:
    st.session_state['loggedIn'] = False
    st.session_state['department'] = None
    st.session_state['hr_page'] = "My Details"
    st.session_state['emp_id'] = None

def main():
    if st.session_state['loggedIn']:
        show_logout_button()
        emp_details = get_employee_details(st.session_state['emp_id'])
        if emp_details:
            department = emp_details['department']
            st.session_state['department'] = department
            if department == 'HR':
                hr_dashboard()
            elif department in ['Tech', 'Sales', 'Customer Success']:
                st.title(f"{department} Dashboard")
                show_my_details(st.session_state['emp_id'])
            else:
                st.error("Invalid department")
        else:
            st.error("Unable to fetch employee details")
    else:
        show_login_page()

if __name__ == "__main__":
    main()