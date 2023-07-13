import openpyxl
import pandas as pd
import json 
import subprocess
import os 
from fastparquet import write
import re
import spacy
import numpy as np
from matplotlib import pyplot as plt
from spacy.lang.en.stop_words import STOP_WORDS
from collections import Counter 
nlp = spacy.load("en_core_web_sm")


def info_x_author(general_df:pd.DataFrame, target_author_df:pd.DataFrame, author_name:str):
    """The function merges the final data frame from scraping, which combines all authors, with the transcripts per author, 
    creating a new data frame that contains both the scraping information and the transcriptions for each individual author.

    general_df: the df that contains the info from all authors
    target_author_df: the df that contains the transcriptions
    author_name: the name of the channel or author 
    """
    
    # First extract the channel info only 
    author_from_final = general_df[general_df['Author'] == author_name]
    
    # Now join
    author_df = author_from_final.join(target_author_df.set_index('Video_url'), on='Video_url').reset_index(drop=True)
    
    return author_df


def clean(transcription):
    """Returns text without messy punctuation marks"""
    try: 
        transcription = re.sub(r'_+', ' ', transcription) # Remove underscores
        transcription = re.sub(r'"+', '"', transcription) # Remove multiple quotes
        transcription = transcription.replace(",", " ") # Remove commas
        transcription = transcription.replace(".", " ")# Remove dots
    except: 
        pass
    
    return transcription


def max_len(transcirption):
    """To find the maximum length of a transcription"""
    lens = []
    lens.append(len(str(transcirption))) 
    
    return max(lens)

        
def word_tagging(transcription):
    """To assing tags to each type of word. There are Adjectives, nouns and verbs"""
    doc = nlp(str(transcription))
    
    adjectives = []
    nouns = []
    verbs = []
    lemmas = []
    
    for token in doc:
        lemmas.append(token.lemma_)
        if token.pos_ == "ADJ":
            adjectives.append(token.lemma_)
        if token.pos_ == "NOUN" or token.pos_ == "PROPN":
            nouns.append(token.lemma_)
        if token.pos_ == "VERB":
            verbs.append(token.lemma_)
            
    return adjectives, nouns, verbs, lemmas

def remove_stopwords(tokens):
    """Remove stopwords form a list of tokens"""
    return [t for r in tokens if t not in STOP_WORDS]


def text_analysis(author_df:pd.DataFrame):
    
    # Clean the data frame 
    author_df['Text_clean'] = author_df.Text.map(clean)

    # Generate tokens for author
    taggs = author_df.Text_clean.map(word_tagging)
    taggs_author_df = taggs.apply(pd.Series)
    taggs_author_df.columns=['Adjectives', 'Nouns', 'Verbs', 'Lemmas']
    author_df = author_df.join(taggs_author_df)
    
    return author_df

def count_common_words(author_df:pd.DataFrame, column:str):
    """Frequency counter give an column in the dataframe"""
    if column in ['Adjectives', 'Nouns', 'Verbs', 'Lemmas']:
        words = author_df[column].sum()
        counter = Counter(words)
        return counter
    else:
        print('Invalid column name')
        return None

def plot_hist(counter_name:Counter, nbr_of_words:int, author:str, column_name:str, output_path:str):
    y = [count for tag, count in counter_name.most_common(nbr_of_words)]
    x = [tag for tag, count in counter_name.most_common(nbr_of_words)]
    colors = ['crimson', 'purple','mediumaquamarine','steelblue']
    if column_name == 'Adjectives': 
        c = colors[0]
    elif column_name == 'Nouns': 
        c = colors[1]
    elif column_name == 'Verbs': 
        c = colors[2]
    else: 
        c = colors[3]
    
    plt.figure()
    plt.bar(x, y, color=c)
    plt.title(f"{column_name} frequencies in {author} gifts' transcriptions")
    plt.xticks(rotation=90)
    for i, (tag, count) in enumerate(counter_name.most_common(nbr_of_words)):
        plt.text(i, count, f' {count} ', rotation=90,
                 ha='center', va='top' if i < 10 else 'bottom', color='white' if i < 10 else 'black')
    plt.xlim(-0.6, len(x)-0.4) # optionally set tighter x lims
    plt.tight_layout() # change the whitespace such that all labels fit nicely
    plt.savefig(output_path)
    #plt.show()


def main():
    
    # Set file paths 
    root = 'PATH/TO/ROOT'
    in_path = 'Gifts_transcriptions_parsed_part2/Transciprtions_parsed/' ####---------------------///---- modify here
    out_path = 'PATH/TO/FOLDER/FOR/TRANSCRIPTIONS_IN_DATAFRAMES' ####---------------------///---- modify here
    final_df_name = 'PATH/TO/INFO_FILE/gifts_info.parquet' ####---------------------///---- modify here
    
    # Accessing and storing file names
    parque_names = [f for f in os.listdir(root+in_path) if not f.startswith('.')]
    parque_paths = [os.path.join(root+in_path,c) for c in parque_names] 
    final_parquet = pd.read_parquet(root + final_df_name,engine='fastparquet')
    cc = 0
    
    # Process and analyse each data frame
    for p in parque_paths:
        
        name = p.split('/')[-1].split('.parquet')[0]#+'  ' #this is bcs there are folders with ' ' at the end of their names
        author_df = pd.read_parquet(p,engine='fastparquet')
        print(name)
        
        # Merge to obtain an individual df per author 
        author_df = info_x_author(general_df=final_parquet, target_author_df=author_df, author_name=name)
        author_df = text_analysis(author_df)
        author_df.to_parquet(root+out_path+name.strip()+'.parquet',engine='fastparquet')
        
        if cc == 0:
            # Plot just one example. Remove the if and modify the name of the column to get other plots
            col1 = 'Verbs'
            plot_hist(count_common_words(author_df, col1), 20, name.strip(), col1, root+out_path+name.strip()+'_'+col1+'.jpeg')
            col2 = 'Adjectives'
            plot_hist(count_common_words(author_df, col2), 20, name.strip(), col2, root+out_path+name.strip()+'_'+col2+'.jpeg')
            col3 = 'Nouns'
            plot_hist(count_common_words(author_df, col3), 20, name.strip(), col3, root+out_path+name.strip()+'_'+col3+'.jpeg')
            col4 = 'Lemmas'
            plot_hist(count_common_words(author_df, col4), 20, name.strip(), col4, root+out_path+name.strip()+'_'+col4+'.jpeg')
            
            cc += 1
        #else:
        #    break
    
if __name__ == "__main__":
    main()
