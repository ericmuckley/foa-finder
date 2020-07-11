#!/Users/emuckley/Documents/Github/foa-finder/webenv/bin/python

# -*- coding: utf-8 -*-


"""

What this script does:
(1) finds the latest FOA database on grants.gov
(2) downloads the database
(3) unzips the database to an xml file
(4) converts the xml database into a pandas dataframe
(5) filters the FOA dataframe by keywords
(6) sends the filtered FOA list to a dedicated channel on Slack.

python version to use for crontab scheduling in virtual environment:
Users/emuckley/Documents/GitHub/foa-finder/webenv/bin/python


crontab script to run every 24 hours at 18:05 hrs:
5 18 * * * /Users/emuckley/Documents/GitHub/foa-finder/app.py >> ~/cron.log 2>&1


"""


import os
import json
import time
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
    
    print('Found database file {}'.format(filename))
    
    return url, filename



# get url and filename of the latest database available for extraction
url, filename = get_xml_url_and_filename()





# %%%%%%%%%%%%%%%%%%%% download the database %%%%%%%%%%%%%%%%%%%%%%%%%%


def download_file_from_url(url, filename):
    """Download a file from a URL"""
    # remove all previously-downloaded zip files
    [os.remove(f) for f in os.listdir() if f.endswith(".zip")]
    # ping the dataset url
    response = requests.get(url, stream=True)
    # if file url is found
    if response.status_code == 200:
        handle = open(filename, "wb")
        for chunk in response.iter_content(chunk_size=512):
            if chunk:  # filter out keep-alive new chunks
                handle.write(chunk)
        handle.close()
        time.sleep(3)
        print('Database successfully downloaded')
    # if file url is not found
    else:
        print('URL does not exist')





# download the database zip file
download_file_from_url(url, filename)




# %%%%%%%%%%%%%%%%%%%%%%%%% unzip and parse file %%%%%%%%%%%%%%%%%%%%%


def unzip_and_soupify(filename, unzipped_dirname='unzipped'):
    """Unzip a zip file and parse it using beautiful soup"""

    # remove all previously-downloaded zip files
    for f in os.listdir(unzipped_dirname):
        os.remove(os.path.join(unzipped_dirname, f))
    
    # unzip raw file
    with zipfile.ZipFile(filename, "r") as z:
        z.extractall(unzipped_dirname)
    
    # get path of file in unzipped folder
    unzipped_filepath = os.path.join(
        unzipped_dirname,
        os.listdir(unzipped_dirname)[0])
    
    print('Unzipping {}'.format(unzipped_filepath))
    
    # parse as tree and convert to string
    tree = ET.parse(unzipped_filepath)
    root = tree.getroot()
    doc = str(ET.tostring(root, encoding='unicode', method='xml'))
    # initialize beautiful soup object
    soup = BeautifulSoup(doc, 'lxml')  
    print('Database unzipped')
    
    return soup



# get beautiful soup object from parsed zip file
soup = unzip_and_soupify(filename)







# %%%%%%%%%%%%%% convert xml to pandas dataframe %%%%%%%%%%%%%%%%%%%%



def df_from_soup(soup):
    """Generate a pandas dataframe from a beautiful-soup xml object"""
    # extract info from title and ID tags
    titles = [i.text.strip().lower() for i in soup.find_all('ns0:opportunitytitle')]
    ids = [i.text.strip() for i in soup.find_all('ns0:opportunitynumber')]
    postdates = [i.text.strip() for i in soup.find_all('ns0:postdate')]

    postdates = [pd[:2]+'-'+pd[2:4]+'-'+pd[4:] for pd in postdates]

    df = pd.DataFrame(columns=['title', 'num', 'postdate'],
                      data=np.column_stack((titles, ids, postdates)))
    
    print('Created dataframe from database')
    
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
    
    # filter by post date - the current year and previous year only
    curr_yr = np.max([int(i[-4:]) for i in df['postdate'].values])
    #prev_yr = curr_yr - 1
    df = df[df['postdate'].str.contains('-'+str(curr_yr), na=False)]
    
    # filter dataframe by keywords and nonkeywords
    df = df[df['title'].str.contains(keywords_str, na=False)]
    df = df[~df['title'].str.contains(nonkeywords_str, na=False)]
    
    print('Database filtered by keywords')
    
    return df





# get full dataframe from database
#df_full = df_from_soup(soup)


# get dataframe filtered by keywords
#df = filter_df(df_full)





# %%


