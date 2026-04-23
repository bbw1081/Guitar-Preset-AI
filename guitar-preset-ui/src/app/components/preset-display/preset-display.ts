import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Preset } from '../../models/preset.model';

@Component({
  selector: 'app-preset-display',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './preset-display.html',
  styleUrl: './preset-display.css',
})
export class PresetDisplay {
  @Input() preset!: Preset;
  @Output() generateAnother = new EventEmitter<void>();

  downloadHeader() {
    const blob = new Blob([this.preset.header_content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');

    link.href = url;
    link.download = `${this.preset.name.toLowerCase().replace(/\s+/g, '_')}.h`;
    link.click();

    URL.revokeObjectURL(url);
  }

  formatParam(value: number): string {
    return Math.round(value*1000) / 1000 + '';
  }
}
