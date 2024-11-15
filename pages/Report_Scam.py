from os import path
import os
import streamlit as st
import streamlit.components.v1 as components
import subprocess as subp
import pandas as pd 
import datetime
from csv import writer
from csv import reader


path_to_script = path.dirname(path.realpath(__file__))
parent_path = os.path.dirname(path_to_script) ## get parenet directory

###########set default creator_id
creator_id =''

SCAM_FILE = f'{parent_path}/db/scamrecords.csv'
UPLOADED_FOLDER = f'{parent_path}/uploaded_files/'

## Set page title and icons:
st.set_page_config(page_title='Report Scam🔗', page_icon='⛓️', layout="wide", initial_sidebar_state="expanded" , menu_items=None) 
###############################################################################    
def csvout(df):
    # with open(SCAM_FILE, 'a') as csvfile:
    #     csvwriter = writer(csvfile)
        # csvwriter.writerow(df)
        df.to_csv(SCAM_FILE, mode ='a',index=False, header=False)
#        st.write(f'[+] Data Saved : {SCAM_FILE}\n')
        st.write(f'Data Saved sucessfully. Thank you for reporting.\n')

def scam_collector(creator_id):
### Define collecting page
    st.write(f'Hello {creator_id}, thank you for your contribution in cleaning up the world for a bit....')
    st.markdown("# See something...? Say Something!")     
    ################ Upload files and save files ################ 
    st.markdown("##### Record Scams in the Criminal Chain")  
    uploaded_files = st.file_uploader("**Upload scam relevant files**", accept_multiple_files=True)
    for uploaded_file in uploaded_files:
         bytes_data = uploaded_file.read()
         if st.button("Confirm Upload"):
                # Create a new folder to store uploaded files
                record_folder = path.join(UPLOADED_FOLDER, creator_id) # Assigns upload path to variable
                record_filename = f'{creator_id}{uploaded_file.name}'
                try:
                    os.makedirs(record_folder) #create the new folder if this doens't already exist
                except Exception: 
                    pass
                with open(f'{record_folder}/{record_filename}',"wb") as saved_file:
                    saved_file.write(bytes_data)
                    st.write('File is uploaded sucessfully')  
    ################ Scam wallets collection section ################ 
    # Create an empty dataframe
    data = {'ScamType':[],'ScamWallet':[],'TransactionHash': [], 'TransactionDate': [], 'ScamDate': [],
            'Amount': [], 'Currency': [],'Victim':[]}
    collect_df = pd.DataFrame(data)
    scam_site = st.text_input(label="Scam platform name/App Name/website link:") 
    # Select scam type
    scam_type = st.selectbox(label="**Scam Type:**", options=['Crytocurrency','Bank','Gift Card','Other'])
    if scam_type=='Crytocurrency':
        scam_wallet = st.text_input("**Scammer's Receiving Account:**", key =1)
        Transcation_Hash,scammed_date = st.columns(2)
        Transcation_Hash = Transcation_Hash.text_input("Transaction Hash:")
        scammed_date= scammed_date.date_input("Transaction Date:", datetime.date.today())
        amount,currency_type = st.columns(2)
        amount = amount.number_input(label="Scammed Amount:", format="%.7f")
        currency_type = currency_type.selectbox('💱Currency:', options=['', 'BTC', 'ETH', 'USDT', 'Other'], key=2)
        if currency_type == 'Other':
            currency_type = st.text_input('Please enter the currency:')   
    #st.write('The wallets you entered is:', scam_wallet)
    ################################################################################  
    victim = st.text_input("Victim Account:")  ## Convert input data into string then encode it       
    if st.button("Add Another Transcation Record"):
             # Append a new row with user's input to the dataframe
        new_row = { 'ScamType':scam_type,'ScamWallet':scam_wallet,'TransactionHash':Transcation_Hash, 
                   'ScamDate':scammed_date, 'Amount':amount, 'Currency':currency_type,'Victim':victim,}
        df = df.append(new_row, ignore_index=True)
        st.write(df)  # write dataframe to the app
         
   ##### Define GUI texts and input areas here: 
    scam_tool, scam_contact,scammer_url =st.columns(3)
    scam_tool = scam_tool.selectbox(label = "Chat tool:", options = ['','Whatsapp','Line','Phone','Wechat','Telegram','Signal','Facebook','Instagram','Other'])
    scam_contact = scam_contact.text_input(label='Contact number(including country code)') 
    scammer_url = scammer_url.text_input(label="Scammer's social media link:")
    notes = st.text_area("Notes")     
    #######
    pychain_df = pd.DataFrame(pychain.chain)

    if st.button("Submit Scam Record"):
        scam_df =pychain_df[pychain_df.creator_id == creator_id]
        csvout(scam_df)  

    ##st.write(pychain.chain)
    if pychain_df.loc[0,:].isna==False:
        st.markdown("##### You reported:")
        showcolumns =['Sender','Scam_wallet','Amount','Transcation_Hash','Currency','Scammed_date','scam_site','scammer_url','scam_tool','scam_contact','notes' ]
        shown_table = pychain_df[pychain_df['creator_id'] == creator_id][showcolumns]
        st.table(shown_table)   
    ################################################################################
    # Define side bar GUI   
    # if st.sidebar.button("Validate Chain"):
    #     st.sidebar.write(pychain.is_valid())   
    # if st.button("In Ashes Criminals Shall Reap!"):
    #      st.audio("https://minty.club/artist/hatebreed/in-ashes-they-shall-reap/hatebreed-in-ashes-they-shall-reap.mp3", format="audio/mp3")
    ################################################################################
scam_collector(creator_id=creator_id)