"""
# example entry from the database:

<OpportunitySynopsisDetail_1_0>
    <OpportunityID>131073</OpportunityID>
    <OpportunityTitle>Cooperative Ecosystem Studies Unit, Piedmont South Atlantic Coast CESU</OpportunityTitle>
    <OpportunityNumber>G12AS20003</OpportunityNumber>
    <OpportunityCategory>D</OpportunityCategory>
    <FundingInstrumentType>CA</FundingInstrumentType>
    <CategoryOfFundingActivity>ST</CategoryOfFundingActivity>
    <CFDANumbers>15.808</CFDANumbers>
    <EligibleApplicants>25</EligibleApplicants>
    <AdditionalInformationOnEligibility>This financial assistance opportunity is being issued under a Cooperative Ecosystem Studies Unit (CESU) Program.  CESUs are partnerships that provide research, technical assistance, and education.  This assistance is provided through a CESU cooperative agreement, which is neither a contract nor a grant.  Eligible recipients must be a participating partner of the Piedmont - South Atlantic Coast CESU Program.</AdditionalInformationOnEligibility>
    <AgencyCode>DOI-USGS1</AgencyCode>
    <AgencyName>Geological Survey</AgencyName>
    <PostDate>11172011</PostDate>
    <CloseDate>11292011</CloseDate>
    <LastUpdatedDate>11282011</LastUpdatedDate>
    <AwardCeiling>0</AwardCeiling>
    <AwardFloor>0</AwardFloor>
    <EstimatedTotalProgramFunding>31900</EstimatedTotalProgramFunding>
    <ExpectedNumberOfAwards>1</ExpectedNumberOfAwards>
    <Description>The USGS Southeast Ecological Science Center seeks to provide financial assistance for research investigating the use of fish otoliths to identify prime nursery areas for common snook and red drum in Tampa Bay Florida.</Description>
    <Version>Synopsis 2</Version>
    <CostSharingOrMatchingRequirement>No</CostSharingOrMatchingRequirement>
    <ArchiveDate>12172011</ArchiveDate>
    <AdditionalInformationURL>http://www.grants.gov/</AdditionalInformationURL>
    <AdditionalInformationText>http://www.grants.gov/ </AdditionalInformationText>
    <GrantorContactEmail>fgraves@usgs.gov</GrantorContactEmail>
    <GrantorContactEmailDescription>fgraves@usgs.gov</GrantorContactEmailDescription>
    <GrantorContactText>Faith Graves, 703-648-7356&amp;lt;br/&amp;gt;fgraves@usgs.gov&amp;lt;br/&amp;gt;</GrantorContactText>
</OpportunitySynopsisDetail_1_0>

"""








def preview_tags(soup):
    """Preview the tags present in a beautiful-soup object"""
    tags = np.unique([tag.name for tag in soup.find_all()])
    
    """
    array(['body', 'html', 'ns0:additionalinformationoneligibility',
       'ns0:additionalinformationtext', 'ns0:additionalinformationurl',
       'ns0:agencycode', 'ns0:agencyname', 'ns0:archivedate',
       'ns0:awardceiling', 'ns0:awardfloor', 'ns0:categoryexplanation',
       'ns0:categoryoffundingactivity', 'ns0:cfdanumbers',
       'ns0:closedate', 'ns0:closedateexplanation',
       'ns0:costsharingormatchingrequirement', 'ns0:description',
       'ns0:eligibleapplicants', 'ns0:estimatedawarddate',
       'ns0:estimatedprojectstartdate', 'ns0:estimatedsynopsisclosedate',
       'ns0:estimatedsynopsisclosedateexplanation',
       'ns0:estimatedsynopsispostdate',
       'ns0:estimatedtotalprogramfunding', 'ns0:expectednumberofawards',
       'ns0:fiscalyear', 'ns0:fundinginstrumenttype',
       'ns0:grantorcontactemail', 'ns0:grantorcontactemaildescription',
       'ns0:grantorcontactname', 'ns0:grantorcontactphonenumber',
       'ns0:grantorcontacttext', 'ns0:grants', 'ns0:lastupdateddate',
       'ns0:opportunitycategory', 'ns0:opportunitycategoryexplanation',
       'ns0:opportunityforecastdetail_1_0', 'ns0:opportunityid',
       'ns0:opportunitynumber', 'ns0:opportunitysynopsisdetail_1_0',
       'ns0:opportunitytitle', 'ns0:postdate', 'ns0:version'],
      dtype='<U41')
    """
    
    for t in tags:
        print(t)
        #if 'ns0:' in t:
        #    print('{} entries: {}'.format(t.split('ns0:')[1], len(soup(t))))
            
    #    print([i.text.strip().lower() for i in soup.find_all(t)][:5])



#preview_tags(soup)

# %% populate dataframe with every entry tag



def soup_to_df(soup):
    """Convert beautifulsoup object from grants.gov XML into dataframe"""
    # list of bs4 FOA objects
    s = 'opportunitysynopsisdetail'
    foa_objs = [tag for tag in soup.find_all() if s in tag.name.lower()]

    # loop over each FOA in the database and save its details as a dictionary
    dic = {}
    for i, foa in enumerate(foa_objs):
        ch = foa.findChildren()
        dic[i] = {fd.name.split('ns0:')[1]:fd.text for fd in ch}

    # create dataframe from dictionary
    df = pd.DataFrame.from_dict(dic, orient='index')
    return df


df_full = soup_to_df(soup)


df = df_full[df_full['lastupdateddate'].str.endswith('2020')]


# get name and text from each child tag
#foa_details[0].name
#foa_details[0].text




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
        slack_text += '\n{}) {} {} ({})'.format(
            i+1,
            df['postdate'].iloc[i],
            df['title'].iloc[i].upper(),
            df['num'].iloc[i])
    slack_text += '\n======================================='
    slack_text += '\nShowing {} of {} FOAs pulled from grants.gov on {}, with their posted dates, using keywords in {}'.format(
        len(df), len(df_full), db_date, 'https://github.com/ericmuckley/foa-finder/blob/master/keywords.csv.')
    slack_text += '\nTo view FOA details, go to https://www.grants.gov/web/grants/search-grants.html'
    slack_text += ' and search by "Opportunity Number". Opportunity numbers are shown in parenthesis after each FOA title in the above list. If the FOA cannot be found, then it has already been closed.'
    if print_text:
        print(slack_text)
    else:
        print('Slack text generated')
    return slack_text



    
slack_text = create_slack_text()






# %%%%%%%%%%%%%%%%%%%%% send message in slack %%%%%%%%%%%%%%%%%%%%%%%%

send_to_slack = False
if send_to_slack:

    print('sending results to slack')
    
    try:
        response = requests.post(
            os.environ['SLACK_WEBHOOK_URL'],
            data=json.dumps({'text': slack_text}),
            headers={'Content-Type': 'application/json'})
        print('Slack response: ' + str(response.text))
    except:
        print('Connection to Slack could not be established.')
    

