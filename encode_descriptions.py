"""
    encode_descriptions.py; parses and encodes the preset files
    Copyright (C) 2026  Richard Wilkinson

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from sentence_transformers import SentenceTransformer
from pathlib import Path
import json
import re
import numpy as np

def parse_preset_file(filepath):
    """
    Reads a header (.h) file and extract the JSON data containined within
    """
    text = filepath.read_text()

    #search for the data contained between R"()";
    match = re.search(r'R"\((.+?)\)"', text, re.DOTALL)

    if (not match):
        print(f"WARNING: could not find JSON in {filepath.name}, skipping")
        return None
    
    json_str = match.group(1)

    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"WARNING: Json parse error in {filepath.name}: {e}, skipping")
        return None
    
# Collect all header files in the data/ folder
data_dir = Path('data')
preset_files = list(data_dir.glob('*.h'))
print(f"Found {len(preset_files)} preset files")

#parse each file
presets = []
for filepath in preset_files:
    preset = parse_preset_file(filepath)
    if preset is not None:
        presets.append(preset)

print(f"Successfully parsed {len(presets)} presets")

#save all presets into single json file
with open('data/presets_combined.json', 'w') as f:
    json.dump(presets, f, indent=2)
print("Saved combined dataset to data/presets_combined.json")

#extract and encode descriptions
descriptions = [p['description'] for p in presets]

encoder = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = encoder.encode(descriptions)

print(f"Each description is now shape: {embeddings[0].shape}")

np.save('data/embeddings.npy', embeddings)
print("Saved embeddings to data/embeddings.npy")