# FOA Finder

This is an automated web scraper for finding funding opportunity announcements from grants.gov. Every day, the [grants.gov](https://www.grants.gov/) database is updated and exported to a zipped XML file which is avilable for download [here](https://www.grants.gov/web/grants/xml-extract.html). This scraper downloads the latest database export, searches it for relevant keywords, and sends matches to a destination.

[Information about the format of the XML file](https://www.grants.gov/help/html/help/index.htm?rhcsh=1&callingApp=custom#t=XMLExtract%2FXMLExtract.htm)

`pip install xmltodict`

`pip install beautifulsoup4`

