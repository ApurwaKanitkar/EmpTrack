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

def login(emp_id, password):
    # Check if employee ID exists
    mc.execute("SELECT e.*, p.department FROM employee_basic_info e JOIN employee_professional_info p ON e.emp_id = p.emp_id WHERE e.emp_id = %s", (emp_id,))
    result = mc.fetchone()
    
    if result:
        # If employee ID exists, check the password
        if result['password'] == password:
            return True, result['department'], None
        else:
            return False, None, "Incorrect password!"
    else:
        return False, None, "Incorrect Employee ID! Employee does not exist!"

def LoggedIn_Clicked(emp_id, password):
    success, department, error_message = login(emp_id, password)
    if success:
        st.session_state['loggedIn'] = True
        st.session_state['department'] = department
        st.session_state['emp_id'] = emp_id
        st.rerun()
    else:
        st.session_state['loggedIn'] = False
        st.error(error_message)

def LoggedOut_Clicked():
    st.session_state['loggedIn'] = False
    st.session_state['department'] = None

def show_login_page():

    # Display the main title and subtitle

    st.markdown("<h1 style='text-align: center;'>Welcome to EmpTrack!</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;'>Employee Database Management System</h4>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login_form"):
            st.title("Employee Login")
            emp_id = st.text_input("Enter your Employee ID")
            password = st.text_input("Enter your Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                LoggedIn_Clicked(emp_id, password)

def show_logout_button():
    st.button("Log Out", on_click=LoggedOut_Clicked)