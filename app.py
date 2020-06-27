# -*- coding: utf-8 -*-

import glob
import zipfile
import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

import dash
import dash_html_components as html



# %%%%%%%%%%%%%%%%%%%% download the xml file %%%%%%%%%%%%%%%%%%%%%%%%%%


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
    


url, filename = get_xml_url_and_filename()


# %% 


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




# %%%%%%%%%%%%%%%%%%%%%%%%% parse xml file %%%%%%%%%%%%%%%%%%%%%%%%%%

# set name of zip folder
target_path = 'GrantsDBExtract20200626v2.zip'


# set name of directory to unzip to
unzipped_dirname = 'unzipped'

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

# %%%%%%%%%%%%%% convert xml to pandas dataframe %%%%%%%%%%%%%%%%%%%%

# find all tags present in the xml
#tags = np.unique([tag.name for tag in soup.find_all()])

titles = [i.text.strip().lower() for i in soup.find_all('ns0:opportunitytitle')]
ids = [i.text.strip() for i in soup.find_all('ns0:opportunityid')]
#descriptions = [i.text.strip() for i in soup.find_all('ns0:opportuitydescription')]

df_full = pd.DataFrame(columns=['title', 'id'],
                  data=np.column_stack((titles, ids)))


# get keywords to filter dataframe
keywords = list(pd.read_csv('keywords.csv').columns)
keyword_str = '|'.join(keywords).lower()

df = df_full[df_full['title'].str.contains(keyword_str, na=False)]

keyword_titles = list(df['title'])
print(keyword_titles)



# %%%%%%%%%%%%%%%%%%%% create kanding page for app %%%%%%%%%%%%%%%%%%%%%
# title for the browser page tab
TITLE = 'FOA finder'
app = dash.Dash(__name__)
app.title = TITLE
server = app.server  # this line is required for web hosting
start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')



# create html paragraph listing all matching titles
titles_html = [html.B('Matching titles:'), html.Br()]
for kt in keyword_titles:
   titles_html.append(str(kt))
   titles_html.append(html.Br())


# create app layout - this is shown at foa-finder.herokuapp.com
app.layout = html.Div([
    
    html.H1(children=TITLE),
    
    html.P([
        html.B('App loaded: '), str(start_time), html.Br(),
        html.B('Newest available database: '), str(filename), html.Br()
        ]),
    
    html.Hr(),

    html.P(titles_html)
    
    ])

if __name__ == '__main__':
    app.run_server(debug=False)