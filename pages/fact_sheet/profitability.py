from dash import html, dcc

latest_year = 2024

def chart_container(chart_id, title, default_year):
    """
    Creates a container for a chart with a title and a Graph component.
    """
    return html.Div([
        html.H3(
            title, 
            style={
                'textAlign': 'center', 
                'margin': '5px 0',
                'backgroundColor': "#2C3E50",
                'padding': '10px',
                'color': "#ECF0F1"
            }
        ),
        dcc.Graph(id=chart_id)
    ], style={
        'border': '1px solid #CED2CC',
        'padding': '10px',
        'backgroundColor': '#FFFFFF',
        'borderRadius': '4px'
    })

layout = html.Div([
    html.H2("Chapter 1: Profitability Analysis"),
    html.P("This section covers profitability metrics."),
    # First row: Revenue chart, centered.
    html.Div(
        chart_container("chart1", "Revenue", default_year=latest_year),
        style={"textAlign": "center", "width": "100%"}
    ),
    # Second row: EBITDA and Cost charts side by side.
    html.Div([
        html.Div(
            chart_container("chart3", "EBITDA", default_year=latest_year),
            style={"width": "48%", "display": "inline-block", "verticalAlign": "top"}
        ),
        html.Div(
            chart_container("chart4", "Cost", default_year=latest_year),
            style={"width": "48%", "display": "inline-block", "verticalAlign": "top", "marginLeft": "4%"}
        )
    ], style={"marginTop": "20px"})
], style={"padding": "20px"})
