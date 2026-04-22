"""
    predict.py; predicts a preset based on a user's description
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

import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from pathlib import Path
import json

encoder           = SentenceTransformer('all-MiniLM-L6-v2')
effect_classifier = pickle.load(open('models/effect_classifier.pkl', 'rb'))
param_regressors  = pickle.load(open('models/param_regressors.pkl',  'rb'))
metadata          = pickle.load(open('models/metadata.pkl',          'rb'))

ALL_EFFECTS = metadata['all_effects']

PARAM_RANGES = {
    'autowah':      [(0, 100),   (0, 1),     (0, 1)],
    'chorus':       [(0, 100),   (0, 1),     (0, 20)],
    'decimator':    [(0, 16),    (0.0, 10.0)],
    'delay':        [(0, 1000),  (0, 1),     (0, 1)],
    'eq':           [(0, 1)] * 10,
    'flanger':      [(0, 100),   (0, 1),     (0, 20)],
    'overdrive':    [(0, 1)],
    'phaser':       [(0, 1),     (0, 20000), (0, 20), (1, 8)],
    'pitchshifter': [(0, 65535), (0.0, 1.0), (-24, 24), (0, 1)],
    'reverb':       [(0, 1),     (0, 24000)],
    'reversedelay': [(0, 1000),  (0, 1),     (0, 1)],
    'tremolo':      [(0, 1),     (0, 20)],
    'wavefolder':   [(0.0, 10.0),(0.0, 1.0)],
    'hard_clip':    [(0, 1),     (0, 1),     (0, 1)],
    'soft_clip':    [(0, 1),     (0, 1)],
    'jfet':         [(0, 1),     (0, 1),     (0, 1),  (0, 1)],
    'bjt':          [(0, 1),     (0, 1),     (0, 1),  (0, 1),  (0, 1)],
    'opamp':        [(0, 1),     (0, 1),     (0, 1),  (0, 1),  (0, 1)],
    'cmos':         [(0, 1),     (0, 1),     (0, 1),  (0, 1),  (0, 1), (0, 1)],
}

DISTORTION_EFFECTS = {
    'overdrive', 'hard_clip', 'soft_clip', 'jfet', 'bjt', 'opamp', 'cmos'
}

def clamp_params(effect, raw_params):
    """
    Takes the raw float output from the regressor and clips each parameter
    to its valid range. Also rounds integer parameters like bits and poles.
    """
    ranges = PARAM_RANGES[effect]
    clamped = []
    for value, (lo, hi) in zip(raw_params, ranges):
        clamped_value = float(np.clip(value, lo, hi))
        # Round parameters that must be integers
        if effect == 'decimator' and len(clamped) == 0:  # bits to crush
            clamped_value = round(clamped_value)
        if effect == 'phaser' and len(clamped) == 3:      # poles
            clamped_value = round(clamped_value)
        if effect == 'pitchshifter' and len(clamped) == 0: # delay size
            clamped_value = int(clamped_value)
        if effect == 'pitchshifter' and len(clamped) == 2: # transpose semitones
            clamped_value = round(clamped_value)
        clamped.append(clamped_value)
    return clamped


def predict_preset(description, preset_name=None):
    """
    Takes a text description and returns a preset dict ready to be
    written as a header file.
    """
    # Encode the description
    embedding = encoder.encode([description])

    # Stage 1: predict which effects are active
    # predict() returns a binary array
    predicted_binary = effect_classifier.predict(embedding)[0]
    active_effects = [
        effect for effect, active
        in zip(ALL_EFFECTS, predicted_binary)
        if active == 1
    ]

    # Handle the distortion conflict
    active_distortions = [e for e in active_effects if e in DISTORTION_EFFECTS]
    if len(active_distortions) > 1:
        best = max(
            active_distortions,
            key=lambda e: effect_classifier.estimators_[
                ALL_EFFECTS.index(e)
            ].predict_proba(embedding)[0][1]
        )
        # Remove all distortions except the most confident one
        active_effects = [
            e for e in active_effects
            if e not in DISTORTION_EFFECTS or e == best
        ]

    # Handle no effects predicted
    if not active_effects:
        print("Warning: no effects predicted, defaulting to overdrive")
        active_effects = ['overdrive']

    # Stage 2: predict parameters for each active effect
    predicted_params = []
    for effect in active_effects:
        if effect not in param_regressors:
            ranges = PARAM_RANGES[effect]
            fallback = [(lo + hi) / 2 for lo, hi in ranges]
            predicted_params.append(fallback)
            print(f"Warning: no regressor for {effect}, using default params")
            continue

        regressor = param_regressors[effect]
        raw = regressor.predict(embedding)[0]  # raw float array
        clamped = clamp_params(effect, raw)
        predicted_params.append(clamped)

    # Assemble the preset dict
    name = preset_name if preset_name else description[:32]
    return {
        'name': name,
        'effects': active_effects,
        'params': predicted_params,
        'description': description
    }


def write_header_file(preset, output_path):
    """
    Writes the preset dict as a C++ header file
    """
    # json.dumps with indent=4 produces nicely formatted JSON
    json_str = json.dumps({
        'name':        preset['name'],
        'effects':     preset['effects'],
        'params':      preset['params'],
        'description': preset['description']
    }, indent=4)

    # Build the C++ header string
    header = f"""#pragma once
const char preset[] = R"({{
{json_str}
}})";
"""
    Path(output_path).write_text(header)
    print(f"Written to {output_path}")


# Main loop
if __name__ == '__main__':
    print("\n\nGuitar Preset Generator")
    print("Copyright (C) 2026  Richard Wilkinson")
    print("See LICENSE for more info\n")

    while True:
        description = input("Type a description to generate a preset, or 'quit' to exit: ").strip()
        if description.lower() in ('quit', 'exit', 'q'):
            break
        if not description:
            continue

        name = input("Preset name (or press Enter to use description): ").strip()
        if not name:
            name = description[:32]

        preset = predict_preset(description, name)

        print(f"\nGenerated preset:")
        print(f"  Effects: {preset['effects']}")
        for effect, params in zip(preset['effects'], preset['params']):
            print(f"  {effect}: {params}")

        save = input("\nSave as header file? (y/n): ").strip().lower()
        if save == 'y':
            filename = name.lower().replace(' ', '_') + '.h'
            output_dir = Path('generated_presets')
            output_dir.mkdir(exist_ok=True)
            write_header_file(preset, output_dir / filename)

        print()

