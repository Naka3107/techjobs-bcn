import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NuevaOferta } from './nueva-oferta';

describe('NuevaOferta', () => {
  let component: NuevaOferta;
  let fixture: ComponentFixture<NuevaOferta>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NuevaOferta],
    }).compileComponents();

    fixture = TestBed.createComponent(NuevaOferta);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
