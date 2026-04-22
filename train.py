"""
    train.py; trains the AI models
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

import json
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.multioutput import MultiOutputClassifier, MultiOutputRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import hamming_loss
from pathlib import Path

ALL_EFFECTS = [
    'autowah', 'chorus', 'decimator', 'delay', 'eq', 'flanger', 
    'overdrive', 'phaser', 'pitchshifter', 'reverb', 'reversedelay',
    'tremolo', 'wavefolder', 'hard_clip', 'soft_clip', 'jfet',
    'bjt', 'opamp', 'cmos' 
]

EFFECT_PARAM_COUNTS = {
    'autowah'       : 3,
    'chorus'        : 3,
    'decimator'     : 2,
    'delay'         : 3,
    'eq'            : 10,
    'flanger'       : 3, 
    'overdrive'     : 1,
    'phaser'        : 4,
    'pitchshifter'  : 4,
    'reverb'        : 2,
    'reversedelay'  : 3,
    'tremolo'       : 2,
    'wavefolder'    : 2,
    'hard_clip'     : 3,
    'soft_clip'     : 2,
    'jfet'          : 4,
    'bjt'           : 5,
    'opamp'         : 5,
    'cmos'          : 6
}

def validate(presets):
    """
    Checks every preset has the correct number of parameters.
    Returns True if all valid, False if any problems found.
    """
    print("\nValidating parameter counts...")
    passed = True
    for preset in presets:
        for effect_index, effect in enumerate(preset['effects']):
            expected = EFFECT_PARAM_COUNTS.get(effect)
            if expected is None:
                print(f"  '{preset['name']}': unknown effect '{effect}'")
                passed = False
                continue
            actual = len(preset['params'][effect_index])
            if actual != expected:
                print(f"  '{preset['name']}': {effect} has {actual} params, "
                      f"expected {expected}")
                passed = False
    if passed:
        print("All presets valid.")
    return passed

def train():
    """
    Loads data, trains both models, saves them to models/.
    Returns the hamming loss score so the pipeline can report it.
    """
    # Load data 
    embeddings = np.load('data/embeddings.npy')
    with open('data/presets_combined.json') as f:
        presets = json.load(f)
    print(f"Loaded {len(presets)} presets")

    # Validate 
    if not validate(presets):
        raise ValueError("Preset validation failed — fix errors before training")

    # Stage 1: effect classification 
    effect_labels = []
    for preset in presets:
        row = [1 if e in preset['effects'] else 0 for e in ALL_EFFECTS]
        effect_labels.append(row)
    effect_labels = np.array(effect_labels)

    X_train, X_test, y_train, y_test = train_test_split(
        embeddings, effect_labels,
        test_size=0.2,
        random_state=42
    )
    print(f"Training on {len(X_train)} presets, testing on {len(X_test)}")

    print("\nTraining effect classifier...")
    effect_classifier = MultiOutputClassifier(
        RandomForestClassifier(n_estimators=100, random_state=42)
    )
    effect_classifier.fit(X_train, y_train)

    y_pred = effect_classifier.predict(X_test)
    hl = hamming_loss(y_test, y_pred)
    print(f"Effect classifier hamming loss: {hl:.3f}")

    # Stage 2: parameter regressors 
    print("\nTraining parameter regressors...")
    param_regressors = {}

    for effect in ALL_EFFECTS:
        indices = [i for i, p in enumerate(presets) if effect in p['effects']]

        if len(indices) < 5:
            print(f"  {effect}: only {len(indices)} examples, skipping")
            continue

        X_effect = embeddings[indices]
        y_effect = []
        for i in indices:
            preset = presets[i]
            effect_index = preset['effects'].index(effect)
            y_effect.append(preset['params'][effect_index])
        y_effect = np.array(y_effect)

        regressor = MultiOutputRegressor(
            RandomForestRegressor(n_estimators=100, random_state=42)
        )
        regressor.fit(X_effect, y_effect)
        param_regressors[effect] = regressor
        print(f"  {effect}: trained on {len(indices)} presets, "
              f"{EFFECT_PARAM_COUNTS[effect]} params")

    # Save 
    Path('models').mkdir(exist_ok=True)
    pickle.dump(effect_classifier, open('models/effect_classifier.pkl', 'wb'))
    pickle.dump(param_regressors,  open('models/param_regressors.pkl',  'wb'))
    pickle.dump({
        'all_effects':   ALL_EFFECTS,
        'param_counts':  EFFECT_PARAM_COUNTS
    }, open('models/metadata.pkl', 'wb'))

    print("\nSaved models to models/")

    # Return the hamming loss so pipeline.py can display a summary
    return hl

if __name__ == '__main__':
    train()