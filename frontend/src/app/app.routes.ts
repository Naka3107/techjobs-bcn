import { Routes } from '@angular/router';
import { Buscador } from './buscador/buscador';
import { ListaOfertas } from './lista-ofertas/lista-ofertas';
import { Perfil } from './perfil/perfil';
import { EditarPerfil } from './editar-perfil/editar-perfil';
import { Bienvenida } from './bienvenida/bienvenida';
import { NuevaOferta } from './nueva-oferta/nueva-oferta';
import { EditarOferta } from './editar-oferta/editar-oferta';
import { Login } from './login/login';
import { Registro } from './registro/registro';
import { authGuard } from './guards/auth-guard';

export const routes: Routes = [
  { path: '', component: Bienvenida },
  { path: 'ofertas', component: ListaOfertas },
  { path: 'buscador', component: Buscador, canActivate: [authGuard] },
  { path: 'perfil', component: Perfil, canActivate: [authGuard] },
  { path: 'editar-perfil', component: EditarPerfil, canActivate: [authGuard] },
  { path: 'ofertas/nueva', component: NuevaOferta, canActivate: [authGuard] },
  { path: 'ofertas/editar/:id', component: EditarOferta, canActivate: [authGuard] },
  { path: 'login', component: Login },       
  { path: 'registro', component: Registro },  
  { path: '**', redirectTo: '' } 
];