import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PresetDisplay } from './preset-display';

describe('PresetDisplay', () => {
  let component: PresetDisplay;
  let fixture: ComponentFixture<PresetDisplay>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PresetDisplay],
    }).compileComponents();

    fixture = TestBed.createComponent(PresetDisplay);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
