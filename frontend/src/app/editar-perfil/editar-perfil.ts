import { Component, inject, signal, OnInit, computed } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { PerfilService } from '../services/perfil.service';
import { AuthService } from '../services/auth';
import { PerfilResponse } from '../models/perfil-response';
import { HttpClient } from '@angular/common/http';
import { PAISES } from '../data/paises';
import { TECNOLOGIAS } from '../data/tecnologias';

@Component({
  selector: 'app-editar-perfil',
  imports: [RouterLink],
  templateUrl: './editar-perfil.html',
  styleUrl: './editar-perfil.scss',
})
export class EditarPerfil {
  private perfilService = inject(PerfilService);
  authService = inject(AuthService);
  private http = inject(HttpClient);
  private router = inject(Router);
  
  perfilOriginal = signal<PerfilResponse | null>(null);
  nombre = signal('');
  ciudad = signal('');
  pais = signal('');
  experiencia = signal(0);
  paginaWeb = signal('');
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
    const original = this.perfilOriginal();
    if (!original) return false;
    const nombreCambiado = this.nombre() !== original.nombre;
    const ciudadCambiada = this.ciudad() !== original.ciudad;
    const paisCambiado = this.pais() !== original.pais;
    const experienciaCambiada = this.experiencia() !== (original.experiencia ?? 0);
    const paginaWebCambiada = this.paginaWeb() !== (original.pagina_web ?? '');
    const tecnologiasCambiadas = JSON.stringify([...this.tecnologiasSeleccionadas()].sort()) !== 
                     JSON.stringify([...this.tecnologiasActuales()].sort());
    
    return nombreCambiado || ciudadCambiada || paisCambiado || experienciaCambiada || paginaWebCambiada || tecnologiasCambiadas;
  });
  
  ngOnInit() {
    this.perfilService.getPerfil().subscribe({
      next: (data) => {
        this.perfilOriginal.set(data);
        this.nombre.set(data.nombre);
        this.ciudad.set(data.ciudad);
        this.pais.set(data.pais);
        this.experiencia.set(data.experiencia ?? 0);
        this.paginaWeb.set(data.pagina_web ?? '');
        const paisEncontrado = PAISES.find(p => p.nombre === data.pais);
        if (paisEncontrado) this.paisSeleccionado.set(paisEncontrado);
        this.tecnologiasActuales.set(data.tecnologias ?? []);
        this.tecnologiasSeleccionadas.set(data.tecnologias ?? []);
      },
      error: (err) => console.error('Error al cargar el perfil', err)
    });
  }

  actualizarPerfil() {
    if (!this.perfilOriginal()) return;
    if (!confirm('¿Estás seguro que quieres guardar los cambios?')) return;
    const nuevasTecnologias = this.tecnologiasSeleccionadas()

    const datosActualizados: PerfilResponse = {
      nombre: this.nombre(),
      ciudad: this.ciudad(),
      pais: this.pais(),
      experiencia: this.experiencia(),
      pagina_web: this.paginaWeb(),
      email: this.perfilOriginal()!.email
    };

    this.perfilService.actualizarPerfil(datosActualizados, this.authService.rol()!, this.tecnologiasActuales(), nuevasTecnologias).subscribe({
      next: () => {
        alert('Perfil actualizado con éxito');
        this.tecnologiasActuales.set(nuevasTecnologias);
        this.router.navigate(['/perfil']);
      },
      error: (err) => {
        console.error('Error al actualizar el perfil', err);
        alert('Error al actualizar el perfil');
      }
    });
  }
}
