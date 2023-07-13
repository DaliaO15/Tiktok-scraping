import pandas as pd
import os
from yt_dlp import YoutubeDL
import logging
import os.path
from fastparquet import write

"""
This code generates two outputs:
1. A data frame (.parquet file) with the status of each video, i.e, wheter it was successfully downloaded or not. 
2. All the videos stored in a folder per author. 
"""

logging.basicConfig(level=logging.INFO, filename='video_download.log', 
                    format='%(asctime)s : %(levelname)s : %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')

def create_folder(folder):
    try: # if it is possible to create the folder
        os.mkdir(folder)
    except: # if the folder was not created successfuly, raise a warning
        logging.info('There is an error with the folder')

def video_download(root_folder:str, df:pd.DataFrame, download_status_path:str): 
    # df: metadata. df must contain a column called Video_url where the urls to the videos are stored
    # root_folder: folder where videos are to be stored
    # download_status_path: location of the oarquet file that will contain the download status per video
    
    file_path = download_status_path + '/downloads_status.parquet'

    for idx in range(0,df.shape[0]):

        # Access the video url from data frame
        channel_name = df['Author'].iloc[idx]
        video_url = df['Video_url'].iloc[idx]
        down_request = df['Download_request'].iloc[idx]

        # Create a folder for that channel
        channel_folder = root_folder + channel_name + '/'
        
        # Create a new folder for the channel
        if not os.path.exists(channel_folder):
            create_folder(channel_folder)

        # Set the options for downloading the videos 
        ydl_opts = {'outtmpl': channel_folder + '%(id)s.%(ext)s',
                    'format': 'best[ext=mp4]/mp4',
                    'overwrites': False,
                    'retries': 15,
                    'concurrent-fragments':12}
        
        # Download only the 'Yes' videos
        if down_request == 'Yes':
            try:
                collected_status = 'Downloaded'
                with YoutubeDL(ydl_opts) as ydl:
                    ydl.download([video_url]) 

            except Exception as e:
                logging.error(f'Error when downloading video {video_url} in channel {channel_name}')
                logging.error(f'We are in index {idx}')
                logging.error(f"Error: {e}")
                collected_status = 'Error'
        else:
            logging.info(f'The video {video_url} is not requiered to be downloaded')
            logging.info(f'We are in index {idx}')
            collected_status = 'No'
        
        # Save downloading status 
        info = {'Channel':[channel_name],'Video_url':[video_url], 'Status':[collected_status]} 

        # Store the info in the parque file 
        if not os.path.isfile(file_path):
            write(file_path, pd.DataFrame(info))
        else:
            write(file_path, pd.DataFrame(info), append=True)


def video_download_re_try(root_folder:str, df:pd.DataFrame, download_status_path:str): 
    # df: metadata. df must contain a column called Video_url where the urls to the videos are stored
    # root_folder: folder where videos are to be stored
    # download_status_path: location of the oarquet file that will contain the download status per video
    
    file_path = download_status_path + '/downloads_re-try_status.parquet'

    for idx in range(0,df.shape[0]):

        # Access the video url from data frame
        channel_name = df['Channel'].iloc[idx]
        video_url = df['Video_url'].iloc[idx]

        # Create a folder for that channel
        channel_folder = root_folder + channel_name + '/'
        
        if not os.path.exists(channel_folder):
            create_folder(channel_folder)

        # Set the options for downloading the videos 
        ydl_opts = {'outtmpl': channel_folder + '%(id)s.%(ext)s',
                    'format': 'best[ext=mp4]/mp4',
                    'overwrites': False,
                    'retries': 15,
                    'concurrent-fragments':12}
        
        # Download all videos
        try:
            collected_status = 'Downloaded'
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url]) 

        except Exception as e:
            logging.error(f'Error when downloading video {video_url} in channel {channel_name}')
            logging.error(f'We are in index {idx}')
            logging.error(f"Error: {e}")
            collected_status = 'Error'

        
        # Save downloading status 
        info = {'Channel':[channel_name],'Video_url':[video_url], 'Status':[collected_status]} 

        # Store the info in the parque file 
        if not os.path.isfile(file_path):
            write(file_path, pd.DataFrame(info))
        else:
            write(file_path, pd.DataFrame(info), append=True)            
            
def main():
    
    # Set up paths
    download_request_path = 'PATH/TO/DOWNLOAD_REQUEST_INFO/gifts_w_downrequest.parquet' ####---------------------///---- modify here
    gifts = pd.read_parquet(download_request_path, engine='fastparquet')
    
    # Path to store the file that contains the status of each video to analyse, find errors, and re-try downloads if needed. 
    download_status = 'PATH/TO/DOWNLOAD_STATUS_INFO/' ####---------------------///---- modify here
    
    # Path to store the videos
    storage_path = 'PATH/TO/VIDEOS/STORAGE/FOLDER' ####---------------------///---- modify here
    
    # Download
    video_download(root_folder = storage_path, df=gifts, download_status_path=download_status)
    #video_download_re_try(root_folder = storage_path, df = gifts, download_status_path=download_status) # In case of re-trying downloads
    
    
if __name__ == "__main__":
    main()