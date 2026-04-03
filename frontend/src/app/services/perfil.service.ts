import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { PerfilResponse } from '../models/perfil-response';
import { forkJoin } from 'rxjs';


@Injectable({ providedIn: 'root'})
export class PerfilService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:5000';

  getPerfil() {
    return this.http.get<PerfilResponse>(`${this.apiUrl}/perfil`);
  }

  actualizarPerfil(datos: PerfilResponse, rol: string, tecnologiasActuales: string[], tecnologiasNuevas: string[]) {
    const agregar = tecnologiasNuevas.filter(t => !tecnologiasActuales.includes(t));
    const eliminar = tecnologiasActuales.filter(t => !tecnologiasNuevas.includes(t));

    const datosFiltrados: any = {
      nombre: datos.nombre,
      ciudad: datos.ciudad,
      pais: datos.pais
    };

    if (rol === 'programador') {
      datosFiltrados.años_experiencia = datos.experiencia;
    } else if (rol === 'empresa') {
      datosFiltrados.pagina_web = datos.pagina_web;
    }

    const actualizarDatos$ = this.http.put(`${this.apiUrl}/perfil`, datosFiltrados);

    const llamadas = [actualizarDatos$];

    if (agregar.length > 0) {
      llamadas.push(this.http.post(`${this.apiUrl}/perfil/tecnologias`, { tecnologias: agregar }));
    }
    
    if (eliminar.length > 0) {
      llamadas.push(this.http.delete(`${this.apiUrl}/perfil/tecnologias`, { body: { tecnologias: eliminar } }));
    }

    return forkJoin(llamadas);
  }
}
