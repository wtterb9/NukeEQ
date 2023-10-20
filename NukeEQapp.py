import streamlit as st
import pandas as pd
from EQparser import parse_item_data

st.title('Nukefire EQ Database by Biscuit')

# Load data from Excel with caching and session state
@st.cache_data(ttl=60*5)
def load_data():
    try:
        df = pd.read_excel('data.xlsx', engine='openpyxl')
    except FileNotFoundError:
        df = pd.DataFrame()
        df.to_excel('data.xlsx', engine='openpyxl')  # Save the empty DataFrame to data.xlsx
    return df

if 'df' not in st.session_state:
    st.session_state.df = load_data()
df = st.session_state.df

# Display data
if st.button('Show All Data'):
    st.write(df)

# Paste item data for parsing
if 'pasted_data' not in st.session_state:
    st.session_state.pasted_data = ''
pasted_data = st.text_area("Paste the item data here:", value=st.session_state.pasted_data)

# Add text input fields for Zone, MOB, and Directions
if 'zone' not in st.session_state:
    st.session_state.zone = ''
zone = st.text_input("Zone:", value=st.session_state.zone)

if 'directions' not in st.session_state:
    st.session_state.directions = ''
directions = st.text_area("Directions for Zone:", value=st.session_state.directions)

if 'mob' not in st.session_state:
    st.session_state.mob = ''
mob = st.text_input("MOB:", value=st.session_state.mob)

if st.button('Parse and Add to Database'):
    try:
        parsed_data = parse_item_data(pasted_data)
        parsed_data['Zone'] = zone
        parsed_data['Directions'] = directions
        parsed_data['MOB'] = mob

        df = pd.concat([df, pd.DataFrame([parsed_data])], ignore_index=True)
        df.to_excel('data.xlsx', index=False, engine='openpyxl')  # Specify the openpyxl engine here as well

        st.session_state.df = df  # Update the session state with the new dataframe
        st.success('Data parsed and added to the database!')

        # Optional: Display the last row to confirm data upload
        st.write(df.tail(1))

        # Clearing the fields after a successful data upload
        st.session_state.pasted_data = ''
        st.session_state.zone = ''
        st.session_state.directions = ''
        st.session_state.mob = ''

    except Exception as e:
        st.error(f"Error: {e}")


# Search functionality
st.subheader("Search Items")
search_name = st.text_input("Search by Item Name:")
search_zone = st.text_input("Search by Zone:")
search_mob = st.text_input("Search by MOB:")
search_type = st.text_input("Search by Type:")
search_worn_locations = st.text_input("Search by Worn Location:")

results = None
if st.button('Search'):
    results = df
    if search_name:
        results = results[results['name'].str.contains(search_name, case=False, na=False)]
    if search_zone:
        results = results[results['Zone'].str.contains(search_zone, case=False, na=False)]
    if search_mob:
        results = results[results['MOB'].str.contains(search_mob, case=False, na=False)]
    # Updated search logic for the new fields
    if search_type:
        results = results[results['type'].str.contains(search_type, case=False, na=False)]
    if search_worn_locations:
        results = results[results['worn_locations'].str.contains(search_worn_locations, case=False, na=False)]

    st.dataframe(results)

# ... [existing code]

# Edit functionality
st.subheader("Edit Data")

# Select item to edit
edit_name = st.selectbox("Select Item Name to Edit:", df['name'].unique())

# Select data column to edit
columns_to_edit = df.columns.tolist()
selected_column = st.selectbox("Select Data Column to Edit:", columns_to_edit)

# Get the current value of the selected data column for the chosen item
current_value = df[df['name'] == edit_name][selected_column].values[0]
if pd.isna(current_value):
    current_value = ''  # Set the current value to an empty string if it's NaN
st.write(f"Current {selected_column}: {current_value}")

# Determine and display the appropriate input field based on the selected column
new_data = ''
if selected_column in ["Directions", "pasted_data"]:
    # Use a text area for larger text fields
    new_data = st.text_area(f"Enter New {selected_column}:", value=current_value)
else:
    # Use a text input for other fields
    new_data = st.text_input(f"Enter New {selected_column}:", value=str(current_value))

# Two-step confirmation
if 'confirm_update' not in st.session_state:
    st.session_state.confirm_update = False

if st.button('Prepare to Update'):
    st.session_state.confirm_update = True

if st.session_state.confirm_update:
    st.warning("Are you sure you want to update this record?")
    if st.button("Confirm Update"):
        # Find the index of the selected data in the dataframe
        index_to_edit = df[df['name'] == edit_name].index[0]

        # Update the data in the dataframe
        df.at[index_to_edit, selected_column] = new_data

        # Save updated dataframe back to the Excel file
        df.to_excel('data.xlsx', index=False, engine='openpyxl')

        # Update the session state with the updated dataframe
        st.session_state.df = df

        st.success(f"'{edit_name}' has been updated in column '{selected_column}'!")

        # Reset the confirmation state
        st.session_state.confirm_update = False
