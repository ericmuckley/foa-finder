# FOA Finder

This is an automated web scraper for finding funding opportunity announcements from grants.gov. Every day, the [grants.gov](https://www.grants.gov/) database is updated and exported to a zipped XML file which is available for download [here](https://www.grants.gov/web/grants/xml-extract.html). This scraper downloads the latest database export, searches it for relevant keywords, and sends matches to a dedicated Slack channel.

[Information about the format of the XML file](https://www.grants.gov/help/html/help/index.htm?rhcsh=1&callingApp=custom#t=XMLExtract%2FXMLExtract.htm)



## File description

* **app.py**: Main Python application
* **keywords.csv**: keywords to use for searching FOA titles
* **nonkeywords.csv**: keywords to avoid for searching FOA titles
* **requirements.txt**: Requirements file for installing app dependencies with pip



## Setting environment variables

Environment variables are required for connecting to the Slack API. To edit environment variables on macOS: `touch ~/.bash_profile; open ~/.bash_profile`

Add the line `export VAR_NAME="VAR_VALUE"`, where `VAR_NAME` and `VAR_VALUE` are the name and value of the variable.



## Running the scraper on a schedule using crontab

Install using `pip install crontab`



Make the python script executable using `chmod +x app.py`

Use shebang line in the python script (#!/usr/bin/python3, or for venv for example: #!/Users/emuckley/Documents/Github/foa-finder/webenv/bin/python) to direct to Python exe

Open scheduler using `crontab -e`. Paste the cron scheduler line. Type `:x` to save and exit scheduler. The scheduler line should look something like this for repeating at the start of the hour (0) every 24 hours:
`0 */24 * * * /path/to/script/app.py >> ~/cron.log 2>&1`



## Setup for development

Install / upgrade pip: `python3 -m pip install --user --upgrade pip`

Test pip version: `python3 -m pip --version`

Install virtualenv: `python3 -m pip install --user virtualenv`

To create a virtual environment, navigate to the project folder and run: `python3 -m venv <env>`, where `<env>` is the name of your new virtual environment.

Before installing packages inside the virtual environment, activate the environment: `source <env>/bin/activate`, where `<env>` is the name of your virtual environment.

To deactivate the environment: `deactivate`

Once the environment is activated, use pip to install libraries in it.

To export the list of installed packages as a `requirements.txt` file: `pip freeze > requirements.txt`

To install packages from the requirements file: `pip install -r requirements.txt`

