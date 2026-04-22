"""
    pipeline.py; runs the entire training pipeline
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

from encode_descriptions import encode
from train import train
from predict import predict_preset, write_header_file
from pathlib import Path

def run_pipeline():
    # Step 1: Encode
    print("=" * 50)
    print("STEP 1: Encoding descriptions")
    print("=" * 50)
    presets, embeddings = encode()

    # Step 2: Train 
    print("\n" + "=" * 50)
    print("STEP 2: Training models")
    print("=" * 50)
    try:
        hl = train()
    except ValueError as e:
        print(f"\nPipeline stopped: {e}")
        return

    # Step 3: Validation prediction
    # Run a test prediction to confirm the saved models load and work
    # correctly end-to-end before reporting success
    print("\n" + "=" * 50)
    print("STEP 3: Validating pipeline with test prediction")
    print("=" * 50)
    test = predict_preset("warm overdrive with light reverb", "pipeline test")
    print(f"Test prediction effects: {test['effects']}")
    print(f"Test prediction params:  {test['params']}")

    # Optionally write the test preset so you can inspect the output format
    Path('generated_presets').mkdir(exist_ok=True)
    write_header_file(test, 'generated_presets/pipeline_test.h')

    # Summary
    print("\n" + "=" * 50)
    print("Pipeline complete")
    print(f"  Presets loaded:   {len(presets)}")
    print(f"  Hamming loss:     {hl:.3f}")
    print(f"  Models saved to:  models/")
    print(f"  Test preset:      generated_presets/pipeline_test.h")
    print("=" * 50)

if __name__ == '__main__':
    run_pipeline()