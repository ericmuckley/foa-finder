#!/Documents/Github/foa-finder/webenv/bin/python

# -*- coding: utf-8 -*-


"""

What this script does:
(1) finds the latest FOA database on grants.gov
(2) downloads the database
(3) unzips the database to an xml file
(4) converts the xml database into a pandas dataframe
(5) filters the FOA dataframe by keywords
(6) sends the filtered FOA list to a dedicated channel on Slack.

"""


import os
import glob
import json
import zipfile
import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup



# %%%%%%%%%%%%%%%%%%%% find the database %%%%%%%%%%%%%%%%%%%%%%%%%%


def get_xml_url_and_filename():
    """Get the URL and filename of the most recent XML database file
    posted on grants.gov."""

    day_to_try = datetime.today()
    
    file_found = None
    while file_found is None:
        url = 'https://www.grants.gov/extract/GrantsDBExtract{}v2.zip'.format(
            day_to_try.strftime('%Y%m%d'))
        response = requests.get(url, stream=True)
        
        # look back in time if todays data is not posted yet
        if response.status_code == 200:
            file_found = url
        else:
            day_to_try = day_to_try - timedelta(days=1)

        filename = 'GrantsDBExtract{}v2.zip'.format(
            day_to_try.strftime('%Y%m%d'))
    return url, filename



# get url and filename of the latest database available for extraction
url, filename = get_xml_url_and_filename()





# %%%%%%%%%%%%%%%%%%%% download the database %%%%%%%%%%%%%%%%%%%%%%%%%%


def download_file_from_url(url, filename):
    """Download a file from a URL"""
    response = requests.get(url, stream=True)
    # if file url is found
    if response.status_code == 200:
        handle = open(filename, "wb")
        for chunk in response.iter_content(chunk_size=512):
            if chunk:  # filter out keep-alive new chunks
                handle.write(chunk)
        handle.close()
    # if file url is not found
    else:
        print('URL does not exist')



# remove all previously-downloaded zip files
[os.remove(f) for f in os.listdir() if f.endswith(".zip")]

# download the database zip file
download_file_from_url(url, filename)






# %%%%%%%%%%%%%%%%%%%%%%%%% unzip and parse file %%%%%%%%%%%%%%%%%%%%%


def unzip_and_soupify():
    """Unzip a zip file and parse it using beautiful soup"""
    # set name of directory to unzip to
    unzipped_dirname = 'unzipped'
    
    # remove all previously-unzipped files
    [os.remove(f) for f in os.listdir(unzipped_dirname) if f.endswith(".zip")]
    
    # unzip raw file
    with zipfile.ZipFile(filename, 'r') as z:
        z.extractall(unzipped_dirname)
    
    # get path of file in unzipped folder
    unzipped_filepath = glob.glob(unzipped_dirname+'/*')[0]
    
    # parse as tree and convert to string
    tree = ET.parse(unzipped_filepath)
    root = tree.getroot()
    doc = str(ET.tostring(root, encoding='unicode', method='xml'))
    # initialize beautiful soup object
    soup = BeautifulSoup(doc, 'lxml')   
    return soup



# get beautiful soup object from parsed zip file
soup = unzip_and_soupify()







# %%%%%%%%%%%%%% convert xml to pandas dataframe %%%%%%%%%%%%%%%%%%%%



def df_from_soup(soup):
    """Generate a pandas dataframe from a beautiful-soup xml object"""
    # find all tags present in the xml
    #tags = np.unique([tag.name for tag in soup.find_all()])
    # extract info from title and ID tags
    titles = [i.text.strip().lower() for i in soup.find_all('ns0:opportunitytitle')]
    ids = [i.text.strip() for i in soup.find_all('ns0:opportunitynumber')]
    #descriptions = [i.text.strip() for i in soup.find_all('ns0:opportuitydescription')]
    df = pd.DataFrame(columns=['title', 'num'],
                      data=np.column_stack((titles, ids)))
    return df


def filter_df(df):
    """Filter the dataframe by keywords and nonkeywords (words to avoid).
    The keywords and nonkeywords are set in external csv files called
    'keywords.csv' and 'nonkeywords.csv'"""
    # get keywords to filter dataframe
    keywords = list(pd.read_csv('keywords.csv', header=None)[0])
    keywords_str = '|'.join(keywords).lower()
    # get non-keywords to avoid
    nonkeywords = list(pd.read_csv('nonkeywords.csv', header=None)[0])
    nonkeywords_str = '|'.join(nonkeywords).lower()
    # filter dataframe by keywords and nonkeywords
    df = df[df['title'].str.contains(keywords_str, na=False)]
    df = df[~df['title'].str.contains(nonkeywords_str, na=False)]
    return df


# get full dataframe from database
df_full = df_from_soup(soup)

# get dataframe filtered by keywords
df = filter_df(df_full)








# %%%%%%%%%%%%%%% format string message for Slack %%%%%%%%%%%%%%%%%%%%%%


def create_slack_text(print_text=True):
    """Create text to send into Slack"""
    # get database date
    db_date = filename.split('GrantsDBExtract')[1].split('v2')[0]
    db_date = db_date[:4]+'-'+db_date[4:6]+'-'+db_date[6:]
    # create text
    slack_text = 'Funding announcements from grants.gov, extracted {}:'.format(
        db_date)
    slack_text += '\n======================================='
    # loop over each FOA title and add to text
    for i in range(len(df)):
        slack_text += '\n{}) {} ({})'.format(
            i+1, df['title'].iloc[i].upper(), df['num'].iloc[i])
    slack_text += '\n======================================='
    slack_text += '\nShowing {} of {} FOAs pulled from grants.gov on {}, using keywords in {}'.format(
        len(df), len(df_full), db_date, 'https://github.com/ericmuckley/foa-finder/blob/master/keywords.csv.')
    slack_text += '\nTo view FOA details, go to https://www.grants.gov/web/grants/search-grants.html'
    slack_text += ' and search by "Opportunity Number". Opportunity numbers are shown in parenthesis after each FOA title in the above list.'
    if print_text:
        print(slack_text)
    return slack_text
        
    
slack_text = create_slack_text(print_text=True)






# %%%%%%%%%%%%%%%%%%%%% send message in slack %%%%%%%%%%%%%%%%%%%%%%%%

send_to_slack = False
if send_to_slack:
    
    slack_text = 'testing multi-line message: \n line 1 \n line 2'

    try:
        response = requests.post(
            os.environ['SLACK_WEBHOOK_URL'],
            data=json.dumps({'text': slack_text}),
            headers={'Content-Type': 'application/json'})
        print('Slack response: ' + str(response.text))
    except:
        print('Connection to Slack could not be established.')
    

