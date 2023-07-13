import whisper
import pandas as pd
import json 
import subprocess
import os 
import time
import logging

"""
This code applies the Whisper medium english model to every video. It generates a folder per author 
containing a json file per video transcription.
Thee tree structure would look like this:
-Data
    -Videos
        -Author1
            -video1-1.mp4
            -video2-1.mp4
        -Author2
            -video1-2.mp4
            -video2-2.mp4
    -Transcriptions
        -Author1
            -video1-1.json
            -video2-1.json
        -Author2
            -video1-2.json
            -video2-2.json
"""

# Create file for tracking error
logging.basicConfig(level=logging.INFO, filename='transcriptions.log', 
                    format='%(asctime)s : %(levelname)s : %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')

# To run whispers with custom parameters 
def transcript(video_path:str, output_path:str):
    comand = ['whisper', video_path, 
              '--model', 'medium.en',
              '--threads', '50',
              '--output_format', 'json', 
              '--output_dir', output_path]
    # Run
    subprocess.run(comand)
    
# Applying Whispers in all gifts     
def all_transcriptions(root_folder:str, input_dir_name:str, output_dir_name:str): 
    
    gifts_folder = root_folder + input_dir_name
    gifts_transcriptions_folder = root_folder + output_dir_name
    
    # Get paths for all gifts
    channels_names = [f for f in os.listdir(gifts_folder) if not f.startswith('.')]
    for c in channels_names:
        
        # Make output folder 
        trans_path = os.path.join(gifts_transcriptions_folder, c)
        #os.makedirs(trans_path, exist_ok=True)
        
        # Get paths to gifts
        channel_path = os.path.join(gifts_folder,c) 
        gifts_paths = [os.path.join(channel_path,f) for f in os.listdir(channel_path) if not f.startswith('.')]
        
        # Apply the model to each gift
        for gift in gifts_paths:
            try:
                transcript(gift, trans_path)
            except Exception as e:
                logging.error(f'Error transcribing gift {gift} from {c}')

def main(): 
    
    # For timing
    start_time = time.time()
    # Running Whispers 
    all_transcriptions(root_folder = 'PATH/TO/ROOT', ####---------------------///---- modify here
                       input_dir_name = 'PATH/TO/FOLDER/WITH/VIDEOS', 
                       output_dir_name = 'PATH/TO/FOLDER/FOR/TRANSCRIPTIONS')
    # Print final time
    print("--- %s seconds for execution ---" % (time.time() - start_time))
    
    
if __name__ == "__main__":
    main()