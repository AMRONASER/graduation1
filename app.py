import os
import pandas as pd
import pickle
from dash import html, dcc, Input, Output, Dash
import plotly.graph_objects as go

# -------------------------------
# Load the saved AI model, scaler, and label encoder
# -------------------------------
model_filename = 'AI/best_model.pkl'
with open(model_filename, 'rb') as file:
    model_data = pickle.load(file)

best_model = model_data['model']
scaler = model_data['scaler']
label_encoder = model_data['label_encoder']

# -------------------------------
# Create the Dash app instance
# -------------------------------
app = Dash(__name__, suppress_callback_exceptions=True)

# --- Coherent Color Palette ---
PRIMARY_COLOR   = "#2C3E50"  # Dark blue (header background)
SECONDARY_COLOR = "#ECF0F1"  # Light grey (dropdown background)
ACCENT_COLOR    = "#3498DB"  # Blue accent (controls area)
TEXT_COLOR      = "#2C3E50"  # Dark blue text
PAGE_BG         = "#F7F9FA"  # Very light grey (page background)

# --- Dummy Preprocessing Function ---
def preprocess_year_month_columns(df):
    # (Insert any needed preprocessing here)
    return df

# --- DATA CONFIGURATION ---
DATA_FOLDER = "database"
company_files = [f for f in os.listdir(DATA_FOLDER) if f.lower().endswith((".xlsx", ".csv"))]
company_files.sort()

if company_files:
    default_file = os.path.join(DATA_FOLDER, company_files[0])
    # Adjust reader based on file extension
    if default_file.lower().endswith(".xlsx"):
        results_df = pd.read_excel(default_file)
    else:
        results_df = pd.read_csv(default_file)
    results_df = preprocess_year_month_columns(results_df)
else:
    results_df = pd.DataFrame()

# --- HEADER (Company dropdown and view controls) ---
header = html.Div(
    [
        # Logo container
        html.Div(
            html.Img(src="/assets/logo.jpg", style={"maxWidth": "200px"}),
            style={"flex": "1"}
        ),
        # Controls container: Company, view mode, period
        html.Div(
            [
                dcc.Dropdown(
                    id="company-dropdown",
                    options=[{"label": os.path.splitext(f)[0], "value": f} for f in company_files],
                    value=company_files[0] if company_files else None,
                    clearable=False,
                    style={
                        "width": "180px",
                        "marginRight": "10px",
                        "border": "none",
                        "borderRadius": "4px",
                        "boxShadow": "none",
                        "outline": "none",
                        "color": TEXT_COLOR,
                        "backgroundColor": SECONDARY_COLOR,
                    }
                ),
                dcc.Dropdown(
                    id="global-view-mode",
                    options=[
                        {"label": "YTD", "value": "YTD"},
                        {"label": "YOY", "value": "YOY"},
                        {"label": "Monthly", "value": "yearly"}
                    ],
                    value="YTD",
                    clearable=False,
                    style={
                        "width": "150px",
                        "marginRight": "10px",
                        "border": "none",
                        "borderRadius": "4px",
                        "boxShadow": "none",
                        "outline": "none",
                        "color": TEXT_COLOR,
                        "backgroundColor": SECONDARY_COLOR,
                    }
                ),
                dcc.Dropdown(
                    id="global-period",
                    clearable=False,
                    style={
                        "width": "150px",
                        "marginRight": "10px",
                        "border": "none",
                        "borderRadius": "4px",
                        "boxShadow": "none",
                        "outline": "none",
                        "color": TEXT_COLOR,
                        "backgroundColor": SECONDARY_COLOR,
                    }
                )
            ],
            style={
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "flex-end",
                "gap": "10px",
                "backgroundColor": ACCENT_COLOR,
                "padding": "5px"
            }
        )
    ],
    style={
        "display": "flex",
        "alignItems": "center",
        "padding": "10px",
        "backgroundColor": PRIMARY_COLOR
    }
)

