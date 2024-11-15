from os import path
import os
import streamlit as st
import streamlit.components.v1 as components
import subprocess as subp
import pandas as pd 
import datetime
from csv import writer
from csv import reader

# Get current and parent directory paths
path_to_script = path.dirname(path.realpath(__file__))
parent_path = os.path.dirname(path_to_script)

# Set default creator_id
creator_id = ''

# Define file paths
SCAM_FILE = f'{parent_path}/db/scamrecords.csv'
UPLOADED_FOLDER = f'{parent_path}/uploaded_files/'

# Set Streamlit page configuration
st.set_page_config(page_title='Report Scam🔗', page_icon='⛓️', layout="wide", initial_sidebar_state="expanded")

# Function to output DataFrame to CSV
def csvout(df):
    df.to_csv(SCAM_FILE, mode='a', index=False, header=False)
    st.success('Data saved successfully. Thank you for reporting.')

# Define the main function to collect scam information
import datetime

def scam_collector(creator_id):
    st.write(f'Hello {creator_id}, thank you for your contribution in cleaning up the world a bit....')
    st.markdown("# See something...? Say Something!")
    st.markdown("##### Record Scams in the Criminal Chain")

    # Unique keys for text inputs to avoid duplicate errors
    scam_site = st.text_input("Scam platform name/App Name/website link:", key=f"{creator_id}_scam_site")
    scam_wallet = st.text_input("**Scammer's Receiving Account:**", key=f"{creator_id}_scam_wallet")
    Transcation_Hash = st.text_input("Transaction Hash:", key=f"{creator_id}_transaction_hash")
    victim = st.text_input("Victim Account:", key=f"{creator_id}_victim")
    
    scam_tool = st.selectbox("Chat tool:", ['', 'Whatsapp', 'Line', 'Phone', 'Wechat', 'Telegram', 'Signal', 'Facebook', 'Instagram', 'Other'], key=f"{creator_id}_scam_tool")
    scam_contact = st.text_input("Contact number (including country code):", key=f"{creator_id}_scam_contact")
    scammer_url = st.text_input("Scammer's social media link:", key=f"{creator_id}_scammer_url")
    notes = st.text_area("Notes", key=f"{creator_id}_notes")

    # File uploader with unique key
    unique_key_file = f"{creator_id}_file_{datetime.datetime.now().timestamp()}"
    uploaded_files = st.file_uploader("**Upload scam relevant files**", accept_multiple_files=True, key=unique_key_file)
    
    # Button with unique key
    unique_key_button = f"{creator_id}_button_{datetime.datetime.now().timestamp()}"
    if st.button("Confirm Upload", key=unique_key_button):
        for uploaded_file in uploaded_files:
            bytes_data = uploaded_file.read()
            record_folder = path.join(UPLOADED_FOLDER, creator_id)
            record_filename = f'{creator_id}_{uploaded_file.name}'
            os.makedirs(record_folder, exist_ok=True)
            with open(f'{record_folder}/{record_filename}', "wb") as saved_file:
                saved_file.write(bytes_data)
                st.success(f'File \"{uploaded_file.name}\" uploaded successfully.')

    # Additional code for other form inputs continues here...


    # Scam details section
    data = {'ScamType': [], 'ScamWallet': [], 'TransactionHash': [], 'TransactionDate': [], 'ScamDate': [],
            'Amount': [], 'Currency': [], 'Victim': []}
    collect_df = pd.DataFrame(data)
    scam_type = st.selectbox("**Scam Type:**", ['Crytocurrency', 'Bank', 'Gift Card', 'Other'])

    scam_wallet = ""
    Transcation_Hash = ""
    scammed_date = datetime.date.today()
    amount = 0.0
    currency_type = ""
    
    if scam_type == 'Crytocurrency':
        scam_wallet = st.text_input("**Scammer's Receiving Account:**")
        Transcation_Hash = st.text_input("Transaction Hash:")
        scammed_date = st.date_input("Transaction Date:", datetime.date.today())
        amount = st.number_input("Scammed Amount:", format="%.7f")
        currency_type = st.selectbox('💱Currency:', ['', 'BTC', 'ETH', 'USDT', 'Other'])
        if currency_type == 'Other':
            currency_type = st.text_input('Please enter the currency:')
    
    victim = st.text_input("Victim Account:")
    
    # Temporary DataFrame for transaction records
    transaction_df = pd.DataFrame(columns=collect_df.columns)
    
    if st.button("Add Another Transaction Record"):
        new_row = {
            'ScamType': scam_type,
            'ScamWallet': scam_wallet,
            'TransactionHash': Transcation_Hash,
            'TransactionDate': scammed_date,
            'ScamDate': datetime.date.today(),
            'Amount': amount,
            'Currency': currency_type,
            'Victim': victim,
        }
        transaction_df = transaction_df.append(new_row, ignore_index=True)
        st.write(transaction_df)  # Display updated DataFrame

    # Contact information section
    scam_tool = st.selectbox("Chat tool:", ['', 'Whatsapp', 'Line', 'Phone', 'Wechat', 'Telegram', 'Signal', 'Facebook', 'Instagram', 'Other'])
    scam_contact = st.text_input("Contact number (including country code):")
    scammer_url = st.text_input("Scammer's social media link:")
    notes = st.text_area("Notes")

    # If Submit button is clicked
    if st.button("Submit Scam Record"):
        scam_df = transaction_df[transaction_df['ScamWallet'] == creator_id]  # Filter if applicable
        csvout(scam_df)

# Run the function
scam_collector(creator_id)

    # ##st.write(pychain.chain)
    # if pychain_df.loc[0,:].isna==False:
    #     st.markdown("##### You reported:")
    #     showcolumns =['Sender','Scam_wallet','Amount','Transcation_Hash','Currency','Scammed_date','scam_site','scammer_url','scam_tool','scam_contact','notes' ]
    #     shown_table = pychain_df[pychain_df['creator_id'] == creator_id][showcolumns]
    #     st.table(shown_table)   
    ################################################################################
    # Define side bar GUI   
    # if st.sidebar.button("Validate Chain"):
    #     st.sidebar.write(pychain.is_valid())   
    # if st.button("In Ashes Criminals Shall Reap!"):
    #      st.audio("https://minty.club/artist/hatebreed/in-ashes-they-shall-reap/hatebreed-in-ashes-they-shall-reap.mp3", format="audio/mp3")
    ################################################################################
