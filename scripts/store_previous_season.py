import pandas as pd
from pathlib import Path

base_url = "https://raw.githubusercontent.com/nikolimaj/oeskb_dashboard/master/parsed_data"

input_file = f"{base_url}/game_data_latest.csv"
output_file = Path("parsed_data/game_data_previous.csv")

output_file.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(input_file)
df.to_csv(output_file, index=False)