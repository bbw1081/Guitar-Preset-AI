import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { PresetService } from '../../services/preset';
import { Preset } from '../../models/preset.model';
import { PresetDisplay } from '../preset-display/preset-display';

@Component({
  selector: 'app-generator',
  standalone: true,
  imports: [CommonModule, FormsModule, PresetDisplay],
  templateUrl: './generator.html',
  styleUrl: './generator.css',
})
export class Generator {
  description = '';
  presetName = '';
  preset: Preset | null = null;
  loading = false;
  error: string | null = null;

  constructor(private presetService: PresetService, private cdr: ChangeDetectorRef) {}

  generate() {
    if (!this.description.trim()) return;

    this.loading = true;
    this.error = null;
    this.preset = null;
    console.log('Sending generate request with:', this.description);

    this.presetService.generatePreset(
      this.description.trim(),
      this.presetName.trim()
    ).subscribe({
      next: (result) => {
        console.log('Preset response received:', result);
        this.preset = result;
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: (err) => {
        console.error('Error generating preset:', err);
        this.error = err.error?.detail ?? "Something went wrong, please try again"
        this.loading = false
        this.cdr.markForCheck();
      }
    });
  }

  reset() {
    this.preset = null;
    this.description = '';
    this.presetName = '';
    this.error = null;
  }
}
