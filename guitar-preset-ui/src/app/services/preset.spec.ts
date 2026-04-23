import { TestBed } from '@angular/core/testing';

import { PresetService } from './preset';

describe('Preset', () => {
  let service: PresetService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(PresetService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
