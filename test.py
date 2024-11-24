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
    st.session_state.input_groups = []  # Each group will be a dictionary { "problem": "", "cause": "", "interim_action": "" }
if "search_clicked" not in st.session_state:
    st.session_state.search_clicked = False  # Track whether the search button was clicked
if "filtered_data" not in st.session_state:
    st.session_state.filtered_data = pd.DataFrame()  # To store fetched data
if "search_clicked" not in st.session_state:
    st.session_state.search_clicked = False  # Track whether the search button was clicked
if "add_new_group" not in st.session_state:
    st.session_state.add_new_group = False  # Track if a new group was added during the last interaction


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

        # Add ORDER BY clause
        query += " ORDER BY WorkingDate"

        # Execute the query
        df = pd.read_sql(query, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        return pd.DataFrame()

# # Function to handle adding a new group of inputs
# def add_input_group():
#     st.session_state.input_groups.append({"problem": "", "cause": "", "interim_action": ""})
#     # st.session_state.add_new_group = True  # Mark that a new group has been added

def add_input_group(problem_id):
    if problem_id not in st.session_state.input_groups:
        st.session_state.input_groups[problem_id] = {"problem": "", "cause": "", "interim_action": ""}

# Create columns for filters
col1, col2 = st.columns([1, 1])

# LineCode dropdown filter (left column)
with col1:
    line_codes = get_line_codes()
    line_code_filter = st.selectbox("Line :", ["All"] + line_codes, index=None, placeholder="Please Select Line Code...")

# WorkingDate date range picker (right column)
with col2:
    date_range = st.date_input("Date range :", [],help="Please Select Date Range")
    if len(date_range) == 2:
        start_date_filter = date_range[0].strftime('%Y-%m-%d')
        end_date_filter = date_range[1].strftime('%Y-%m-%d')
    else:
        start_date_filter = None
        end_date_filter = None

# Search and Clear buttons
search_col, clear_col = st.columns([1, 1])

with search_col:
    if st.button("Search"):
        # Check if at least one filter is selected
        if (line_code_filter == "All" or not line_code_filter) and not (start_date_filter and end_date_filter):
            st.error("Please select at least one filter: Line or Date Range.")
        else:
            st.session_state.search_clicked = True
            st.session_state.filtered_data = fetch_data(line_code=line_code_filter, start_date=start_date_filter, end_date=end_date_filter)

with clear_col:
    if st.button("Clear"):
        # Reset all filters and clear data
        st.session_state.search_clicked = False
        st.session_state.filtered_data = pd.DataFrame()
        line_code_filter = "All"
        date_range = []

# Display filtered data if search was clicked
if st.session_state.search_clicked and not st.session_state.filtered_data.empty:
    filtered_data = st.session_state.filtered_data.reset_index(drop=True)
    st.write("### List of Line Stop Problems")
    st.dataframe(filtered_data, use_container_width=True)

    for index, row in filtered_data.iterrows():
        # Assign a unique problem_id for each row, using the "ID" column from the database
        problem_id = row["ID"]  # Ensure your dataframe has a column named "ID"
        st.write(f"**ID**: {index+1} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Date**: {row['WorkingDate']} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Time**: {row['TimeStart']}-{row['TimeEnd']} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Type**: {row['LS_Type']} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Line stop**: {row['LS_Time']}")
        
        # # Button to add new input groups
        # if st.button(f"Add Detail **ID**: {index+1}"):
        #     add_input_group()
        # Button to add details for the specific problem ID
        if st.button(f"Add Detail **ID**: {index+1}", key=f"add_detail_{problem_id}"):
            add_input_group(problem_id)
        
        # # Render all input groups dynamically
        # for i, group in enumerate(st.session_state.input_groups):
        #     if not (st.session_state.add_new_group and i == len(st.session_state.input_groups) - 1):
        #         # Only render the last added group on the next rerun
        #         st.session_state.input_groups[i]["problem"] = st.text_input(
        #             f"Problem-{index+1}", value=group["problem"], key=f"problem_{index}_{i}"
        #         )
        #         st.session_state.input_groups[i]["cause"] = st.text_input(
        #             f"Cause-{index+1}", value=group["cause"], key=f"cause_{index}_{i}"
        #         )
        #         st.session_state.input_groups[i]["interim_action"] = st.text_input(
        #             f"Interim Action-{index+1}", value=group["interim_action"], key=f"interim_action_{index}_{i}"
        #         )
        #         st.divider()
        # Render the input group only if it exists for this problem ID
        if problem_id in st.session_state.input_groups:
            group = st.session_state.input_groups[problem_id]
            st.session_state.input_groups[problem_id]["problem"] = st.text_input(
                f"Problem-{index+1}", value=group["problem"], key=f"problem_{problem_id}"
            )
            st.session_state.input_groups[problem_id]["cause"] = st.text_input(
                f"Cause-{index+1}", value=group["cause"], key=f"cause_{problem_id}"
            )
            st.session_state.input_groups[problem_id]["interim_action"] = st.text_input(
                f"Interim Action-{index+1}", value=group["interim_action"], key=f"interim_action_{problem_id}"
            )
            st.divider()

        # Reset the add_new_group flag after rendering
        st.session_state.add_new_group = False
