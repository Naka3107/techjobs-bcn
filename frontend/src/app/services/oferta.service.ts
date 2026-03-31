import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Oferta } from '../models/oferta';
import { Programador } from '../models/programador';

@Injectable({ providedIn: 'root' })
export class OfertaService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:5000';

  getOfertas() {
    return this.http.get<Oferta[]>(`${this.apiUrl}/ofertas`);
  }

  getOfertasCompatibles(salarioMinimo?: number, pais?: string) {
    let params = new HttpParams();
    if (salarioMinimo) params = params.set('salario_minimo', salarioMinimo);
    if (pais) params = params.set('pais', pais);
    return this.http.get<Oferta[]>(`${this.apiUrl}/ofertas/compatibles`, { params });
  }

  getProgramadores() {
    return this.http.get<Programador[]>(`${this.apiUrl}/programadores`);
  }
}