import streamlit as st
import pandas as pd  # Import pandas for table formatting

# Initialize a session state variable to track the number of input groups
if "input_groups" not in st.session_state:
    st.session_state.input_groups = []  # Each group will be a dictionary { "problem": "", "cause": "", "interim_action": "" }
if "add_new_group" not in st.session_state:
    st.session_state.add_new_group = False  # Track if a new group was added during the last interaction

# Function to handle adding a new group of inputs
def add_input_group():
    st.session_state.input_groups.append({"problem": "", "cause": "", "interim_action": ""})
    # st.session_state.add_new_group = True  # Mark that a new group has been added

# Button to add new input groups
if st.button("Add Detail"):
    add_input_group()

# Render all input groups dynamically
for i, group in enumerate(st.session_state.input_groups):
    if not (st.session_state.add_new_group and i == len(st.session_state.input_groups) - 1):
        # Only render the last added group on the next rerun
        st.session_state.input_groups[i]["problem"] = st.text_input(
            f"Problem", value=group["problem"], key=f"problem_{i}"
        )
        st.session_state.input_groups[i]["cause"] = st.text_input(
            f"Cause", value=group["cause"], key=f"cause_{i}"
        )
        st.session_state.input_groups[i]["interim_action"] = st.text_input(
            f"Interim Action", value=group["interim_action"], key=f"interim_action_{i}"
        )
        st.divider()

# Reset the add_new_group flag after rendering
st.session_state.add_new_group = False

# Display the data in a table format
if st.button("Save"):
    st.write("### Current Details in Table Format:")
    if st.session_state.input_groups:
        # Convert input groups into a DataFrame
        df = pd.DataFrame(st.session_state.input_groups)
        st.table(df)  # Use st.table() for static table or st.dataframe() for interactive
    else:
        st.write("No details added yet.")
