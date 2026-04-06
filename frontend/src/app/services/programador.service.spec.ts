import { TestBed } from '@angular/core/testing';

import { ProgramadorService } from './programador.service';

describe('Programador', () => {
  let service: ProgramadorService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ProgramadorService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
