import streamlit as st
import mysql.connector as mys
import pandas as pd
from login_logout import *
from my_details import *

# Connect to the database
mydb = mys.connect(
    host="localhost", 
    user="root", 
    password="L3arn@11t",
    database="Emp_DBMS"
)
mc = mydb.cursor(dictionary=True)

# Add these functions at the top of the file
@st.cache_data
def get_all_departments():
    mc.execute("SELECT DISTINCT department FROM employee_professional_info")
    return [row['department'] for row in mc.fetchall()]

@st.cache_data
def get_department_employees(department):
    query = """
    SELECT ebi.emp_id, ebi.emp_name, epi.department, ebi.date_of_joining, ebi.city, 
           ebi.phone_no, ebi.email_id, epi.organisational_level, epi.address, epi.designation
    FROM employee_basic_info ebi
    JOIN employee_professional_info epi ON ebi.emp_id = epi.emp_id
    WHERE epi.department = %s
    """
    mc.execute(query, (department,))
    return mc.fetchall()

def hr_dashboard():
    st.title("HR Dashboard")

    # Custom CSS for the menu
    st.markdown("""
    <style>
    .menu-item {
        padding: 10px;
        cursor: pointer;
        margin-bottom: 5px;
        border-radius: 5px;
    }
    .menu-item:hover {
        background-color: #e6e6e6;
    }
    .menu-item.active {
        background-color: #ff1f0f;
        color: white;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    # Sidebar navigation using custom HTML/CSS
    with st.sidebar:
        st.markdown("<h3>Menu</h3>", unsafe_allow_html=True)
        menu_items = ["My Details", "View Department Details", "Update Employee Details", "Delete Employee", "Add New Employee"]
        for item in menu_items:
            if st.session_state['hr_page'] == item:
                st.markdown(f'<div class="menu-item active">{item}</div>', unsafe_allow_html=True)
            else:
                if st.button(item, key=f"menu_{item}", use_container_width=True):
                    st.session_state['hr_page'] = item
                    st.rerun()

    # Main content area
    if st.session_state['hr_page'] == "My Details":
        st.header("My Details")
        emp_details = get_employee_details(st.session_state['emp_id'])
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
            update_option = st.selectbox("Select field to update", ["City", "Phone Number", "Email ID", "Address"])
            
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
                        update_employee_field(emp_details['emp_id'], 'phone_no', new_phone,'employee_basic_info')
                        st.success("Phone Number Updated Successfully")
                    else:
                        st.error("Invalid Phone Number. It should be a 10-digit number.")

            elif update_option == "Email ID":
                new_email = st.text_input("New Email ID", emp_details['email_id'])
                if st.button("Update Email ID"):
                    if new_email.lower().endswith(('@yahoo.com', '@outlook.com', '@hotmail.com', '@icloud.com', '@gmail.com')):
                        update_employee_field(emp_details['emp_id'], 'email_id', new_email,'employee_basic_info')
                        st.success("Email ID Updated Successfully")
                    else:
                        st.error("Invalid Email ID!")

            elif update_option == "Address":
                new_address = st.text_area("New Address", emp_details['address'])
                if st.button("Update Address"):
                    if new_address:
                        update_employee_field(emp_details['emp_id'], 'address', new_address,'employee_professional_info')
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

    elif st.session_state['hr_page'] == "View Department Details":
        st.header("View Department Details")
        departments = get_all_departments()
        selected_department = st.selectbox("Select Department", departments)
        
        if selected_department:
            employees = get_department_employees(selected_department)
            if employees:
                # Create a new DataFrame with renamed columns
                df = pd.DataFrame(employees)
                df = df.rename(columns={
                    'emp_id': 'Employee ID',
                    'emp_name': 'Employee Name',
                    'department': 'Department',
                    'date_of_joining': 'Date of Joining',
                    'city': 'City',
                    'phone_no': 'Phone Number',
                    'email_id': 'Email ID',
                    'organisational_level': 'Organizational Level',
                    'address': 'Address',
                    'designation': 'Designation'
                })
                
                # Add a new column for numbering, starting from 1
                df.insert(0, 'S.No.', range(1, len(df) + 1))
                
                # Reset the index to remove the default numeric index
                df = df.set_index('S.No.')
                
                # Display the DataFrame
                st.dataframe(df)
            else:
                st.write("No employees found in this department.")

    elif st.session_state['hr_page'] == "Update Employee Details":
        st.header("Update Employee Details")

        # Employee ID input
        emp_id = st.text_input("Enter Employee ID to update")

        if emp_id:
            # Check if employee exists
            mc.execute("SELECT * FROM employee_basic_info WHERE emp_id = %s", (emp_id,))
            basic_details = mc.fetchone()
            mc.execute("SELECT * FROM employee_professional_info WHERE emp_id = %s", (emp_id,))
            professional_details = mc.fetchone()

            if basic_details and professional_details:
                st.success(f"Updating details for employee: {basic_details['emp_name']} (ID: {emp_id})")

                # Create a form for updates
                with st.form(key='update_form'):
                    # Display current values and allow updates
                    new_name = st.text_input("Name", basic_details['emp_name'])
                    new_department = st.selectbox("Department", ['HR', 'Tech', 'Sales', 'Customer Success'], index=['HR', 'Tech', 'Sales', 'Customer Success'].index(professional_details['department']))
                    new_doj = st.date_input("Date of Joining", basic_details['date_of_joining'])
                    new_city = st.text_input("City", basic_details['city'])
                    new_phone = st.text_input("Phone Number", basic_details['phone_no'])
                    new_email = st.text_input("Email ID", basic_details['email_id'])
                    new_org_level = st.selectbox("Organizational Level", ['L1', 'L2', 'L3', 'L4', 'L5'], index=['L1', 'L2', 'L3', 'L4', 'L5'].index(professional_details['organisational_level']))
                    new_address = st.text_input("Address", professional_details['address'])
                    new_designation = st.text_input("Designation", professional_details['designation'])

                    # Submit button
                    submitted = st.form_submit_button("Update Employee Details")

                if submitted:
                    # Prepare update query
                    update_basic_query = """
                    UPDATE employee_basic_info
                    SET emp_name = %s, date_of_joining = %s, city = %s, phone_no = %s, email_id = %s
                    WHERE emp_id = %s
                    """
                    update_basic_values = (new_name, new_doj, new_city, new_phone, new_email, emp_id)

                    update_professional_query = """
                    UPDATE employee_professional_info
                    SET department = %s, organisational_level = %s, address = %s, designation = %s
                    WHERE emp_id = %s
                    """

                    update_professional_values = (new_department, new_org_level, new_address, new_designation, emp_id)

                    try:
                        mc.execute(update_basic_query, update_basic_values)
                        mc.execute(update_professional_query, update_professional_values)
                        mydb.commit()
                        st.success("Employee details updated successfully!")
                        
                        # Clear the cache to ensure fresh data is loaded
                        st.cache_data.clear()
                        
                        # Refresh the page to show updated data
                        st.rerun()
                    except mys.Error as e:
                        st.error(f"An error occurred while updating employee details: {e}")
            else:
                st.error(f"Employee with ID {emp_id} does not exist.")

    elif st.session_state['hr_page'] == "Delete Employee":
        st.header("Delete Employee")

        emp_id = st.text_input("Enter Employee ID to delete")
        
        if emp_id:
            # Check if employee exists
            mc.execute("SELECT emp_name FROM employee_basic_info WHERE emp_id = %s", (emp_id,))
            result = mc.fetchone()
            
            if result:
                st.warning(f"You are about to delete the employee: {result['emp_name']} (ID: {emp_id})")
                st.error("This is a permanent action and cannot be reversed!")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes, delete", key="delete_button"):
                        try:
                            mc.execute("DELETE FROM employee_professional_info WHERE emp_id = %s", (emp_id,))
                            mc.execute("DELETE FROM employee_basic_info WHERE emp_id = %s", (emp_id,))
                            mydb.commit()
                            st.success(f"Employee {emp_id} has been successfully deleted.")
                            # Clear the input field after successful deletion
                            st.session_state['delete_emp_id'] = ''
                        except mys.Error as e:
                            st.error(f"An error occurred while deleting the employee: {e}")
                
                with col2:
                    if st.button("Cancel", key="cancel_button"):
                        st.info("Deletion cancelled.")
                        # Clear the input field after cancellation
                        st.session_state['delete_emp_id'] = ''
            else:
                st.error(f"Employee with ID {emp_id} does not exist.")

    elif st.session_state['hr_page'] == "Add New Employee":
        st.header("Add New Employee")
        
        # Get existing departments, cities, and organizational levels
        mc.execute("SELECT DISTINCT department FROM employee_professional_info")
        departments = [row['department'] for row in mc.fetchall()]
        mc.execute("SELECT DISTINCT city FROM employee_basic_info")
        cities = [row['city'] for row in mc.fetchall()]
        mc.execute("SELECT DISTINCT organisational_level FROM employee_professional_info")
        org_levels = [row['organisational_level'] for row in mc.fetchall()]

        with st.form("add_employee_form"):
            # Employee ID
            emp_id = st.text_input("Employee ID (4 digits)")
            
            # Name
            emp_name = st.text_input("Employee Name")
            
            # Department
            dept_options = [''] + departments + ['Other']
            department = st.selectbox("Department", dept_options)
            if department == 'Other':
                department = st.text_input("Specify Department")
            
            # Date of Joining
            date_of_joining = st.date_input("Date of Joining")
            
            # City
            city_options = [''] + cities + ['Other']
            city = st.selectbox("City", city_options)
            if city == 'Other':
                city = st.text_input("Specify City")
            
            # Phone Number
            phone_no = st.text_input("Phone Number (10 digits)")
            
            # Email ID
            email_id = st.text_input("Email ID")
            
            # Organizational Level
            org_level_options = [''] + org_levels + ['Other']
            org_level = st.selectbox("Organizational Level", org_level_options)
            if org_level == 'Other':
                org_level = st.text_input("Specify Organizational Level")
            
            # Address
            address = st.text_area("Address")
            
            # Designation
            designation = st.text_input("Designation")
            
            # Password
            password = st.text_input("Password", type="password")
            
            submitted = st.form_submit_button("Add Employee")
            
            if submitted:
                # Validate inputs
                if not (emp_id.isdigit() and len(emp_id) == 4):
                    st.error("Invalid Employee ID. It should be a 4-digit number.")
                elif not emp_name:
                    st.error("Employee Name is required.")
                elif not department:
                    st.error("Department is required.")
                elif not phone_no.isdigit() or len(phone_no) != 10:
                    st.error("Invalid Phone Number. It should be a 10-digit number.")
                elif not email_id or not email_id.lower().endswith(('@yahoo.com', '@outlook.com', '@hotmail.com', '@icloud.com', '@gmail.com')):
                    st.error("Invalid Email ID!")
                elif not address:
                    st.error("Address is required.")
                elif not designation:
                    st.error("Designation is required.")
                elif not password:
                    st.error("Password is required.")
                elif not city:
                    st.error("City is required.")
                elif not org_level:
                    st.error("Organizational Level is required.")
                else:
                    # All validations passed, insert new employee
                    try:
                        # Insert into employee_basic_info
                        basic_query = """
                        INSERT INTO employee_basic_info (emp_id, emp_name, date_of_joining, city, phone_no, email_id, password)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """
                        basic_values = (emp_id, emp_name, date_of_joining.strftime('%Y-%m-%d'), city, phone_no, email_id, password)
                        mc.execute(basic_query, basic_values)

                        # Insert into employee_professional_info
                        professional_query = """
                        INSERT INTO employee_professional_info (emp_id, department, organisational_level, address, designation)
                        VALUES (%s, %s, %s, %s, %s)
                        """
                        professional_values = (emp_id, department, org_level, address, designation)
                        mc.execute(professional_query, professional_values)

                        mydb.commit()
                        st.success("New employee added successfully!")
                    except mys.Error as e:
                        st.error(f"Error adding new employee: {e}")