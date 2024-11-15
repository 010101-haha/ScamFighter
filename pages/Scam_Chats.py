import pandas as pd
import os
import streamlit as st
import emoji
import time
from PIL import Image
from pathlib import Path


creator_id=''
# Specify the directory where images are stored
folder_dir = Path(os.getcwd())/'scam_chats'

try: 

    col1, col2 =  st.columns(spec=[0.45,0.55])
    #UPLOADED_FOLDER = Path(os.getcwd()).parent/'uploaded_files'
    uploaded_files = col1.file_uploader("**Reveal My Scammer⚓Records Forever**", accept_multiple_files=True)
    ##### Confirm to upload files
    if uploaded_files:
        # Display a confirm button
        if col1.button("Confirm Upload"):
            # Process each uploaded file
            for uploaded_file in uploaded_files:
                bytes_data = uploaded_file.read()
                #st.write("filename:", uploaded_file.name)
                # Create a new folder to store uploaded files
                record_folder = os.path.join(folder_dir, creator_id) # Assigns upload path to variable
                record_filename = f'{creator_id}{uploaded_file.name}'
                try:
                    os.makedirs(record_folder) #create the new folder if this doesn't already exist
                except Exception: 
                    pass
                with open(f'{record_folder}/{record_filename}',"wb") as saved_file:
                    saved_file.write(bytes_data)
                    col1.write('File is uploaded successfully')

    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')

    # Get list of all files in the directory
    files = os.listdir(folder_dir)
    # Filter the list of files to include only .jpg and .png files
    images = [file for file in files if file.endswith(('jpg', 'png','jpeg'))]
    # # Display images
    # for imagename in images:
    #     display_image = Image.open(os.path.join(folder_dir, imagename))
    #     st.image(display_image,use_column_width=True)
    #     time.sleep(1) # delay for 1 second


    # Store the current image index in a persistent variable
    index = st.session_state.get('image_index', 0)
    # Display the image
    display_image = Image.open(os.path.join(folder_dir, images[index]))
    #img_resized=  display_image.resize((800, 300))
    col2.image(display_image, use_column_width=True)

    # Create two columns for buttons to sit next to each other
    # Create a button to go to the next image
    if col1.button('👀 Next 🖻'):
        # Increment the index
        index += 1
        # If we have reached the end of the list of images, go back to the first image
        if index == len(images):
            index = 0
        # Update the persistent variable
        st.session_state.image_index = index

    # Create a button to go to the previous image
    if col1.button('👀 Previous 🖻'):
        # Decrement the index
        index -= 1
        # If the index is negative, go to the last image
        if index < 0:
            index = len(images) - 1
        # Update the persistent variable
        st.session_state.image_index = index

    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')
    
    #st.markdown('<img src="https://placekitten.com/200/300" width=300 height=100>', unsafe_allow_html=True)
    # if st.button("Take a shot"):
    #     picture = st.camera_input("Take a picture")

    #     if picture:
    #         st.image(picture)
    # Filter the list of files to include only .jpg and .png files
    videos = [file for file in files if file.endswith(('mp4', 'rmbv'))]
    # Store the current image index in a persistent variable
    video_index = st.session_state.get('video_index', 0)
    # Display the image
    display_video = open(os.path.join(folder_dir, videos[video_index]),'rb')
    col2.video(display_video, format="video/mp4", start_time=0)

    # Create a button to go to the next video
    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')
    col1.markdown('\n')
    if col1.button('👀 Next 🎞️'):
        # Increment the index
        video_index += 1
        # If we have reached the end of the list of images, go back to the first image
        if video_index == len(videos):
            video_index = 0
        # Update the persistent variable
        st.session_state.video_index = video_index
        # Create a button to go to the previous video
    if col1.button('👀 Previous 🎞️'):
        # Decrement the index
        video_index -= 1
        # If the index is negative, go to the last video
        if video_index < 0:
            video_index = len(videos) - 1
        # Update the persistent variable
        st.session_state.vidoe_index = video_index

        #######################
        ###### User comments session #############

    # Get user input
    User_name = col1.text_input("User Name(Optional):")
    user_comment = col1.text_area("**Enter your comment:**")



    new_comment = emoji.emojize(user_comment)

    # Save DataFrame to csv file
    comments_file= Path(os.getcwd())/'data/comments.csv'
    # If there's a new comment, append it to the CSV file
    if col1.button("Post"):
        # Append new comment to CSV file
        if not User_name:
            User_name="Someone" ## Assign default value
        with open(comments_file, 'a+', encoding='utf-8') as f:
            f.write(f"{User_name}, {new_comment} \n")

    # If comment file exists, load all comments from the CSV file into a DataFrame
    if os.path.isfile(comments_file):
        df_comments = pd.read_csv(comments_file, names=["Comment"])
        # Display all comments
        st.subheader("Comments")
        for comment in df_comments['Comment']:
            st.markdown(comment)

except Exception as e:
    st.write("Error Occured", e)