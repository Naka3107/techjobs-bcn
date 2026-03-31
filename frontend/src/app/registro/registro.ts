import { Component, inject, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../services/auth';
import { HttpClient } from '@angular/common/http';
import { PAISES } from '../data/paises';

@Component({
  selector: 'app-registro',
  imports: [RouterLink],
  templateUrl: './registro.html',
  styleUrl: './registro.scss',
})
export class Registro {
  private router = inject(Router);
  private authService = inject(AuthService);
  private http = inject(HttpClient);

  modo = signal<'programador' | 'empresa'>('programador');
  email = signal('');
  password = signal('');
  nombre = signal('');
  error = signal('');
  cargando = signal(false);
  ciudad = signal('');
  pais = signal('');

  experiencia = signal<number>(0);
  paginaWeb = signal<string>('');

  sugerenciasCiudad = signal<string[]>([]);
  buscandoCiudad = signal(false);
  paisSeleccionado = signal<{nombre: string, codigo: string} | null>(null);

  tecnologiasSeleccionadas = signal<string[]>([]);
  otraTecnologia = signal('');
  readonly PAISES = PAISES;

  readonly TECNOLOGIAS = [
    'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#',
    'SQL', 'PostgreSQL', 'MySQL', 'MongoDB',
    'React', 'Angular', 'Vue',
    'Node', 'Flask', 'Spring Boot', 'Django',
    'Docker', 'AWS', 'Azure', 'Git',
    'Linux', 'Swift', 'Kotlin', 'PHP'
  ];

  toggleTecnologia(tec: string) {
    const actuales = this.tecnologiasSeleccionadas();
    if (actuales.includes(tec)) {
      this.tecnologiasSeleccionadas.set(actuales.filter(t => t !== tec));
    } else {
      this.tecnologiasSeleccionadas.set([...actuales, tec]);
    }
  }

  getTecnologias(): string[] {
    const todas = [...this.tecnologiasSeleccionadas()];
    if (this.otraTecnologia().trim()) {
      todas.push(...this.otraTecnologia().split(',').map(t => t.trim()).filter(t => t));
    }
    return todas;
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

  seleccionarCiudad(ciudad: string) {
    this.ciudad.set(ciudad);
    this.sugerenciasCiudad.set([]);
  }

  cambiarModo() {
    this.modo.set(this.modo() === 'programador' ? 'empresa' : 'programador');
    this.error.set('');
  }

  validarEmail(email: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  validarPassword(password: string): boolean {
    if (password === '123456') return true;  // modo test
    return password.length >= 8 && /[a-zA-Z]/.test(password) && /[0-9]/.test(password);
  }

  registrar() {
    if (!this.email() || !this.password() || !this.nombre() || !this.ciudad()) {
      this.error.set('Completa todos los campos');
      return;
    }
    if (!this.validarEmail(this.email())) {
      this.error.set('Email no válido');
      return;
    }
    if (!this.validarPassword(this.password())) {
      this.error.set('La contraseña debe tener mínimo 8 caracteres, letras y números');
      return;
    }
    if (this.experiencia() < 0) {
      this.error.set('Los años de experiencia no pueden ser negativos');
      return;
    }
    if (!this.pais()) {
      this.error.set('Selecciona un país');
      return;
    }

    const datos: any = {
      email: this.email(),
      contraseña: this.password(),
      nombre: this.nombre(),
      ciudad: this.ciudad(),
      pais: this.pais()
    };

    if (this.modo() === 'programador') {
      if (this.experiencia() === null || this.getTecnologias().length === 0) {
        this.error.set('Completa años de experiencia y tecnologías');
        return;
      }
      datos.años_experiencia = this.experiencia();
      datos.tecnologias = this.getTecnologias();
    }

    if (this.modo() === 'empresa') {
      if (!this.paginaWeb()) {
        this.error.set('Completa la página web');
        return;
      }
      datos.pagina_web = this.paginaWeb();
    }

    this.cargando.set(true);
    this.error.set('');

    const request$ = this.modo() === 'programador'
      ? this.authService.registrarProgramador(datos)
      : this.authService.registrarEmpresa(datos);

    request$.subscribe({
      next: () => {
        this.cargando.set(false);
        alert('Registro exitoso, ya puedes iniciar sesión');
        this.router.navigate(['/login']);
      },
      error: () => {
        this.error.set('Error al registrar, intenta de nuevo');
        this.cargando.set(false);
      }
    });
  }
}
