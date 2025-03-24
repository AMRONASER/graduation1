
- **app.py**: The main entry point that defines the Dash application, layout, callbacks, and server configuration.  
- **pages/fact_sheet/introduction.py**: A sample page module that might display introductory text or a simple table.  
- **pages/fact_sheet/profitability.py**: Contains the layout (three chart containers) for displaying **Revenue**, **EBITDA**, and **Cost**.  
- **database/**: A folder containing the Excel files (one per company) with columns like `Date`, `Year`, `Month`, `Revenue`, `EBITDA`, `Cost`.  
- **assets/**: A folder for images (e.g. `logo.jpg`).  

---

## Requirements

You will need:

- **Python 3.7+**  
- The following Python libraries:
  - [Dash](https://dash.plotly.com/) (and its dependencies)  
  - [Plotly](https://plotly.com/python/)  
  - [Pandas](https://pandas.pydata.org/)  
  - [openpyxl](https://pypi.org/project/openpyxl/) (or another Excel reader library)  

You can install these via `pip`:

```bash
pip install dash
pip install plotly
pip install pandas
pip install openpyxl
