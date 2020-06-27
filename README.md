# FOA Finder

This is an automated web scraper for finding funding opportunity announcements from grants.gov. Every day, the [grants.gov](https://www.grants.gov/) database is updated and exported to a zipped XML file which is avilable for download [here](https://www.grants.gov/web/grants/xml-extract.html). This scraper downloads the latest database export, searches it for relevant keywords, and sends matches to a destination.

[Information about the format of the XML file](https://www.grants.gov/help/html/help/index.htm?rhcsh=1&callingApp=custom#t=XMLExtract%2FXMLExtract.htm)

`pip install xmltodict`

`pip install beautifulsoup4`

`pip install lxml`




## Setting environment variables

On macOS: `touch ~/.bash_profile; open ~/.bash_profile`

Add the line `export VAR_NAME="VAR_VALUE"`, where `VAR_NAME` and `VAR_VALUE` are the name and value of the variable.





## Testing locally

To test locally: `python app.py`. This will open the Dash page at the localhost: `http://127.0.0.1:8050/`

To stop running the application, use `ctrl + c`


## File description

* **app.py**: Main Python file which creates the application
* **requirements.txt**: Requirements file for installing app dependencies with pip. This is also used by the application host
* **Procfile**: file which Heroku uses to launch app


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



## Free web hosting on Heroku

Before deploying to the web, make sure that the app is not configured in `debug` mode. This is done by setting the line `app.run_server(debug=False)` in `app.py`.

To host the application on the web using Heroku, first put it in a Github repository. Then follow these steps:

* Setup account on Heroku
* Create a new app in Heroku
* Open your new app and go to **Deploy**
* Choose Github as the deployment method, and connect to your Github repository
* Scroll to the bottom of the page and click **Deploy now** under the **Manual deploy** section
* To make changes, edit your files in the Github repo, then re-deploy on Heroku
