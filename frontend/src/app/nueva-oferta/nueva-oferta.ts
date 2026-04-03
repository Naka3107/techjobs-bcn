import { Component, inject, signal } from '@angular/core';
import { RouterLink , Router } from '@angular/router';
import { OfertaService } from '../services/oferta.service';
import { PAISES } from '../data/paises';
import { TECNOLOGIAS } from '../data/tecnologias';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-nueva-oferta',
  imports: [RouterLink],
  templateUrl: './nueva-oferta.html',
  styleUrl: './nueva-oferta.scss',
})
export class NuevaOferta {
  private service = inject(OfertaService);
  private router = inject(Router);
  private http = inject(HttpClient);

  puesto = signal ('');
  salario = signal(0);
  ciudad = signal('');
  pais = signal('');
  cargando = signal(false);
  error = signal ('');
  tecnologiasSeleccionadas = signal<string[]>([]);

  readonly PAISES = PAISES;
  readonly TECNOLOGIAS = TECNOLOGIAS

  paisSeleccionado = signal<{nombre: string, codigo: string} | null>(null);
  sugerenciasCiudad = signal<string[]>([]);

  seleccionarPais(pais: {nombre: string, codigo: string}) {
    this.paisSeleccionado.set(pais);
    this.pais.set(pais.nombre);
    this.ciudad.set('');
    this.sugerenciasCiudad.set([]);
  }

  buscarCiudad(query: string) {
    this.ciudad.set(query);
    if (query.length < 3 || !this.paisSeleccionado()) {
      this.sugerenciasCiudad.set([]);
      return;
    }
    const codigo = this.paisSeleccionado()!.codigo;
    this.http.get<any[]>(
      `https://nominatim.openstreetmap.org/search?q=${query}&format=json&addressdetails=1&limit=5&featureType=city&countrycodes=${codigo}`
    ).subscribe(resultados => {
      this.sugerenciasCiudad.set(resultados.map(r => r.display_name.split(',')[0]));
    });
  }

  seleccionarCiudad(ciudad: string) {
    this.ciudad.set(ciudad);
    this.sugerenciasCiudad.set([]);
  }

  toggleTecnologia(tec: string) {
    const actuales = this.tecnologiasSeleccionadas();
    if (actuales.includes(tec)) {
      this.tecnologiasSeleccionadas.set(actuales.filter(t => t !== tec));
    } else {
      this.tecnologiasSeleccionadas.set([...actuales, tec]);
    }
  }

  agregarOtraTecnologia(tec: string) {
    const t = tec.trim();
    if (t && !this.tecnologiasSeleccionadas().includes(t)) {
      this.tecnologiasSeleccionadas.set([...this.tecnologiasSeleccionadas(), t]);
    }
  }

  guardarOferta() {
    if (!this.puesto() || !this.salario()) {
      this.error.set('Completa los campos obligatorios');
      return;
    }
    this.cargando.set(true);
    this.service.crearOferta({
      puesto: this.puesto(),
      salario: this.salario(),
      pais: this.pais(),
      ciudad: this.ciudad(),
      tecnologias: this.tecnologiasSeleccionadas()
    }).subscribe({
      next: () => this.router.navigate(['/ofertas']),
      error: () => {
        this.error.set('Error al crear la oferta');
        this.cargando.set(false);
      }
    });
  }

}
