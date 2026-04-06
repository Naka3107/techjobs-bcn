import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Programador } from '../models/programador';

@Injectable({
  providedIn: 'root',
})
export class ProgramadorService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:5000';

  getProgramadores() {
    return this.http.get<Programador[]>(`${this.apiUrl}/programadores`);
  }

  getProgramadoresCompatibles(ofertaId?: number, experienciaMinima?: number, ciudad?: string) {
    let params = new HttpParams();
    if(ofertaId) params = params.set('ofertaId', ofertaId);
    if(experienciaMinima) params = params.set('años_experiencia_minimo', experienciaMinima);
    if(ciudad) params = params.set('ciudad', ciudad);
    return this.http.get<Programador[]>(`${this.apiUrl}/programadores/compatibles`, { params });
  }
}
