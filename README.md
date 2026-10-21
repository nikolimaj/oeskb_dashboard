
# ÖSKB Dashboard

A data-driven dashboard for exploring Austrian ninepin bowling (Kegeln) results and player statistics. The project combines automated data collection and processing, as well as an interactive R Shiny application.

## Project Overview

The project is designed to collect, process, store, and visualize ÖSKB data across multiple seasons. Python scripts handle data retrieval and processing, while the Shiny dashboard provides an interactive interface for exploring player and match information.

### Main Features

- Historical match and player data covering multiple seasons
- Automated data retrieval and processing with Python
- Structured CSV datasets for analysis and visualization
- Interactive dashboard built with R Shiny
- Exploratory data analysis using Quarto and Jupyter notebooks
- Support for automated data updates using GitHub Actions


## Technologies

- **Python** — data retrieval, transformation, and processing
- **Pandas** — tabular data processing
- **Jupyter Notebook** — interactive data exploration
- **R and Shiny** — interactive dashboard and data visualization
- **Quarto** — reproducible reports and exploratory analysis
- **shinyapps.io** — dashboard hosting
- **GitHub Actions** — scheduled data updates


## Data Pipeline

The data processing workflow is organized into several stages:

1. **Data retrieval** — obtain source data using the Python collection scripts.
2. **Processing** — clean, transform, and structure the retrieved data.
3. **Storage** — save processed datasets as CSV files for subsequent analysis.
4. **Visualization** — use the processed data in the Shiny dashboard and exploratory reports.
5. **Automation** — run configured GitHub Actions workflows to update datasets on a schedule.


## Deployment

The Shiny application is configured for deployment to **shinyapps.io** and available at https://use3cn-maja-nikolic.shinyapps.io/shiny_dashboard_oeskb/