# --- Add a Div for the AI recommendation pop-up message ---
ai_recommendation_div = html.Div(
    id="ai-recommendation",
    style={
        'margin': '20px',
        'padding': '10px',
        'backgroundColor': SECONDARY_COLOR,
        'color': TEXT_COLOR,
        'border': '1px solid #ccc',
        'borderRadius': '4px',
        'fontWeight': 'bold',
        'textAlign': 'center'
    }
)

# --- Import Page Modules ---
from pages.fact_sheet import introduction, profitability

# --- TAB LAYOUT ---
tabbed_page = html.Div(
    [
        header,
        # Place the AI recommendation message below the header
        ai_recommendation_div,
        dcc.Tabs(
            children=[
                dcc.Tab(label="Introduction", children=introduction.layout),
                dcc.Tab(label="Profitability", children=profitability.layout)
            ]
        )
    ],
    className="main-content",
    style={"backgroundColor": PAGE_BG}
)

app.layout = html.Div(
    [
        tabbed_page,
        dcc.Store(id="results-store", data=results_df.to_json(date_format="iso", orient="split"))
    ]
)

# -------------------------------
# DATA UPDATE CALLBACK
# -------------------------------
@app.callback(Output("results-store", "data"), Input("company-dropdown", "value"))
def update_data(selected_file):
    if selected_file:
        full_path = os.path.join(DATA_FOLDER, selected_file)
        if full_path.lower().endswith(".xlsx"):
            df = pd.read_excel(full_path)
        else:
            df = pd.read_csv(full_path)
        df = preprocess_year_month_columns(df)
        return df.to_json(date_format="iso", orient="split")
    return None

# -------------------------------
# GLOBAL PERIOD OPTIONS CALLBACK
# -------------------------------
@app.callback(
    [Output("global-period", "options"),
     Output("global-period", "value")],
    Input("global-view-mode", "value")
)
def update_global_period_options(view_mode):
    if view_mode == "yearly":
        # For monthly view: show available years as integers.
        years = sorted(results_df["Year"].unique()) if not results_df.empty and "Year" in results_df.columns else [2023]
        options = [{"label": str(int(year)), "value": int(year)} for year in years]
        default = int(years[-1]) if years else 2023
        return options, default
    else:
        # For YTD and YOY, show months.
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        options = [{"label": m, "value": m} for m in months]
        default = "January"
        return options, default

# -------------------------------
# PROFITABILITY CHART CALLBACK
# -------------------------------
import plotly.graph_objects as go

