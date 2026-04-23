// src/app/models/preset.model.ts
export interface GenerateRequest {
  description: string;
  name: string;
}

export interface Preset {
  name: string;
  effects: string[];
  params: number[][];
  description: string;
  header_content: string;
}

export interface EffectInfo {
  name: string;
  params: string[];
}