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

results = None
if st.button('Search'):
    results = df
    if search_name:
        results = results[results['name'].str.contains(search_name, case=False, na=False)]
    if search_zone:
        results = results[results['Zone'].str.contains(search_zone, case=False, na=False)]
    if search_mob:
        results = results[results['MOB'].str.contains(search_mob, case=False, na=False)]

    st.dataframe(results)
