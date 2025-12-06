import streamlit as st
import pandas as pd
import os

# --- Configuration ---
st.set_page_config(
    page_title="Voter List Search",
    layout="wide"
)

# Define the list of all CSV files and their location
CSV_FILES = [
    "voter_lists/1_Pappad.csv",
    "voter_lists/2_Manchampara_Marathakam.csv",
    "voter_lists/3_Manchampara_Manikyam.csv",
    "voter_lists/4_Communityhall_Rightside.csv",
    "voter_lists/5_Communityhall_Leftside.csv",
    "voter_lists/6_CPT.csv",
    "voter_lists/7_Depaul.csv",
]

# --- Data Loading and Cleaning ---

@st.cache_data
def load_and_clean_data():
    """Loads, combines, and cleans all voter data from CSV files."""
    all_data = []

    # Check for the data directory
    if not os.path.exists("voter_lists"):
        st.error("Error: The 'voter_lists' directory was not found. Please create it and place the CSV files inside.")
        return pd.DataFrame()

    # Load each file
    for file_path in CSV_FILES:
        try:
            # Reading with default index_col=False and standard encoding
            df = pd.read_csv(file_path, encoding='utf-8')
            all_data.append(df)
        except FileNotFoundError:
            st.warning(f"File not found: {file_path}. Skipping this list.")
        except Exception as e:
            st.error(f"Error loading {file_path}: {e}")

    # Combine all dataframes
    if not all_data:
        st.error("No voter data could be loaded. Please check your files.")
        return pd.DataFrame()

    voter_data = pd.concat(all_data, ignore_index=True)

    # Clean the combined data
    
    # 1. Drop completely empty columns (like the extra ones at the end of your file snippets)
    voter_data.dropna(axis=1, how='all', inplace=True)
    
    # 2. Rename columns to ensure consistency and correct capitalization
    # We rely on the first 7 columns being the standard ones found in the snippets
    try:
        voter_data.columns = [
            'Serial No.', 
            'Name', 
            "Guardian's Name", 
            'OldWard No/ House No.', 
            'House Name', 
            'Gender / Age', 
            'New SEC ID No.'
        ]
    except ValueError:
        st.error("Column mismatch detected. Please ensure all 7 CSV files have the expected 7 columns.")
        return pd.DataFrame()

    # 3. Split the 'Gender / Age' column
    voter_data[['Gender', 'Age']] = voter_data['Gender / Age'].str.split(' / ', expand=True)
    voter_data['Age'] = pd.to_numeric(voter_data['Age'], errors='coerce') # Convert Age to numeric
    
    # 4. Drop the original combined column
    voter_data.drop(columns=['Gender / Age'], inplace=True)
    
    # Select and reorder final columns for display
    final_columns = [
        'Serial No.',
        'Name', 
        'Gender', 
        'Age',
        "Guardian's Name", 
        'House Name',
        'OldWard No/ House No.', 
        'New SEC ID No.'
    ]
    
    # Ensure all final columns exist before subsetting
    # This guards against issues where certain files might have missing data/columns
    cols_to_keep = [col for col in final_columns if col in voter_data.columns]
    
    return voter_data[cols_to_keep]

# --- Main Streamlit App Logic ---

st.title("Voter List Search Application 🔎")
st.markdown("Search for a voter by **Name** in the compiled list of all 7 files.")

# Load the data using the cached function
df = load_and_clean_data()

if not df.empty:
    
    # Sidebar status
    st.sidebar.success(f"✅ Total Voters Loaded: {len(df):,}")
    
    # Search input
    search_term = st.text_input("Enter Voter's Name to Search (case-insensitive):").strip()
    
    # Search button (optional, but good for performance on large datasets)
    # if st.button("Search"):
    
    if search_term:
        # Perform the search: filter rows where 'Name' contains the search term
        # astype(str) handles potential NaN/non-string values in the 'Name' column
        filtered_df = df[
            df['Name'].astype(str).str.contains(search_term, case=False, na=False)
        ]
        
        # Display results
        st.subheader(f"Results for '{search_term}'")
        st.info(f"Found **{len(filtered_df)}** result(s).")
        
        if not filtered_df.empty:
            # Reset index for cleaner display in the table
            st.dataframe(filtered_df.reset_index(drop=True), use_container_width=True)
        else:
            st.warning("No matching voters found. Try a broader search term.")
            
    else:
        # Overview when no search is performed
        st.subheader("Voter List Overview (Sample Data)")
        st.dataframe(df.head(20), use_container_width=True)
        st.caption(f"Showing a sample of the first 20 records out of {len(df):,} total.")

else:
    st.error("The application failed to load data. Please check the console for errors and verify your 'voter_lists' directory setup.")
