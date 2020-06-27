
import glob
import zipfile
import numpy as np
import pandas as pd
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

from datetime import datetime

import requests

# %%%%%%%%%%%%%%%%%%%% downlaod the xml file %%%%%%%%%%%%%%%%%%%%%%%%%%


today = datetime.today().strftime('%Y%m%d')
today = '20200626'
url = 'https://www.grants.gov/extract/GrantsDBExtract{}v2.zip'.format(today)

#downloaded_zip = requests.get(url)


#url = 'https://www2.census.gov/geo/tiger/GENZ2017/shp/cb_2017_02_tract_500k.zip'
target_path = 'GrantsDBExtract{}v2.zip'.format(today)

response = requests.get(url, stream=True)


# if file url is found
if response.status_code == 200:
    handle = open(target_path, "wb")
    for chunk in response.iter_content(chunk_size=512):
        if chunk:  # filter out keep-alive new chunks
            handle.write(chunk)
    handle.close()
# if file url is not found
else:
    print('URL does not exist')


#%%


# %%%%%%%%%%%%%%%%%%%%%%%%% parse xml file %%%%%%%%%%%%%%%%%%%%%%%%%%

# set name of zip folder
target_path = 'GrantsDBExtract20200626v2.zip'


# set name of directory to unzip to
unzipped_dirname = 'unzipped'

# unzip raw file
with zipfile.ZipFile(zip_dir, 'r') as z:
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

titles = [i.text.strip().lower for i in soup.find_all('ns0:opportunitytitle')]
ids = [i.text.strip() for i in soup.find_all('ns0:opportunityid')]
#descriptions = [i.text.strip() for i in soup.find_all('ns0:opportuitydescription')]

df_full = pd.DataFrame(columns=['title', 'id'],
                  data=np.column_stack((titles, ids)))


# get keywords to filter dataframe
keywords = list(pd.read_csv('keywords.csv').columns)
keyword_str = '|'.join(keywords).lower()

df = df_full[df_full['title'].str.contains('keyword1|keyword2', na=False)]

print(df)


