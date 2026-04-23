import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { GenerateRequest, Preset, EffectInfo } from '../models/preset.model';

@Injectable({
  providedIn: 'root',
})
export class PresetService {
  private apiUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  generatePreset(description: string, name: string): Observable<Preset> {
    const body: GenerateRequest = { description, name };
    return this.http.post<Preset>(`${this.apiUrl}/generate`, body);
  }

  getEffects(): Observable<{ effects: EffectInfo[] }> {
    return this.http.get<{ effects: EffectInfo[] }>(`${this.apiUrl}/effects`);
  }
}

