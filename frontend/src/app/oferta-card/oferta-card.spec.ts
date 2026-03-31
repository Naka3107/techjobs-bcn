import { ComponentFixture, TestBed } from '@angular/core/testing';

import { OfertaCard } from './oferta-card';

describe('OfertaCard', () => {
  let component: OfertaCard;
  let fixture: ComponentFixture<OfertaCard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [OfertaCard],
    }).compileComponents();

    fixture = TestBed.createComponent(OfertaCard);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
