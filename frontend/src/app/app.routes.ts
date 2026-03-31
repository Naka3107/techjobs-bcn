import { Routes } from '@angular/router';
import { Buscador } from './buscador/buscador';
import { ListaOfertas } from './lista-ofertas/lista-ofertas';
import { Bienvenida } from './bienvenida/bienvenida';
import { Login } from './login/login';
import { Registro } from './registro/registro';
import { authGuard } from './guards/auth-guard';

export const routes: Routes = [
  { path: '', component: Bienvenida },
  { path: 'ofertas', component: ListaOfertas },
  { path: 'buscador', component: Buscador, canActivate: [authGuard] },
  { path: 'login', component: Login },       
  { path: 'registro', component: Registro },  
  { path: '**', redirectTo: '' } 
];