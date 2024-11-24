import streamlit as st
import pyodbc
import pandas as pd

# Streamlit app title
st.title("L-Tractor Line Stop Management")

# Database connection details
server_IT = 'DESKTOP-JTU1UI9\\TEW_SQLEXPRESS'  # Replace with your server name -> server
database_IT = 'LineStop'                       # Replace with your database name -> database
username_IT = ''                               # Leave empty for Windows Authentication -> username
password_IT = ''                               # Leave empty for Windows Authentication -> password

# Connection string
conn_string_IT = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server_IT};DATABASE={database_IT};Trusted_Connection=yes;' # conn_string

# Initialize session state variables
if "input_groups" not in st.session_state:
    st.session_state.input_groups = []  # Each group will be a dictionary { "problem": "", "cause": "", "interim_action": "" }
if "search_clicked" not in st.session_state:
    st.session_state.search_clicked = False  # Track whether the search button was clicked
if "filtered_data" not in st.session_state:
    st.session_state.filtered_data = pd.DataFrame()  # To store fetched data
if "search_clicked" not in st.session_state:
    st.session_state.search_clicked = False  # Track whether the search button was clicked

# Function to fetch distinct LineCodes for dropdown
def get_line_codes():
    try:
        conn = pyodbc.connect(conn_string_IT)
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
        conn = pyodbc.connect(conn_string_IT)

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
        st.write(f"**ID**: {index+1} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Date**: {row['WorkingDate']} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Time**: {row['TimeStart']}-{row['TimeEnd']} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Type**: {row['LS_Type']} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Line stop**: {row['LS_Time']}")
