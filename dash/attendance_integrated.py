import dash
from dash import html
from dash import dcc

import attendance_permanent_members_per_comm_integrated
import attendance_per_party_integrated
import attendance_per_member_integrated 


app = dash.Dash(__name__, assets_folder='assets') # Relative path to the folder of css file)
app.title = "Aanwezigheid in commissies waarvan parlementsleden vast lid zijn" # title of tab in browser

app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(
            label='Gemiddelde aanwezigheid vaste leden in commissie', 
            children=attendance_permanent_members_per_comm_integrated.layout),
        dcc.Tab(
            label='Aanwezigheid per partij', 
            children=attendance_per_party_integrated.layout),
        dcc.Tab(
            label='Aanwezigheid per parlementslid', 
            children=attendance_per_member_integrated.layout),
        ])
])

  
    
# Register callbacks for each visualization
attendance_permanent_members_per_comm_integrated.register_callbacks(app)
attendance_per_party_integrated.register_callbacks(app)
attendance_per_member_integrated.register_callbacks(app) 



if __name__ == '__main__':
    app.run_server(debug=True)