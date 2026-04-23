from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import json


from predict import predict_preset

# app setup
app = FastAPI(
    title="Guitar Preset AI",
    description="Generate guitar effect presets from descriptions",
    version="BETA_0.1.0"
)

# CORS
# allows for interaction with angular frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200", # angular dev server address
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

# request and response models
class GenerateRequest(BaseModel):
    description: str
    name: str = ""

class PresetResponse(BaseModel):
    name: str
    effects: list[str]
    params: list[list[float]]
    description: str
    header_content: str

def build_header_content(preset: dict) -> str:
    """
    Builds a C++ header file as a string,
    Allows for the frontend to offer it as a download
    """

    json_str = json.dumps({
        'name'          : preset['name'],
        'effects'       : preset['effects'],
        'params'        : preset['params'],
        'description'   : preset['description']
    }, indent=4)

    return f'#pragma once\nconst char preset[] = R"({{\n{json_str}\n}})";\n'

#routes
@app.get("/")
def root():
    """
    Health check endpoint
    """
    return{"status": "ok", "message": "Guitar preset AI is running"}

@app.get("/effects")
def get_effects():
    """
    returns the list of all possible effects and thier parameters
    """
    return {
        "effects": [
            {"name": "autowah",      "params": ["dry_wet (0-100)", "level (0-1)", "wah (0-1)"]},
            {"name": "chorus",       "params": ["delay (ms)", "feedback (0-1)", "lfo_frequency (Hz)"]},
            {"name": "decimator",    "params": ["bits (0-16)", "downsample (float)"]},
            {"name": "delay",        "params": ["delay_time (ms)", "feedback (0-1)", "mix (0-1)"]},
            {"name": "eq",           "params": ["31Hz", "62Hz", "125Hz", "250Hz", "500Hz", "1kHz", "2kHz", "4kHz", "8kHz", "16kHz"]},
            {"name": "flanger",      "params": ["delay (ms)", "feedback (0-1)", "lfo_frequency (Hz)"]},
            {"name": "overdrive",    "params": ["drive_amount (0-1)"]},
            {"name": "phaser",       "params": ["feedback (0-1)", "frequency (Hz)", "lfo_frequency (Hz)", "poles (1-8)"]},
            {"name": "pitchshifter", "params": ["size (uint32_t)", "fun (float)", "transpose (semitones)", "mix (0-1)"]},
            {"name": "reverb",       "params": ["feedback (0-1)", "lp_frequency (0-24000)"]},
            {"name": "reversedelay", "params": ["delay_time (ms)", "feedback (0-1)", "mix (0-1)"]},
            {"name": "tremolo",      "params": ["depth (0-1)", "frequency (Hz)"]},
            {"name": "wavefolder",   "params": ["gain (float)", "offset (float)"]},
            {"name": "hard_clip",    "params": ["drive (0-1)", "tone (0-1)", "symmetry (0-1)"]},
            {"name": "soft_clip",    "params": ["drive (0-1)", "tone (0-1)"]},
            {"name": "jfet",         "params": ["drive (0-1)", "grit (0-1)", "bias (0-1)", "tone (0-1)"]},
            {"name": "bjt",          "params": ["drive (0-1)", "steepness (0-1)", "asymmetry (0-1)", "bias (0-1)", "tone (0-1)"]},
            {"name": "opamp",        "params": ["drive (0-1)", "soft_threshold (0-1)", "hard_threshold (0-1)", "mix (0-1)", "tone (0-1)"]},
            {"name": "cmos",         "params": ["drive (0-1)", "crunch (0-1)", "fizz (0-1)", "pregain (0-1)", "sag (0-1)", "tone (0-1)"]},
        ]
    }

@app.post("/generate", response_model=PresetResponse)
def generate(request: GenerateRequest):
    """
    Main endpoint - takes a description and name,
    returns the generated preset
    """
    #input validation
    if not request.description.strip():
        raise HTTPException(
            status_code=400,
            detail="Description cannot be empty"
        )
    
    #cap description length
    if len(request.description) > 500:
        raise HTTPException(
            status_code=400,
            detail="Description must be under 500 characters"
        )
    
    try:
        preset = predict_preset(
            request.description.strip(),
            request.name.strip() or None
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Model error: {str(e)}"
        )

    return PresetResponse(
        name=preset['name'],
        effects=preset['effects'],
        params=preset['params'],
        description=preset['description'],
        header_content=build_header_content(preset)
    )