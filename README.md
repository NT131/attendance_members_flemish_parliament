# attendance_members_flemish_parliament
This repository holds code to set up a Dash application to dynamically assess the attendance of members of parliament of the Flemisch parliament.
It uses the data as available on the website of the Flemish Parliament (https://www.vlaamsparlement.be) as well as through the dedicated API (http://ws.vlpar.be/e/opendata/api).

Initial data extraction from the Parliament's API (https://ws.vlpar.be/e/opendata/api/) was done using a Jupyter Notebook script (see `code` folder). The resulting data was moved to the `data` folder. However, a .py script was rendered of this extraction script to allow extraction outside of Notebook environment. 

Further data modification and graph building was tried out in Jupyter Notebook, but implemented in .py files under the `dash` folder.

The data can be updated through the update script located at "code/vlaams_parlement_API_update_data.py".

A working version of the application is available at http://erpohk.ddns.net/visualisaties/aanwezigheid-vlaams-parlement/. A cron job is set up to run the update script every Sunday with regard to this application. 

