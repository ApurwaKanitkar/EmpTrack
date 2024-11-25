import streamlit as st
import mysql.connector as mys
import pandas as pd
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

def show_my_details(emp_id):
    st.header("My Details")
    emp_details = get_employee_details(emp_id)
    if emp_details:
        # Get salary details
        mc.execute("SELECT * FROM emp_salary WHERE organisational_level = %s", (emp_details['organisational_level'],))
        salary_details = mc.fetchone()

        # Create two columns for Personal Details and Salary Details
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Personal Details")
            st.write(f"Employee ID: {emp_details['emp_id']}")
            st.write(f"Name: {emp_details['emp_name']}")
            st.write(f"Department: {emp_details['department']}")
            st.write(f"Date of Joining: {emp_details['date_of_joining']}")
            st.write(f"City: {emp_details['city']}")
            st.write(f"Phone Number: {emp_details['phone_no']}")
            st.write(f"Email ID: {emp_details['email_id']}")
            st.write(f"Organizational Level: {emp_details['organisational_level']}")
            st.write(f"Address: {emp_details['address']}")
            st.write(f"Designation: {emp_details['designation']}")

        with col2:
            st.subheader("Salary Details")
            if salary_details:
                st.write(f"Current Fixed Salary: ₹{salary_details['Current_Fixed_Salary']:,.2f}")
                st.write(f"Current Variable Salary: ₹{salary_details['Current_Variable_Salary']:,.2f}")
                st.write(f"Total Salary: ₹{salary_details['Total_Salary']:,.2f}")
            else:
                st.error("Unable to fetch salary details.")

        # Add "Update My Details" section
        st.subheader("Update My Details")
        update_option = st.selectbox("Select field to update", ["City", "Phone Number", "Email ID", "Address", "Password"])
        
        if update_option == "City":
            new_city = st.text_input("New City", emp_details['city'])
            if st.button("Update City"):
                if new_city:
                    update_employee_field(emp_details['emp_id'], 'city', new_city, 'employee_basic_info')
                    st.success("City Updated Successfully")
                else:
                    st.error("City cannot be empty.")

        elif update_option == "Phone Number":
            new_phone = st.text_input("New Phone Number", emp_details['phone_no'])
            if st.button("Update Phone Number"):
                if new_phone.isdigit() and len(new_phone) == 10:
                    update_employee_field(emp_details['emp_id'], 'phone_no', new_phone, 'employee_basic_info')
                    st.success("Phone Number Updated Successfully")
                else:
                    st.error("Invalid Phone Number. It should be a 10-digit number.")

        elif update_option == "Email ID":
            new_email = st.text_input("New Email ID", emp_details['email_id'])
            if st.button("Update Email ID"):
                if new_email.lower().endswith(('@yahoo.com', '@outlook.com', '@hotmail.com', '@icloud.com', '@gmail.com')):
                    update_employee_field(emp_details['emp_id'], 'email_id', new_email, 'employee_basic_info')
                    st.success("Email ID Updated Successfully")
                else:
                    st.error("Invalid Email ID!")

        elif update_option == "Address":
            new_address = st.text_area("New Address", emp_details['address'])
            if st.button("Update Address"):
                if new_address:
                    update_employee_field(emp_details['emp_id'], 'address', new_address, 'employee_professional_info')
                    st.success("Address Updated Successfully")
                else:
                    st.error("Address cannot be empty.")
        
        elif update_option == "Password":
            new_password = st.text_area("Password", emp_details['password'])
            if st.button("Update Password"):
                if new_password:
                    update_employee_field(emp_details['emp_id'], 'password', new_password, 'employee_basic_info')
                else:
                    st.error("Password cannot be empty.")

    else:
        st.error("Unable to fetch employee details.")