import streamlit as st
import pandas as pd
from EQparser import parse_item_data

# -------------------------------------
# Load Data Function
# -------------------------------------
@st.cache_data(ttl=60*5)
def load_data():
    try:
        df = pd.read_excel('data.xlsx', engine='openpyxl')
    except FileNotFoundError:
        df = pd.DataFrame()
        df.to_excel('data.xlsx', engine='openpyxl')
    return df

# -------------------------------------
# Display Data Function
# -------------------------------------
import os


def display_data(df):
    if st.button('Show All Data'):
        st.write(df)

    if st.button('Clear Displayed Data'):
        st.experimental_rerun()

    # Provide a download link for the data.xlsx file
    if os.path.exists('data.xlsx'):
        with open('data.xlsx', 'rb') as file:
            file_bytes = file.read()
        st.download_button(
            label="Download data.xlsx",
            data=file_bytes,
            file_name="data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# -------------------------------------
# Add New Data Function
# -------------------------------------
def add_new_data(df):
    # Use a unique key for the text_area widget
    if 'pasted_data_key' not in st.session_state:
        st.session_state.pasted_data_key = "initial_key"

    if 'pasted_data' not in st.session_state:
        st.session_state.pasted_data = ''

    pasted_data = st.text_area("Paste the item data here:", value=st.session_state.pasted_data,
                               key=st.session_state.pasted_data_key)

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
            df.to_excel('data.xlsx', index=False, engine='openpyxl')

            st.session_state.df = df
            st.success('Data parsed and added to the database!')
            st.write(df.tail(1))

            st.session_state.pasted_data = ''
            st.session_state.zone = ''
            st.session_state.directions = ''
            st.session_state.mob = ''

        except Exception as e:
            st.error(f"Error parsing or adding data: {e}")

    # Clear Fields Button
    if st.button('Clear Fields'):
        st.session_state.pasted_data_key = str(
            hash(st.session_state.pasted_data_key + "new"))  # Generate a new unique key
        st.session_state.pasted_data = ''
        st.session_state.zone = ''
        st.session_state.directions = ''
        st.session_state.mob = ''
        st.experimental_rerun()

# -------------------------------------
# Search Data Function
# -------------------------------------
def search_data(df):
    st.subheader("Search Items")

    # Unique keys for the search fields
    search_name_key = "search_name_key"
    search_zone_key = "search_zone_key"
    search_mob_key = "search_mob_key"
    search_type_key = "search_type_key"
    search_worn_locations_key = "search_worn_locations_key"

    # Initialize them if they aren't in session state
    for key in [search_name_key, search_zone_key, search_mob_key, search_type_key, search_worn_locations_key]:
        if key not in st.session_state:
            st.session_state[key] = "initial_" + key

    search_name = st.text_input("Search by Item Name:", key=st.session_state[search_name_key])
    search_zone = st.text_input("Search by Zone:", key=st.session_state[search_zone_key])
    search_mob = st.text_input("Search by MOB:", key=st.session_state[search_mob_key])
    search_type = st.text_input("Search by Type:", key=st.session_state[search_type_key])
    search_worn_locations = st.text_input("Search by Worn Location:", key=st.session_state[search_worn_locations_key])

    if st.button('Search'):
        try:
            results = df
            if search_name:
                results = results[results['name'].str.contains(search_name, case=False, na=False)]
            if search_zone:
                results = results[results['Zone'].str.contains(search_zone, case=False, na=False)]
            if search_mob:
                results = results[results['MOB'].str.contains(search_mob, case=False, na=False)]
            if search_type:
                results = results[results['type'].str.contains(search_type, case=False, na=False)]
            if search_worn_locations:
                results = results[results['worn_locations'].str.contains(search_worn_locations, case=False, na=False)]
            st.dataframe(results)
        except Exception as e:
            st.error(f"Error during search: {e}")

    # Clear Fields Button
    if st.button('Clear Fields'):
        # Generate new unique keys for the search fields
        st.session_state[search_name_key] = str(hash(st.session_state[search_name_key] + "new"))
        st.session_state[search_zone_key] = str(hash(st.session_state[search_zone_key] + "new"))
        st.session_state[search_mob_key] = str(hash(st.session_state[search_mob_key] + "new"))
        st.session_state[search_type_key] = str(hash(st.session_state[search_type_key] + "new"))
        st.session_state[search_worn_locations_key] = str(hash(st.session_state[search_worn_locations_key] + "new"))
        st.experimental_rerun()

# -------------------------------------
# Edit Data Function
# -------------------------------------
def edit_data(df):
    st.subheader("Edit Data")

    # Define unique keys for the widgets
    select_name_key = "select_name_key"
    select_column_key = "select_column_key"
    input_field_key = "input_field_key"

    # Initialize them if they're not in session state
    if select_name_key not in st.session_state:
        st.session_state[select_name_key] = "initial_name_key"
    if select_column_key not in st.session_state:
        st.session_state[select_column_key] = "initial_column_key"
    if input_field_key not in st.session_state:
        st.session_state[input_field_key] = "initial_input_key"

    edit_name = st.selectbox("Select Item Name to Edit:", [""] + sorted(df['name'].unique()),
                             key=st.session_state[select_name_key])
    columns_to_edit = [""] + df.columns.tolist()
    selected_column = st.selectbox("Select Data Column to Edit:", columns_to_edit,
                                   key=st.session_state[select_column_key])

    if edit_name and selected_column:
        current_value = df[df['name'] == edit_name][selected_column].values[0]
        if pd.isna(current_value):
            current_value = ''
        st.write(f"Current {selected_column}: {current_value}")

        new_data = ''
        if selected_column in ["Directions", "pasted_data"]:
            new_data = st.text_area(f"Enter New {selected_column}:", value=current_value,
                                    key=st.session_state[input_field_key])
        else:
            new_data = st.text_input(f"Enter New {selected_column}:", value=str(current_value),
                                     key=st.session_state[input_field_key])

        if 'confirm_update' not in st.session_state:
            st.session_state.confirm_update = False

        if st.button('Prepare to Update'):
            st.session_state.confirm_update = True

        if st.session_state.confirm_update:
            st.warning("Are you sure you want to update this record?")
            if st.button("Confirm Update"):
                try:
                    # Find the index of the selected data in the dataframe
                    index_to_edit = df[df['name'] == edit_name].index[0]

                    # Update the data in the dataframe
                    df.at[index_to_edit, selected_column] = new_data

                    # Save updated dataframe back to the Excel file
                    df.to_excel('data.xlsx', index=False, engine='openpyxl')

                    # Update the session state with the updated dataframe
                    st.session_state.df = df
                    st.success(f"'{edit_name}' has been updated in column '{selected_column}'!")

                    # Reset the confirmation state and the widget keys
                    st.session_state.confirm_update = False
                    st.session_state[select_name_key] = str(hash(st.session_state[select_name_key] + "new"))
                    st.session_state[select_column_key] = str(hash(st.session_state[select_column_key] + "new"))
                    st.session_state[input_field_key] = str(hash(st.session_state[input_field_key] + "new"))
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error updating data: {e}")

# -------------------------------------
# Main Body
# -------------------------------------
st.title('Nukefire EQ Database')
st.markdown('This tool is a rough draft and will be updated over time.\n\nSee below for example of what identify data is needed for upload. Questions, comments, complaints - see Biscuit in the Nukefire Discord.')
st.markdown('[Nukefire Discord](https://discord.gg/XMFPShK2)', unsafe_allow_html=True)

example_data_string = """
Object 'a mystical pendant', Item type: TREASURE
Item will give you following abilities:  NOBITS 
Worn Location(s): TAKE NECK 
Item is: NOBITS 
Weight: 3, Suggested Retail Value: 1000, Rent: 20, Min. level: 0
Can affect you as :
   Affects: SPELLPOWER By 2
   Affects: HITROLL By 1
   Affects: MAXMANA By 15
   Affects: DEX By 1
   Affects: INT By 1
   Affects: WIS By 1
"""

st.text(example_data_string)

if 'df' not in st.session_state:
    st.session_state.df = load_data()
df = st.session_state.df

st.sidebar.header("Actions")
action = st.sidebar.radio("Select Action", ["Display Data", "Add New Data", "Search Data", "Edit Data"])

if action == "Display Data":
    display_data(df)
elif action == "Add New Data":
    add_new_data(df)
elif action == "Search Data":
    search_data(df)
elif action == "Edit Data":
    edit_data(df)
