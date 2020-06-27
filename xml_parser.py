
import xmltodict

import glob

import zipfile

import xml
import xml.etree.ElementTree as ET


from bs4 import BeautifulSoup




# set name of zip folder
zip_dir = 'GrantsDBExtract20200626v2.zip'
# set name of directort to unzip to
unzipped_dirname = 'unzipped'


# unzip raw file
with zipfile.ZipFile(zip_dir, 'r') as z:
    z.extractall(unzipped_dirname)


# get path of file in unzipped folder
unzipped_filepath = glob.glob(unzipped_dirname+'/*')[0]



'''
# read unzipped file
with open(unzipped_filepath) as z:
    doc = xmltodict.parse(z.read())
'''

# parse as tree and convert to string
tree = ET.parse(unzipped_filepath)
root = tree.getroot()
doc = str(ET.tostring(root, encoding='unicode', method='xml'))





soup = BeautifulSoup(doc, 'lxml')   

# %%

titles = []
counter = 0


[str(tag) for tag in soup.find_all()]


'''

for entry in soup.findAll('Grants'):#"OpportunitySynopsisDetail_1_0"):
    op_id = entry.find('OpportunityID').text.strip()
    titles.append(entry.find('OpportunityTitle').text.strip())
    counter += 1

    title = entry.find("title").text.strip()
    author = entry.find("author").text.strip()
    link  = entry.find("link").text.strip()
    summary = entry.find("summary").text.strip()
'''





# %%



# %%

print('Root tag: {}'.format(root.tag))

print('Root attribute: {}'.format(root.attrib))


#for child in root:
#    print(child.tag, child.attrib)


# %%

#xmlraw = xmltodict.parse(unzipped_filepath)


#child_tags = xml_raw['parent_tag'].keys()


'''
print(list(doc))

print(list(doc['Grants']))


for a in doc['Grants']:
    print(len(list(doc['Grants'][a])))

'''