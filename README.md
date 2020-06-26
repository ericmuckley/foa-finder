# FOA Finder

This is an automated web scraper for finding funding opportunity announcements from grants.gov. Every day, the [grants.gov](https://www.grants.gov/) database is updated and exported to a zipped XML file which is avilabel for download [here](https://www.grants.gov/web/grants/xml-extract.html). This scraper downloads the latest database export, searches it for relevant keywords, and sends matches to a destination.


`pip install xmltodict`


