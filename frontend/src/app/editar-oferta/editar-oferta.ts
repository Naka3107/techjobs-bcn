import { Component, inject, signal, OnInit, computed } from '@angular/core';
import { Router, RouterLink, ActivatedRoute } from '@angular/router';
import { OfertaService } from '../services/oferta.service';
import { Oferta } from '../models/oferta';
import { AuthService } from '../services/auth';
import { HttpClient } from '@angular/common/http';
import { PAISES } from '../data/paises';
import { TECNOLOGIAS } from '../data/tecnologias';

@Component({
  selector: 'app-editar-oferta',
  imports: [RouterLink],
  templateUrl: './editar-oferta.html',
  styleUrl: './editar-oferta.scss',
})
export class EditarOferta {
  private service = inject(OfertaService);
  authService = inject(AuthService);
  private http = inject(HttpClient);
  private router = inject(Router);
  private route = inject(ActivatedRoute);
  
  ofertaOriginal = signal<Oferta | null>(null);
  puesto = signal ('');
  ciudad = signal('');
  pais = signal('');
  salario = signal(0);
  tecnologiasActuales= signal<string[]>([]);
  tecnologiasSeleccionadas = signal<string[]>([]);

  sugerenciasCiudad = signal<string[]>([]);
  buscandoCiudad = signal(false);
  paisSeleccionado = signal<{nombre: string, codigo: string} | null>(null);  

  readonly PAISES = PAISES;
  readonly TECNOLOGIAS = TECNOLOGIAS

  toggleTecnologia(tec: string) {
    const actuales = this.tecnologiasSeleccionadas();
    if (actuales.includes(tec)) {
      this.tecnologiasSeleccionadas.set(actuales.filter(t => t !== tec));
    } else {
      this.tecnologiasSeleccionadas.set([...actuales, tec]);
    }
  }

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
      this.sugerenciasCiudad.set(
        resultados.map(r => r.display_name.split(',')[0])
      );
    });
  }

  agregarOtraTecnologia(tec: string) {
    const t = tec.trim();
    if (t && !this.tecnologiasSeleccionadas().includes(t)) {
      this.tecnologiasSeleccionadas.set([...this.tecnologiasSeleccionadas(), t]);
    }
  }

  seleccionarCiudad(ciudad: string) {
    this.ciudad.set(ciudad);
    this.sugerenciasCiudad.set([]);
  }

  detectaCambios = computed(() => {
    const original = this.ofertaOriginal();
    if (!original) return false;
    const puestoCambiado = this.puesto() !== original.puesto;
    const ciudadCambiada = this.ciudad() !== original.ciudad;
    const paisCambiado = this.pais() !== original.pais;
    const salarioCambiado = this.salario() !== (original.salario ?? 0);
    const tecnologiasCambiadas = JSON.stringify([...this.tecnologiasSeleccionadas()].sort()) !== 
                     JSON.stringify([...this.tecnologiasActuales()].sort());
    
    return puestoCambiado || ciudadCambiada || paisCambiado || salarioCambiado || tecnologiasCambiadas;
  });
  
  ngOnInit() {
    const idParam = this.route.snapshot.paramMap.get('id');
    if (!idParam) {
      this.router.navigate(['/ofertas']);
      return;
    }
    const id = +idParam; // convierte a numero
    this.service.getOferta(id).subscribe({
      next: (data) => {
        this.ofertaOriginal.set(data);
        this.puesto.set(data.puesto);
        this.ciudad.set(data.ciudad);
        this.pais.set(data.pais);
        this.salario.set(data.salario ?? 0);
        const paisEncontrado = PAISES.find(p => p.nombre === data.pais);
        if (paisEncontrado) this.paisSeleccionado.set(paisEncontrado);
        this.tecnologiasActuales.set(data.tecnologias ?? []);
        this.tecnologiasSeleccionadas.set(data.tecnologias ?? []);
      },
      error: (err) => console.error('Error al cargar el perfil', err)
    });
  }

  actualizarOferta() {
    if (!this.ofertaOriginal()) return;
    if (!confirm('¿Estás seguro que quieres guardar los cambios?')) return;
    
    const id = this.ofertaOriginal()!.id;
    const datosActualizados = {
      puesto: this.puesto(),
      salario: this.salario(),
      pais: this.pais(),
      ciudad: this.ciudad(),
      tecnologias: this.tecnologiasSeleccionadas()
    };

    this.service.actualizarOferta(id, datosActualizados).subscribe({
      next: () => {
        alert('Oferta actualizada con éxito');
        this.router.navigate(['/ofertas']);
      },
      error: (err) => {
        console.error('Error al actualizar el perfil', err);
        alert('Error al actualizar el perfil');
      }
    });
  }
}
