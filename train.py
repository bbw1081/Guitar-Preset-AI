"""
    train.py; trains the models on the preset data
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
from sklearn.multioutput import MultiOutputClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import hamming_loss
from pathlib import Path

# -- 1. Load Data --
embeddings = np.load("data/embeddings.npy")

with open('data/presets_combined.json') as f:
    presets = json.load(f)

print(f"Loaded {len(presets)} presets")

# -- 2. Define effect list --

ALL_EFFECTS = [
    'autowah', 'chorus', 'decimator', 'delay', 'eq', 'flanger', 
    'overdrive', 'phaser', 'pitchshifter', 'reverb', 'reversedelay',
    'tremolo', 'wavefolder', 'hard_clip', 'soft_clip', 'jfet',
    'bjt', 'opamp', 'cmos' 
]

# -- 3. Build stage 1 labels
effect_labels = []
for preset in presets:
    row = [1 if effect in preset['effects'] else 0 for effect in ALL_EFFECTS]
    effect_labels.append(row)

effect_labels = np.array(effect_labels)

# -- 4. train/test split --
# 20/80 train/test split
x_train, x_test, y_train, y_test = train_test_split(
    embeddings, effect_labels,
    test_size=0.2,
    random_state=42
)

print(f"Training on {len(x_train)} presets, testing on {len(x_test)}")

# -- 5. train stage 1: effect classifier --
print("\nTraining effect classifier..")
effect_classifier = MultiOutputClassifier(
    RandomForestClassifier(n_estimators=100, random_state=42)
)
effect_classifier.fit(x_train, y_train)

y_pred = effect_classifier.predict(x_test)

hl = hamming_loss(y_test, y_pred)
print(f"Effect classidier hamming loss: {hl:.3f} (lower is better, 0 is perfect)")

# -- 6. train stage 2: parameter regressors --

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

# -- Validate parameter counts --
print("\nValidating parameter counts...")
validation_passed = True

for i, preset in enumerate(presets):
    for effect_index, effect in enumerate(preset['effects']):
        expected = EFFECT_PARAM_COUNTS.get(effect)
        if expected is None:
            print(f"  Preset '{preset['name']}': unknown effect '{effect}'")
            validation_passed = False
            continue
        
        actual = len(preset['params'][effect_index])
        if actual != expected:
            print(f"  Preset '{preset['name']}': {effect} has {actual} params, "
                  f"expected {expected}")
            validation_passed = False

if not validation_passed:
    print("\nFix the above presets before training.")
    exit()
else:
    print("All presets valid.")

print("\nTraining parameter regressors")
param_regressors = {}

for effect in ALL_EFFECTS:
    indices = [i for i, p in enumerate(presets) if effect in p['effects']]

    if (len(indices) < 5):
        print(f"   {effect}: only {len(indices)} examples, skpping regressor")
        continue

    x_effect = embeddings[indices]

    y_effect = []
    for i in indices:
        preset = presets[i]
        effect_index = preset['effects'].index(effect)
        y_effect.append(preset['params'][effect_index])
    
    y_effect = np.array(y_effect)

    from sklearn.multioutput import MultiOutputRegressor
    regressor = MultiOutputRegressor(
        RandomForestRegressor(n_estimators=100, random_state=42)
    )
    regressor.fit(x_effect, y_effect)
    param_regressors[effect] = regressor

    print(f"   {effect}: trained on {len(indices)} presets, "
          f"{EFFECT_PARAM_COUNTS[effect]} params")
    
# -- 7. save everything --

Path('models').mkdir(exist_ok=True)

pickle.dump(effect_classifier, open('models/effect_classifier.pkl', 'wb'))
pickle.dump(param_regressors,  open('models/param_regressors.pkl',  'wb'))
pickle.dump({
    'all_effects': ALL_EFFECTS,
    'param_counts': EFFECT_PARAM_COUNTS
}, open('models/metadata.pkl', 'wb'))

print("\nSaved models to models/")
print("Training complete.")
