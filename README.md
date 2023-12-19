# attendance_members_flemish_parliament
This repository holds code to set up a Dash application to dynamically assess the attendance of members of parliament of the Flemish parliament.

Initial data extraction from the Parliament's API (https://ws.vlpar.be/e/opendata/api/) was done using a Jupyter Notebook script (see `code` folder). The resulting data was moved to the `data` folder. However, a .py script was rendered of this extraction script to allow extraction outside of Notebook environment. 

Further data modification and graph building was tried out in Jupyter Notebook, but implemented in .py files under the `dash` folder.

The application is hosted at http://nielstack.eu.pythonanywhere.com/. The required WSGI file is located at the `flask` folder. 
