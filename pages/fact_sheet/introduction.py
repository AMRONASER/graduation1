# pages/fact_sheet/introduction.py

from dash import html, dash_table, callback, Input, Output
import pandas as pd

# Color definitions
Blue = "#2C3E50" 
WHITE = "#FFFFFF"
GREY = "#808080"
BLACK = "#000000"

layout = html.Div([
    html.H1("Welcome to Our Financial Story"),
    html.P("In this dashboard, we will explore the key financial metrics that drive our business. Navigate through the tabs to follow our narrative."),
    dash_table.DataTable(
        id="intro-table",
        columns=[],   # Populated by the callback
        data=[],      # Populated by the callback
        page_action="none",  # Display all rows on one page
        style_table={
            "overflowX": "auto",
            "border": f"2px solid {GREY}"  # Outer border
        },
        style_cell={
            "fontSize": "15px",       # Increased font size for table cells
            "textAlign": "center",
            "border": f"0.5px dotted {GREY}",  # Very thin dotted inner borders
            "padding": "6px"
        },
        style_header={
            "backgroundColor": Blue,
            "color": WHITE,
            "fontWeight": "bold",
            "textAlign": "center",
            "fontSize": "17px",
            "border": f"0.5px dotted {GREY}"  # Dotted borders for header cells too
        },
        style_data_conditional=[]
    )
], style={"padding": "20px", "backgroundColor": WHITE})

def format_number(x):
    """Format a number so that negatives appear in parentheses and commas separate thousands."""
    if isinstance(x, (int, float)) and pd.notna(x):
        # Remove decimals by rounding and converting to int
        num = int(round(x))
        if num < 0:
            return f"({format(abs(num), ',')})"
        else:
            return format(num, ',')
    return x

@callback(
    [Output("intro-table", "data"),
     Output("intro-table", "columns")],
    Input("results-store", "data")
)
def update_intro_table(results_data):
    if not results_data:
        return [], []

    # Load data and select the last 9 rows
    df = pd.read_json(results_data, orient="split")
    df_subset = df.tail(12)

    # Format numeric values: remove decimals, wrap negatives in parentheses, and insert commas
    df_subset = df_subset.applymap(format_number)

    # Transpose the DataFrame
    df_t = df_subset.T

    # Remove unwanted rows if present
    for label in ["Month Name", "Year", "Month"]:
        if label in df_t.index:
            df_t = df_t.drop(label)

    # Use "Year-Month" row as new column headers, then drop it
    if "Year-Month" in df_t.index:
        year_month_row = df_t.loc["Year-Month"].copy()
        df_t = df_t.drop("Year-Month")
        df_t.columns = year_month_row

    # Drop the second row (index = 1) in the transposed DataFrame if applicable
    if len(df_t) > 1:
        df_t.drop(df_t.index[0], inplace=True)

    # Reset index so that the row labels become a column
    df_t.reset_index(inplace=True)
    # Rename the new column (original index) to an empty string
    df_t.rename(columns={"index": ""}, inplace=True)

    data = df_t.to_dict("records")
    columns = [{"name": str(col), "id": str(col)} for col in df_t.columns]
    return data, columns
