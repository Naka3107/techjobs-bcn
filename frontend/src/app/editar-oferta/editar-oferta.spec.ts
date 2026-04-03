import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EditarOferta } from './editar-oferta';

describe('EditarOferta', () => {
  let component: EditarOferta;
  let fixture: ComponentFixture<EditarOferta>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EditarOferta],
    }).compileComponents();

    fixture = TestBed.createComponent(EditarOferta);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
