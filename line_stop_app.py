import streamlit as st
import pyodbc
import pandas as pd

# Streamlit app title
st.title("L-Tractor Line Stop Management")

# Database connection details
server = 'DESKTOP-JTU1UI9\\TEW_SQLEXPRESS'  # Replace with your server name
database = 'LineStop'                       # Replace with your database name
username = ''                               # Leave empty for Windows Authentication
password = ''                               # Leave empty for Windows Authentication

# Connection string
conn_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

# Initialize session state variables
if "input_groups" not in st.session_state:
    st.session_state.input_groups = {}  # Each group will be a dictionary { "problem": "", "cause": "", "interim_action": "" }
if "search_clicked" not in st.session_state:
    st.session_state.search_clicked = False  # Track whether the search button was clicked
if "filtered_data" not in st.session_state:
    st.session_state.filtered_data = pd.DataFrame()  # To store fetched data
if "add_new_group" not in st.session_state:
    st.session_state.add_new_group = False  # Track if a new group was added during the last interaction

# Function to handle adding a new group of inputs
def add_input_group():
    st.session_state.input_groups.append({"problem": "", "cause": "", "interim_action": ""})
    # st.session_state.add_new_group = True  # Mark that a new group has been added

# Function to fetch distinct LineCodes for dropdown
def get_line_codes():
    try:
        conn = pyodbc.connect(conn_string)
        query = "SELECT DISTINCT LineCode FROM LineStop"
        line_codes = pd.read_sql(query, conn)
        conn.close()
        return line_codes['LineCode'].tolist()
    except Exception as e:
        st.error(f"Error fetching LineCodes: {e}")
        return []

