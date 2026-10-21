from pathlib import Path
import shutil

base_dir = Path(__file__).resolve().parents[1]

input_file = base_dir / "parsed_data" / "game_data_latest.csv"
output_file = base_dir / "parsed_data" / "game_data_previous.csv"

output_file.parent.mkdir(parents=True, exist_ok=True)

shutil.copy(input_file, output_file)