@app.callback(
    [Output("chart1", "figure"),
     Output("chart3", "figure"),
     Output("chart4", "figure")],
    [Input("results-store", "data"),
     Input("global-view-mode", "value"),
     Input("global-period", "value")]
)
def update_profitability_charts(results_data, view_mode, period):
    if not results_data:
        return {}, {}, {}
    
    df = pd.read_json(results_data, orient="split")
    
    # Define month order for proper sorting
    month_order = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]
    
    if "Month" in df.columns:
        df["Month"] = pd.Categorical(df["Month"], categories=month_order, ordered=True)
    
    # Prepare empty figures
    fig_revenue = go.Figure()
    fig_ebitda = go.Figure()
    fig_cost = go.Figure()
    
    if view_mode == "YTD":
        # For YTD, 'period' is a month (e.g., "March")
        selected_month = period
        if "Month" in df.columns:
            df_ytd = df.copy()
            df_ytd["MonthNum"] = df_ytd["Month"].cat.codes + 1
            selected_month_num = month_order.index(selected_month) + 1
            df_ytd = df_ytd[df_ytd["MonthNum"] <= selected_month_num]
            df_group = df_ytd.groupby("Year", as_index=False).agg({
                "Revenue": "sum",
                "EBITDA": "sum",
                "Cost": "sum"
            })
            if "Year" in df_group.columns:
                df_group["Year"] = df_group["Year"].astype(int).astype(str)
        else:
            df_group = pd.DataFrame()
        
        fig_revenue = go.Figure(data=go.Bar(x=df_group["Year"], y=df_group["Revenue"]))
        fig_revenue.update_layout(title=f"YTD Revenue (up to {selected_month})", xaxis_title="Year", yaxis_title="Revenue")
        
        fig_ebitda = go.Figure(data=go.Bar(x=df_group["Year"], y=df_group["EBITDA"]))
        fig_ebitda.update_layout(title=f"YTD EBITDA (up to {selected_month})", xaxis_title="Year", yaxis_title="EBITDA")
        
        fig_cost = go.Figure(data=go.Bar(x=df_group["Year"], y=df_group["Cost"]))
        fig_cost.update_layout(title=f"YTD Cost (up to {selected_month})", xaxis_title="Year", yaxis_title="Cost")
    
    elif view_mode == "YOY":
        # For YOY, 'period' is a month. Filter by that month across years.
        selected_month = period
        df_yoy = df[df["Month"] == selected_month].copy()
        df_group = df_yoy.groupby("Year", as_index=False).agg({
            "Revenue": "sum",
            "EBITDA": "sum",
            "Cost": "sum"
        })
        if "Year" in df_group.columns:
            df_group["Year"] = df_group["Year"].astype(int).astype(str)
        
        fig_revenue = go.Figure(data=go.Bar(x=df_group["Year"], y=df_group["Revenue"]))
        fig_revenue.update_layout(title=f"YOY Revenue for {selected_month}", xaxis_title="Year", yaxis_title="Revenue")
        
        fig_ebitda = go.Figure(data=go.Bar(x=df_group["Year"], y=df_group["EBITDA"]))
        fig_ebitda.update_layout(title=f"YOY EBITDA for {selected_month}", xaxis_title="Year", yaxis_title="EBITDA")
        
        fig_cost = go.Figure(data=go.Bar(x=df_group["Year"], y=df_group["Cost"]))
        fig_cost.update_layout(title=f"YOY Cost for {selected_month}", xaxis_title="Year", yaxis_title="Cost")
    
    elif view_mode == "yearly":
        # For monthly view, 'period' is a year (as int).
        selected_year = int(period)
        df_year = df[df["Year"] == selected_year].copy()
        df_year = df_year.sort_values("Month")
        
        fig_revenue = go.Figure(data=go.Bar(x=df_year["Month"], y=df_year["Revenue"]))
        fig_revenue.update_layout(title=f"Monthly Revenue for {selected_year}", xaxis_title="Month", yaxis_title="Revenue")
        
        fig_ebitda = go.Figure(data=go.Bar(x=df_year["Month"], y=df_year["EBITDA"]))
        fig_ebitda.update_layout(title=f"Monthly EBITDA for {selected_year}", xaxis_title="Month", yaxis_title="EBITDA")
        
        fig_cost = go.Figure(data=go.Bar(x=df_year["Month"], y=df_year["Cost"]))
        fig_cost.update_layout(title=f"Monthly Cost for {selected_year}", xaxis_title="Month", yaxis_title="Cost")
    
    return fig_revenue, fig_ebitda, fig_cost

# -------------------------------
# AI Recommendation Callback
# -------------------------------
@app.callback(
    Output("ai-recommendation", "children"),
    Input("results-store", "data")
)
def update_ai_recommendation(results_data):
    if not results_data:
        return ""
    
    df = pd.read_json(results_data, orient="split")
    # Select only the columns used for training
    required_cols = ['Revenue', 'Net Income', 'EBITDA']
    if not set(required_cols).issubset(df.columns):
        return "Required columns are missing from the data."
    
    features = df[required_cols]
    # Preprocess the features using the saved scaler
    scaled_features = scaler.transform(features)
    
    # Generate prediction using the loaded model; in case of multiple rows, we take the first prediction.
    prediction = best_model.predict(scaled_features)
    recommendation = label_encoder.inverse_transform([prediction[0]])[0]
    return f"AI model recommends: {recommendation}"

if __name__ == "__main__":
    app.run_server(debug=True, port=8050)
