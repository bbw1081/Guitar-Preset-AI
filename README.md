# Guitar-Preset-AI
AI Model for generating presets for this digital guitar pedal: https://github.com/bbw1081/DaisySeed-MultiFXPedal

Still very early, doesn't work very well because it needs a lot more training data

Right now it only works with text dcescriptions of presets

## Installing Dependencies

In the terminal run the following commands:

1. `git submodule update --init`

2. `python -m venv .venv`

3. `source .venv/bin/activate`

4. `pip install -r requirements.txt`

5. `npm install`

## Using the model

In the terminal run the following commands:

1. `python3 pipeline.py`

To use terminal interface:

2. `python3 predict.py`

To use web app:

2. `uvicorn api:app` with optional `--reload` argument

3. `cd guitar-preset-ui/ && ng serve --open`
