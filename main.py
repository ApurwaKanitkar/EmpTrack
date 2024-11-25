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

# Set the page configuration
st.set_page_config(page_title="EmpTrack", layout="wide")

# Initialize session state
if 'loggedIn' not in st.session_state:
    st.session_state['loggedIn'] = False
    st.session_state['department'] = None
    st.session_state['hr_page'] = "My Details"
    st.session_state['emp_id'] = None

def login(emp_id, password):
    # Check if employee ID exists
    mc.execute("SELECT * FROM emp_info WHERE Emp_id = %s", (emp_id,))
    result = mc.fetchone()
    
    if result:
        # If employee ID exists, check the password
        if result['Password'] == password:
            return True, result['Department'], None
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

def get_employee_details(emp_id):
    mc.execute("SELECT * FROM emp_info WHERE Emp_id = %s", (emp_id,))
    return mc.fetchone()

def get_department_employees(department):
    mc.execute("SELECT Emp_id, Emp_name, Department, Date_of_joining, City, Phone_no, Email_id, Organisational_Level, Address, Designation FROM emp_info WHERE Department = %s", (department,))
    return mc.fetchall()

def get_all_departments():
    mc.execute("SELECT DISTINCT Department FROM emp_info")
    return [row['Department'] for row in mc.fetchall()]

