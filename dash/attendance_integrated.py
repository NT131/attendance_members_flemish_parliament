import dash
from dash import html
from dash import dcc

import attendance_permanent_members_per_comm_integrated
import attendance_per_party_integrated
import attendance_per_member_integrated 


app = dash.Dash(__name__, assets_folder='assets') # Relative path to the folder of css file)
app.title = "Aanwezigheid in commissies waarvan parlementsleden vast lid zijn" # title of tab in browser

app.layout = html.Div([
    # Header section
    html.Div(
        children=[
            # Title
            html.H1(
                children="Aanwezigheid Vlaamse parlementsleden",
                className="header-title",
                style={"color": "#FFFFFF"}
            ),
            # Description
            html.P(
                children=(
                    "Het Vlaams Parlement geeft op haar website een overzicht van elke vergadering van elke commissie, en welke vertegenwoordigers hier aanwezig waren. Het Vlaams Parlement stelt deze gegevens ook beschikbaar via een API. Onderstaande visualisaties laten toe om met deze gegevens te interageren."
                    ),
                className="header-description",
                style={"color": "#FFFFFF"}
            ),
        ],
        className="section-header",
        style={"background-color": "#222222"} # Set dark background for this section
    ),
    dcc.Tabs([
        dcc.Tab(
            label='Aanwezigheid per commissie', 
            children=attendance_permanent_members_per_comm_integrated.layout),
        dcc.Tab(
            label='Aanwezigheid per partij', 
            children=attendance_per_party_integrated.layout),
        dcc.Tab(
            label='Aanwezigheid per parlementslid', 
            children=attendance_per_member_integrated.layout),
        ]
	),
	# Footer with hyperlink to GitHub
	html.Footer(["De code en data voor deze toepassing is beschikbaar op ",
				 html.A("GitHub", href="https://github.com/NT131/attendance_members_flemish_parliament")
				]
	),
])

  
    
# Register callbacks for each visualization
attendance_permanent_members_per_comm_integrated.register_callbacks(app)
attendance_per_party_integrated.register_callbacks(app)
attendance_per_member_integrated.register_callbacks(app) 



if __name__ == '__main__':
    app.run_server(debug=True)