# Function to fetch filtered data
def fetch_data(line_code=None, start_date=None, end_date=None):
    try:
        conn = pyodbc.connect(conn_string)

        # Base SQL query
        query = "SELECT ID, WorkingDate, LineCode, TimeStart, TimeEnd, LS_Type, LS_Time FROM LineStop WHERE 1=1"
        params = []

        # Add filters to the query
        if line_code and line_code != "All":
            query += " AND LineCode = ?"
            params.append(line_code)
        if start_date and end_date:
            query += " AND WorkingDate BETWEEN ? AND ?"
            params.append(start_date)
            params.append(end_date)

        # Execute the query
        df = pd.read_sql(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return pd.DataFrame()

# Create columns for filters
col1, col2 = st.columns([1, 1])

# LineCode dropdown filter (left column)
with col1:
    line_codes = get_line_codes()
    line_code_filter = st.selectbox("Line :", ["All"] + line_codes, index=0)

# WorkingDate date range picker (right column)
with col2:
    date_range = st.date_input("Date range :", [])
    if len(date_range) == 2:
        start_date_filter = date_range[0].strftime('%Y-%m-%d')
        end_date_filter = date_range[1].strftime('%Y-%m-%d')
    else:
        start_date_filter = None
        end_date_filter = None

# Search button
if st.button("Search"):
    st.session_state.search_clicked = True
    st.session_state.filtered_data = fetch_data(line_code=line_code_filter, start_date=start_date_filter, end_date=end_date_filter)

# Display filtered data if search was clicked
if st.session_state.search_clicked and not st.session_state.filtered_data.empty:
    filtered_data = st.session_state.filtered_data.reset_index(drop=True)
    st.write("### List of Line Stop Problems")
    st.dataframe(filtered_data, use_container_width=True)

    for index, row in filtered_data.iterrows():
        st.write(f"**ID**: {index+1} | **Date**: {row['WorkingDate']} | **Time**: {row['TimeStart']}-{row['TimeEnd']} | **Type**: {row['LS_Type']} | **Line stop**: {row['LS_Time']}")

        # Add a divider between rows
        st.divider()

    # Render input groups for additional details
    for i, group in enumerate(st.session_state.input_groups):
        if not (st.session_state.add_new_group and i == len(st.session_state.input_groups) - 1):
            st.session_state.input_groups[i]["problem"] = st.text_input(
                f"Problem {i + 1}", value=group["problem"], key=f"problem_{i}"
            )
            st.session_state.input_groups[i]["cause"] = st.text_input(
                f"Cause {i + 1}", value=group["cause"], key=f"cause_{i}"
            )
            st.session_state.input_groups[i]["interim_action"] = st.text_input(
                f"Interim Action {i + 1}", value=group["interim_action"], key=f"interim_action_{i}"
            )
            st.divider()

    # Reset the add_new_group flag after rendering
    st.session_state.add_new_group = False

    # Button to add new input groups
    if st.button("Add Detail", key="add_detail"):
        add_input_group()

    # Save button
    if st.button("Save"):
        st.write("### Current Details in Table Format:")
        if st.session_state.input_groups:
            df = pd.DataFrame(st.session_state.input_groups)
            st.table(df)
        else:
            st.write("No details added yet.")



# import streamlit as st
# import pyodbc
# import pandas as pd

# # Streamlit app title
# st.title("L-Tractor Line Stop Management")

# # Database connection details
# server = 'DESKTOP-JTU1UI9\\TEW_SQLEXPRESS'  # Replace with your server name
# database = 'LineStop'                       # Replace with your database name
# username = ''                               # Leave empty for Windows Authentication
# password = ''                               # Leave empty for Windows Authentication

# # Connection string
# conn_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

# # Initialize a session state variable to track the number of input groups
# if "input_groups" not in st.session_state:
#     st.session_state.input_groups = []  # Each group will be a dictionary { "problem": "", "cause": "", "interim_action": "" }
# if "add_new_group" not in st.session_state:
#     st.session_state.add_new_group = False  # Track if a new group was added during the last interaction
# if "search_clicked" not in st.session_state:
#     st.session_state.search_clicked = False  # Track whether the search button was clicked
# if "filtered_data" not in st.session_state:
#     st.session_state.filtered_data = pd.DataFrame()  # To store fetched data

# # Function to handle adding a new group of inputs
# def add_input_group():
#     st.session_state.input_groups.append({"problem": "", "cause": "", "interim_action": ""})

# # Function to fetch distinct LineCodes for dropdown
# def get_line_codes():
#     try:
#         conn = pyodbc.connect(conn_string)
#         query = "SELECT DISTINCT LineCode FROM LineStop"
#         line_codes = pd.read_sql(query, conn)
#         conn.close()
#         return line_codes['LineCode'].tolist()
#     except Exception as e:
#         st.error(f"Error fetching LineCodes: {e}")
#         return []

# # Function to fetch filtered data
# def fetch_data(line_code=None, start_date=None, end_date=None):
#     try:
#         conn = pyodbc.connect(conn_string)

#         # Base SQL query
#         query = "SELECT ID, WorkingDate, LineCode, TimeStart, TimeEnd, LS_Type, LS_Time FROM LineStop WHERE 1=1"
#         params = []

#         # Add filters to the query
#         if line_code and line_code != "All":
#             query += " AND LineCode = ?"
#             params.append(line_code)
#         if start_date and end_date:
#             query += " AND WorkingDate BETWEEN ? AND ?"
#             params.append(start_date)
#             params.append(end_date)

#         # Execute the query
#         df = pd.read_sql(query, conn, params=params)
#         conn.close()
#         return df
#     except Exception as e:
#         st.error(f"Error connecting to database: {e}")
#         return pd.DataFrame()

# # Function to save additional information to the database
# # def save_additional_info(row_id, additional_info):
# #     try:
# #         conn = pyodbc.connect(conn_string)
# #         query = "UPDATE LineStop SET AdditionalInfo = ? WHERE ID = ?"
# #         params = (additional_info, row_id)
# #         conn.execute(query, params)
# #         conn.commit()
# #         conn.close()
# #         st.success("Additional information saved successfully!")
# #     except Exception as e:
# #         st.error(f"Error saving additional information: {e}")

# # Create columns for filters and position them above the table
# col1, col2 = st.columns([1, 1])

# # LineCode dropdown filter (left column)
# with col1:
#     # st.subheader("Filter by LineCode")
#     line_codes = get_line_codes()
#     line_code_filter = st.selectbox("Line :", ["All"] + line_codes, index= None, placeholder="Select Line Code...")

# # WorkingDate date range picker (right column)
# with col2:
#     # st.subheader("Filter by WorkingDate")
#     date_range = st.date_input("Date range :", [], help="Select date range...")
#     if len(date_range) == 2:
#         start_date_filter = date_range[0].strftime('%Y-%m-%d')
#         end_date_filter = date_range[1].strftime('%Y-%m-%d')
#     else:
#         start_date_filter = None
#         end_date_filter = None

# # Search button
# search_button = st.button("Search")

# # Check if the Search button was clicked and validate filter selection
# if search_button:
#     st.session_state.search_clicked = True
#     st.session_state.filtered_data = fetch_data(line_code=line_code_filter, start_date=start_date_filter, end_date=end_date_filter)

#     if (line_code_filter == "All" and not date_range) or (line_code_filter == "All" and not start_date_filter and not end_date_filter):
#         st.warning("Please select at least one criteria Line or Date range.")
#     else:
#         # Fetch and display filtered data
#         filtered_data = fetch_data(line_code=line_code_filter, start_date=start_date_filter, end_date=end_date_filter)

#         if not filtered_data.empty:
#             # Drop the first three columns (index and unnecessary columns)
#             filtered_data = filtered_data.reset_index(drop=True)
#             # Display the filtered DataFrame in Streamlit
#             st.write("### List of Line Stop Problems")
#             st.dataframe(filtered_data, use_container_width=True)  

#             # Display filtered data with a button for each row
#             for index, row in filtered_data.iterrows():
#                 st.write(f"**ID**: {index+1} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Date**: {row['WorkingDate']} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Time**: {row['TimeStart']}-{row['TimeEnd']} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Type**: {row['LS_Type']} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Line stop**: {row['LS_Time']}")

#                 # Render all input groups dynamically
#                 for i, group in enumerate(st.session_state.input_groups):
#                     st.session_state.input_groups[i]["problem"] = st.text_input(
#                         f"Problem", value=group["problem"], key=f"problem_{i}"
#                     )
#                     st.session_state.input_groups[i]["cause"] = st.text_input(
#                         f"Cause", value=group["cause"], key=f"cause_{i}"
#                     )
#                     st.session_state.input_groups[i]["interim_action"] = st.text_input(
#                         f"Interim Action", value=group["interim_action"], key=f"interim_action_{i}"
#                     )
#                     st.divider()

#                 # Button to add new input groups
#                 if st.button("Add Detail"):
#                     add_input_group()

#                 # Display the data in a table format
#                 if st.button("Save"):
#                     st.write("### Current Details in Table Format:")
#                     if st.session_state.input_groups:
#                         # Convert input groups into a DataFrame
#                         df = pd.DataFrame(st.session_state.input_groups)
#                         st.table(df)  # Use st.table() for static table or st.dataframe() for interactive
#                     else:
#                         st.write("No details added yet.")
#         else:
#             st.warning("No data found for the selected filters.")
