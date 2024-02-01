import dash
from dash import html
from dash import dcc

import attendance_permanent_members_per_comm_integrated
import attendance_per_party_integrated
import attendance_per_member_integrated 
import written_questions


app = dash.Dash(__name__, 
		url_base_pathname='/visualisaties/aanwezigheid-vlaams-parlement/',
		assets_folder='assets') # Relative path to the folder of css file)
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
                children=[
                    "Het Vlaams Parlement geeft op haar ",
                    html.A("website", href="https://www.vlaamsparlement.be/nl/parlementair-werk/plenaire-vergadering/vergaderingen", target="_blank"),
                    " een overzicht van elke vergadering van elke commissie, en welke vertegenwoordigers hier aanwezig waren. Ook de schriftelijke vragen zijn beschikbaar. Het Vlaams Parlement stelt deze gegevens ook beschikbaar via een ",
                    html.A("API", href="https://ws.vlpar.be/e/opendata/api/", target="_blank"),
                    ". Onderstaande visualisaties laten toe om met deze gegevens te interageren."
                ],
                className="header-description",
                style={"color": "#FFFFFF"}
            )
        ],
        className="section-header",
        style={"background-color": "#222222"} # Set dark background for this section
    ),
    dcc.Tabs([
        dcc.Tab(
            label='Aanwezigheid',
            children=[
                dcc.Tabs(
                    children=[
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
                ],
            ),
        dcc.Tab(
            label='Vragen',
            children=[
                dcc.Tabs(
                    children=[
                        # dcc.Tab(
                        #     label='Mondelinge vragen',
                        #     children = []),
                        dcc.Tab(
                            label='Schriftelijke vragen', 
                            children=written_questions.layout),
                        ]
                    ),
                ],
            ),
        ]
	),
    
#     dcc.Tabs([
#         dcc.Tab(
#             label='Aanwezigheid per commissie', 
#             children=attendance_permanent_members_per_comm_integrated.layout),
#         dcc.Tab(
#             label='Aanwezigheid per partij', 
#             children=attendance_per_party_integrated.layout),
#         dcc.Tab(
#             label='Aanwezigheid per parlementslid', 
#             children=attendance_per_member_integrated.layout),
#         dcc.Tab(
#             label='Schriftelijke vragen', 
#             children=written_questions.layout),
#         ]
# 	),
	# Footer with hyperlink to GitHub
	html.Footer(
		className='footer', # Assign a class name for styling
		children=[
			"De code en data voor deze toepassing is beschikbaar op ",
			html.A("GitHub", href="https://github.com/NT131/attendance_members_flemish_parliament")
		]
	),
])

  
    
# Register callbacks for each visualization
attendance_permanent_members_per_comm_integrated.register_callbacks(app)
attendance_per_party_integrated.register_callbacks(app)
attendance_per_member_integrated.register_callbacks(app) 
written_questions.register_callbacks(app)


# Define a callable application object for Gunicorn
application = app.server


# Run app
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=5002)
