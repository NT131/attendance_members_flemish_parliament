# Attendance of members of the Flemish Parliament 2019-2024
This repository holds code to set up a Dash application to dynamically assess the attendance of members of parliament of the Flemisch Parliament.
It uses the data as available on the[website of the Flemish Parliament](https://www.vlaamsparlement.be) as well as through the dedicated [API](http://ws.vlpar.be/e/opendata/api).

Initial data extraction from the Parliament's API was done using a Jupyter Notebook script (see `code` folder). The resulting data is stored in the `data` folder. However, a `.py` script was rendered of this extraction script to allow extraction outside of a Notebook environment. 

Data exploratin and initial graph building was performed in a Jupyter Notebook (see `code` folder). 
The eventual implementation is available in .py files in the `dash` folder.

The data can be updated through the update script located at `code/vlaams_parlement_API_update_data.py`.

A working version of the application is available at a [dedicated website](http://erpohk.ddns.net/visualisaties/aanwezigheid-vlaams-parlement/). A cron job is set up to run the update script every Sunday with regard to this application.
 