def update_employee_field(emp_id, field, value):
    try:
        query = f"UPDATE emp_info SET {field} = %s WHERE Emp_id = %s"
        mc.execute(query, (value, emp_id))
        mydb.commit()
    except mys.Error as e:
        st.error(f"An error occurred while updating {field}: {e}")

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
        background-color: #0068c9;
        color: white;
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
            mc.execute("SELECT * FROM emp_salary WHERE Organisational_Level = %s", (emp_details['Organisational_Level'],))
            salary_details = mc.fetchone()

            # Create two columns for Personal Details and Salary Details
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Personal Details")
                st.write(f"Employee ID: {emp_details['Emp_id']}")
                st.write(f"Name: {emp_details['Emp_name']}")
                st.write(f"Department: {emp_details['Department']}")
                st.write(f"Date of Joining: {emp_details['Date_of_joining']}")
                st.write(f"City: {emp_details['City']}")
                st.write(f"Phone Number: {emp_details['Phone_no']}")
                st.write(f"Email ID: {emp_details['Email_id']}")
                st.write(f"Organizational Level: {emp_details['Organisational_Level']}")
                st.write(f"Address: {emp_details['Address']}")
                st.write(f"Designation: {emp_details['Designation']}")

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
                new_city = st.text_input("New City", emp_details['City'])
                if st.button("Update City"):
                    if new_city:
                        update_employee_field(emp_details['Emp_id'], 'City', new_city)
                        st.success("City Updated Successfully")
                    else:
                        st.error("City cannot be empty.")

            elif update_option == "Phone Number":
                new_phone = st.text_input("New Phone Number", emp_details['Phone_no'])
                if st.button("Update Phone Number"):
                    if new_phone.isdigit() and len(new_phone) == 10:
                        update_employee_field(emp_details['Emp_id'], 'Phone_no', new_phone)
                        st.success("Phone Number Updated Successfully")
                    else:
                        st.error("Invalid Phone Number. It should be a 10-digit number.")

            elif update_option == "Email ID":
                new_email = st.text_input("New Email ID", emp_details['Email_id'])
                if st.button("Update Email ID"):
                    if new_email.lower().endswith(('@yahoo.com', '@outlook.com', '@hotmail.com', '@icloud.com', '@gmail.com')):
                        update_employee_field(emp_details['Emp_id'], 'Email_id', new_email)
                        st.success("Email ID Updated Successfully")
                    else:
                        st.error("Invalid Email ID!")

            elif update_option == "Address":
                new_address = st.text_area("New Address", emp_details['Address'])
                if st.button("Update Address"):
                    if new_address:
                        update_employee_field(emp_details['Emp_id'], 'Address', new_address)
                        st.success("Address Updated Successfully")
                    else:
                        st.error("Address cannot be empty.")

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
                    'Emp_id': 'Employee ID',
                    'Emp_name': 'Employee Name',
                    'Department': 'Department',
                    'Date_of_joining': 'Date of Joining',
                    'City': 'City',
                    'Phone_no': 'Phone Number',
                    'Email_id': 'Email ID',
                    'Organisational_Level': 'Organizational Level',
                    'Address': 'Address',
                    'Designation': 'Designation'
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
            mc.execute("SELECT * FROM emp_info WHERE Emp_id = %s", (emp_id,))
            emp_details = mc.fetchone()

            if emp_details:
                st.success(f"Updating details for employee: {emp_details['Emp_name']} (ID: {emp_id})")

                # Create a form for updates
                with st.form(key='update_form'):
                    # Display current values and allow updates
                    new_name = st.text_input("Name", emp_details['Emp_name'])
                    new_department = st.selectbox("Department", ['HR', 'Tech', 'Sales', 'Customer Success'], index=['HR', 'Tech', 'Sales', 'Customer Success'].index(emp_details['Department']))
                    new_doj = st.date_input("Date of Joining", emp_details['Date_of_joining'])
                    new_city = st.text_input("City", emp_details['City'])
                    new_phone = st.text_input("Phone Number", emp_details['Phone_no'])
                    new_email = st.text_input("Email ID", emp_details['Email_id'])
                    new_org_level = st.selectbox("Organizational Level", ['L1', 'L2', 'L3', 'L4', 'L5'], index=['L1', 'L2', 'L3', 'L4', 'L5'].index(emp_details['Organisational_Level']))
                    new_address = st.text_input("Address", emp_details['Address'])
                    new_designation = st.text_input("Designation", emp_details['Designation'])

                    # Submit button
                    submitted = st.form_submit_button("Update Employee Details")

                if submitted:
                    # Prepare update query
                    update_query = """
                    UPDATE emp_info
                    SET Emp_name = %s, Department = %s, Date_of_joining = %s, City = %s,
                        Phone_no = %s, Email_id = %s, Organisational_Level = %s, Address = %s, Designation = %s
                    WHERE Emp_id = %s
                    """
                    update_values = (new_name, new_department, new_doj, new_city, new_phone, new_email, 
                                     new_org_level, new_address, new_designation, emp_id)

                    try:
                        mc.execute(update_query, update_values)
                        mydb.commit()
                        st.success("Employee details updated successfully!")
                    except mys.Error as e:
                        st.error(f"An error occurred while updating employee details: {e}")
            else:
                st.error(f"Employee with ID {emp_id} does not exist.")

    elif st.session_state['hr_page'] == "Delete Employee":
        st.header("Delete Employee")

        emp_id = st.text_input("Enter Employee ID to delete")
        
        if emp_id:
            # Check if employee exists
            mc.execute("SELECT Emp_name FROM emp_info WHERE Emp_id = %s", (emp_id,))
            result = mc.fetchone()
            
            if result:
                st.warning(f"You are about to delete the employee: {result['Emp_name']} (ID: {emp_id})")
                st.error("This is a permanent action and cannot be reversed!")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes, delete", key="delete_button"):
                        try:
                            mc.execute("DELETE FROM emp_info WHERE Emp_id = %s", (emp_id,))
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
        mc.execute("SELECT DISTINCT Department FROM emp_info")
        departments = [row['Department'] for row in mc.fetchall()]
        mc.execute("SELECT DISTINCT City FROM emp_info")
        cities = [row['City'] for row in mc.fetchall()]
        mc.execute("SELECT DISTINCT Organisational_Level FROM emp_info")
        org_levels = [row['Organisational_Level'] for row in mc.fetchall()]

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
                        query = """
                        INSERT INTO emp_info (Emp_id, Emp_name, Department, Date_of_joining, City, Phone_no, Email_id, Organisational_Level, Address, Designation, Password)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        values = (emp_id, emp_name, department, date_of_joining.strftime('%Y-%m-%d'), city, phone_no, email_id, org_level, address, designation, password)
                        mc.execute(query, values)
                        mydb.commit()
                        st.success("New employee added successfully!")
                    except mys.Error as e:
                        st.error(f"Error adding new employee: {e}")

def get_employee_details(emp_id):
    mc.execute("SELECT * FROM emp_info WHERE Emp_id = %s", (emp_id,))
    return mc.fetchone()

def show_my_details(emp_id):
    st.header("My Details")
    emp_details = get_employee_details(emp_id)
    if emp_details:
        # Get salary details
        mc.execute("SELECT * FROM emp_salary WHERE Organisational_Level = %s", (emp_details['Organisational_Level'],))
        salary_details = mc.fetchone()

        # Create two columns for Personal Details and Salary Details
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Personal Details")
            st.write(f"Employee ID: {emp_details['Emp_id']}")
            st.write(f"Name: {emp_details['Emp_name']}")
            st.write(f"Department: {emp_details['Department']}")
            st.write(f"Date of Joining: {emp_details['Date_of_joining']}")
            st.write(f"City: {emp_details['City']}")
            st.write(f"Phone Number: {emp_details['Phone_no']}")
            st.write(f"Email ID: {emp_details['Email_id']}")
            st.write(f"Organizational Level: {emp_details['Organisational_Level']}")
            st.write(f"Address: {emp_details['Address']}")
            st.write(f"Designation: {emp_details['Designation']}")

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
            new_city = st.text_input("New City", emp_details['City'])
            if st.button("Update City"):
                if new_city:
                    update_employee_field(emp_details['Emp_id'], 'City', new_city)
                    st.success("City Updated Successfully")
                else:
                    st.error("City cannot be empty.")

        elif update_option == "Phone Number":
            new_phone = st.text_input("New Phone Number", emp_details['Phone_no'])
            if st.button("Update Phone Number"):
                if new_phone.isdigit() and len(new_phone) == 10:
                    update_employee_field(emp_details['Emp_id'], 'Phone_no', new_phone)
                    st.success("Phone Number Updated Successfully")
                else:
                    st.error("Invalid Phone Number. It should be a 10-digit number.")

        elif update_option == "Email ID":
            new_email = st.text_input("New Email ID", emp_details['Email_id'])
            if st.button("Update Email ID"):
                if new_email.lower().endswith(('@yahoo.com', '@outlook.com', '@hotmail.com', '@icloud.com', '@gmail.com')):
                    update_employee_field(emp_details['Emp_id'], 'Email_id', new_email)
                    st.success("Email ID Updated Successfully")
                else:
                    st.error("Invalid Email ID!")

        elif update_option == "Address":
            new_address = st.text_area("New Address", emp_details['Address'])
            if st.button("Update Address"):
                if new_address:
                    update_employee_field(emp_details['Emp_id'], 'Address', new_address)
                    st.success("Address Updated Successfully")
                else:
                    st.error("Address cannot be empty.")

    else:
        st.error("Unable to fetch employee details.")

def tech_dashboard():
    st.title("Tech Dashboard")
    show_my_details(st.session_state['emp_id'])

def sales_dashboard():
    st.title("Sales Dashboard")
    show_my_details(st.session_state['emp_id'])

def cs_dashboard():
    st.title("Customer Success Dashboard")
    show_my_details(st.session_state['emp_id'])

def main():
    if st.session_state['loggedIn']:
        show_logout_button()
        department = st.session_state['department']
        if department == 'HR':
            hr_dashboard()
        elif department == 'Tech':
            tech_dashboard()
        elif department == 'Sales':
            sales_dashboard()
        elif department == 'Customer Success':
            cs_dashboard()
    else:
        show_login_page()

if __name__ == "__main__":
    main()