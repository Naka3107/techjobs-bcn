# TechJobs

Plataforma full-stack de empleo tecnológico. Conecta empresas con programadores mediante un sistema de compatibilidad basado en tecnologías, experiencia y ubicación.

---

## Índice

1. [Stack tecnológico](#stack-tecnológico)
2. [Arquitectura general](#arquitectura-general)
3. [Backend — Capas](#backend--capas)
4. [Frontend — Capas](#frontend--capas)
5. [Base de datos](#base-de-datos)
6. [Diagrama de flujo de datos](#diagrama-de-flujo-de-datos)
7. [Casos de uso](#casos-de-uso)
8. [API REST](#api-rest)
9. [Algoritmo de compatibilidad](#algoritmo-de-compatibilidad)
10. [Instalación y ejecución](#instalación-y-ejecución)
11. [Datos de prueba](#datos-de-prueba)
12. [Mejoras futuras](#mejoras-futuras)

---

## Stack tecnológico

| Capa | Tecnología |
|------|-----------|
| Frontend | Angular 21, TypeScript, SCSS |
| Backend | Python, Flask, Flask-JWT-Extended |
| Base de datos | SQLite |
| Autenticación | JWT + bcrypt |
| API externa | Nominatim (OpenStreetMap) |

---

## Arquitectura general

```
┌─────────────────────────────────────────────────────────┐
│                     FRONTEND (Angular)                   │
│                                                         │
│  Componentes → Services → HTTP Interceptor → API        │
└─────────────────────────┬───────────────────────────────┘
                          │ HTTP / JSON
                          │
┌─────────────────────────▼───────────────────────────────┐
│                     BACKEND (Flask)                      │
│                                                         │
│  Controller (app.py) → Service (services.py) → DB       │
│                              ↓                          │
│                    Repository (database.py)             │
│                              ↓                          │
│                         SQLite                          │
└─────────────────────────────────────────────────────────┘
```

---

## Backend — Capas

### Controller — `app.py`

Responsabilidad: recibir peticiones HTTP, verificar autenticación/autorización y devolver respuestas JSON.

```
app.py
│
├── GET  /ofertas                    → pública (3 sin token, todas con token)
├── POST /ofertas                    → solo empresa
├── PUT  /ofertas/<id>               → solo empresa (dueña de la oferta)
├── DELETE /ofertas/<id>             → solo empresa (dueña de la oferta)
├── GET  /ofertas/<id>               → solo empresa
├── GET  /ofertas/compatibles        → solo programador
├── GET  /empresas/ofertas           → solo empresa
│
├── GET  /programadores              → solo empresa
├── GET  /programadores/compatibles  → solo empresa
│
├── POST /registro/programador       → pública
├── POST /registro/empresa           → pública
├── POST /login                      → pública
│
├── GET  /perfil                     → autenticado (programador o empresa)
├── PUT  /perfil                     → autenticado
│
└── POST /reset                      → resetea la DB (solo desarrollo)
```

**Flujo de autenticación en cada ruta protegida:**

```
Request HTTP
    │
    ▼
@jwt_required()
    │
    ├── Token inválido → 401
    │
    ▼
get_jwt_identity() → usuario_id
get_jwt()          → { rol: "programador" | "empresa" }
    │
    ├── Rol incorrecto → 403
    │
    ▼
Lógica del endpoint
    │
    ▼
Response JSON
```

---

### Service — `services.py`

Responsabilidad: lógica de negocio. Cálculos derivados que no se persisten en la DB.

```python
calcular_compatibilidad(programador, oferta)
    │
    ├── Tecnologías (60%)
    │     coincidencias / total_tecnologias_oferta * 60
    │
    ├── Experiencia (25%)
    │     cumple → 25pts
    │     no cumple → (experiencia_programador / experiencia_minima) * 25
    │
    └── Ciudad (15%)
          misma ciudad → 15pts
          mismo país   → 7pts
          diferente    → 0pts
```

---

### Repository — `database.py`

Responsabilidad: únicamente queries SQL y construcción de objetos del dominio.

```
database.py
│
├── inicializar_db(conn)
├── resetear_db(conn)
│
├── guardar_oferta(oferta, conn)
├── modificar_oferta(oferta_id, datos, conn)
├── cargar_ofertas(conn)
├── cargar_oferta(oferta_id, conn)
├── cargar_ofertas_empresa(empresa_id, conn)         [via cargar_ofertas + filtro]
│
├── guardar_programador(programador, conn)
├── cargar_programadores(conn)
├── buscar_programadores_compatibles(oferta_id, conn, ...)
│
├── buscar_ofertas_compatibles(programador_id, conn, ...)
│
├── _construir_oferta_desde_db(oferta_db, tecnologias_db)     [privado]
└── _construir_programador_desde_db(programador_db, tecs_db)  [privado]
```

**Clases del dominio — `bolsa.py`:**

```
Usuario
  ├── id
  ├── email
  └── rol

Programador
  ├── id
  ├── usuario_id
  ├── nombre
  ├── ciudad
  ├── pais
  ├── experiencia
  └── tecnologias[]

Empresa
  ├── id
  ├── usuario_id
  ├── nombre
  ├── ciudad
  ├── pais
  └── pagina_web

Oferta
  ├── id
  ├── empresa_id
  ├── nombre_empresa
  ├── puesto
  ├── salario
  ├── experiencia_minima
  ├── pais
  ├── ciudad
  └── tecnologias[]
```

---

## Frontend — Capas

### Estructura de archivos

```
src/app/
│
├── app.config.ts          → providers: HttpClient, Router, Interceptors
├── app.routes.ts          → definición de rutas
├── app.ts / app.html      → navbar dinámica según rol
│
├── components/
│   ├── bienvenida/
│   ├── lista-ofertas/     → vista pública + empresa (mis ofertas)
│   ├── buscador/          → filtros según rol
│   ├── perfil/            → ver perfil
│   ├── editar-perfil/     → editar perfil
│   ├── login/
│   ├── registro/
│   ├── nueva-oferta/
│   ├── editar-oferta/
│   ├── oferta-card/       → componente reutilizable (modo lista|tarjeta)
│   └── programador-card/  → componente reutilizable con compatibilidad
│
├── services/
│   ├── auth.ts            → sesión, login, registro
│   ├── oferta.service.ts  → CRUD ofertas, compatibilidad programador
│   ├── perfil.service.ts  → GET/PUT perfil
│   └── programador.ts     → GET programadores, compatibilidad empresa
│
├── guards/
│   └── auth-guard.ts      → protege rutas privadas
│
├── interceptors/
│   └── auth-interceptor.ts → añade Bearer token a todas las peticiones
│
├── models/
│   ├── oferta.ts
│   ├── programador.ts
│   ├── empresa.ts
│   ├── perfil-response.ts
│   └── programador-response.ts
│
└── data/
    ├── paises.ts          → lista estática de países
    └── tecnologias.ts     → lista estática de tecnologías
```

### Flujo de datos — Login

```
Login Component
    │
    │ email + password
    ▼
AuthService.login()
    │
    │ POST /login
    ▼
Flask /login
    │
    │ { token, rol, usuario_id }
    ▼
AuthService.guardarSesion()
    │
    │ token.set(), rol.set(), usuarioId.set()
    ▼
Signals en memoria
    │
    ├── AuthGuard lee token() → permite/bloquea rutas
    ├── AuthInterceptor lee token() → añade a cada petición HTTP
    └── Navbar lee rol() → muestra opciones según rol
```

### Flujo de datos — Petición autenticada

```
Componente
    │
    │ service.getData()
    ▼
Service
    │
    │ http.get('/endpoint')
    ▼
AuthInterceptor
    │
    │ req.clone({ headers: Authorization: Bearer {token} })
    ▼
Flask API
    │
    │ @jwt_required() → verifica token
    │ get_jwt_identity() → usuario_id
    │ get_jwt() → rol
    ▼
database.py → SQLite
    │
    │ JSON response
    ▼
Componente → actualiza signals → Angular re-renderiza
```

### Services

**`AuthService`**
```typescript
token     = signal<string | null>(null)
rol       = signal<string | null>(null)
usuarioId = signal<number | null>(null)

login(email, password)         → Observable
registrarProgramador(datos)    → Observable
registrarEmpresa(datos)        → Observable
guardarSesion(token, rol, id)  → void
cerrarSesion()                 → void
estaAutenticado()              → boolean
esProgramador()                → boolean
esEmpresa()                    → boolean
```

**`OfertaService`**
```typescript
getOfertas()                                    → Observable<Oferta[]>
getOfertasEmpresa()                             → Observable<Oferta[]>
getOfertasCompatibles(salario?, pais?, exp?)    → Observable<Oferta[]>
getOferta(id)                                   → Observable<Oferta>
crearOferta(datos)                              → Observable
actualizarOferta(id, datos)                     → Observable
eliminarOferta(id)                              → Observable
```

**`PerfilService`**
```typescript
getPerfil()                                     → Observable<PerfilResponse>
actualizarPerfil(datos, rol, tecnologias)       → Observable
```

**`ProgramadorService`**
```typescript
getProgramadores()                              → Observable<Programador[]>
getProgramadoresCompatibles(ofertaId, exp?, ciudad?) → Observable<ProgramadorResponse[]>
```

### Componentes reutilizables

**`OfertaCard`**
```typescript
oferta = input.required<Oferta>()
modo   = input<'lista' | 'tarjeta'>('tarjeta')
abierta = signal(false)
toggle()
```

**`ProgramadorCard`**
```typescript
programador = input.required<ProgramadorResponse>()
modo        = input<'lista' | 'tarjeta'>('tarjeta')
abierta     = signal(false)
toggle()
```

---

## Base de datos

### Esquema

```
usuarios
  ├── id (PK)
  ├── email (UNIQUE)
  ├── contraseña_hash
  └── rol ('programador' | 'empresa')

programadores
  ├── id (PK)
  ├── usuario_id (FK → usuarios)
  ├── nombre
  ├── ciudad
  ├── pais
  └── experiencia

tecnologias_programador
  ├── id (PK)
  ├── programador_id (FK → programadores)
  └── tecnologia

empresas
  ├── id (PK)
  ├── usuario_id (FK → usuarios)
  ├── nombre
  ├── ciudad
  ├── pais
  └── pagina_web

ofertas
  ├── id (PK)
  ├── empresa_id (FK → empresas)
  ├── puesto
  ├── salario
  ├── pais
  ├── ciudad
  └── experiencia_minima

tecnologias_oferta
  ├── id (PK)
  ├── oferta_id (FK → ofertas)
  └── tecnologia
```

### Relaciones

```
usuarios ──< programadores ──< tecnologias_programador
usuarios ──< empresas ──< ofertas ──< tecnologias_oferta
```

---

## Diagrama de flujo de datos

### Registro programador

```
Formulario registro
    │ { email, password, nombre, ciudad, pais, experiencia, tecnologias[] }
    ▼
POST /registro/programador
    │
    ├── registrar_usuario() → INSERT usuarios → usuario_id
    ├── INSERT programadores (usuario_id, nombre, ciudad, pais, experiencia)
    └── INSERT tecnologias_programador (x N tecnologías)
    │
    ▼
{ mensaje: "Programador registrado correctamente" } 201
```

### Búsqueda de ofertas compatibles (programador)

```
Buscador component
    │ { salario_minimo?, pais?, experiencia_minima? }
    ▼
OfertaService.getOfertasCompatibles()
    │
    │ GET /ofertas/compatibles?salario_minimo=&pais=&experiencia_minima=
    ▼
Flask → buscar_ofertas_compatibles()
    │
    ├── SELECT tecnologias del programador
    ├── SELECT DISTINCT ofertas WHERE tecnologia IN (tecs_programador)
    │     AND salario >= salario_minimo (opcional)
    │     AND pais = pais (opcional)
    │     AND experiencia_minima <= experiencia (opcional)
    └── _construir_oferta_desde_db()
    │
    ▼
Oferta[] ordenadas por relevancia
```

### Búsqueda de programadores compatibles (empresa)

```
Buscador component
    │ { oferta_id, experiencia?, ciudad? }
    ▼
ProgramadorService.getProgramadoresCompatibles()
    │
    │ GET /programadores/compatibles?oferta_id=&experiencia=&ciudad=
    ▼
Flask
    │
    ├── buscar_programadores_compatibles(oferta_id)
    │     SELECT DISTINCT programadores WHERE tecnologia IN (tecs_oferta)
    │
    ├── cargar_oferta(oferta_id)
    │
    └── por cada programador:
          calcular_compatibilidad(programador, oferta)
              ├── tecnologías: coincidentes / faltantes
              ├── experiencia: cumple o no
              └── ciudad: misma ciudad / mismo país / diferente
    │
    ▼
sorted(resultados, key=porcentaje, reverse=True)
    │
    ▼
ProgramadorResponse[] con desglose de compatibilidad
```

---

## Casos de uso

### Programador

```
Programador
    │
    ├── Registro → /registro/programador
    ├── Login → /login → redirige a /buscador
    │
    ├── Ver ofertas públicas (3) → /ofertas (sin token)
    ├── Ver todas las ofertas → /ofertas (con token)
    │
    ├── Buscar ofertas compatibles → /buscador
    │     └── Filtros: salario mínimo, país, experiencia
    │
    ├── Ver perfil → /perfil
    └── Editar perfil → /editar-perfil
          └── nombre, ciudad, país, experiencia, tecnologías
```

### Empresa

```
Empresa
    │
    ├── Registro → /registro/empresa
    ├── Login → /login → redirige a /ofertas
    │
    ├── Ver mis ofertas → /ofertas
    │     ├── Publicar nueva oferta → /ofertas/nueva
    │     ├── Editar oferta → /ofertas/editar/:id
    │     └── Eliminar oferta (inline)
    │
    ├── Buscar programadores compatibles → /buscador
    │     ├── Seleccionar oferta específica
    │     ├── Filtros: experiencia mínima, ciudad
    │     └── Ver desglose de compatibilidad por programador
    │
    ├── Ver perfil → /perfil
    └── Editar perfil → /editar-perfil
          └── nombre, ciudad, país, página web
```

---

## API REST

| Método | Ruta | Auth | Rol | Descripción |
|--------|------|------|-----|-------------|
| GET | /ofertas | Opcional | — | Lista ofertas (3 sin token) |
| POST | /ofertas | ✓ | empresa | Crear oferta |
| GET | /ofertas/:id | ✓ | empresa | Obtener oferta por id |
| PUT | /ofertas/:id | ✓ | empresa | Actualizar oferta |
| DELETE | /ofertas/:id | ✓ | empresa | Eliminar oferta |
| GET | /ofertas/compatibles | ✓ | programador | Ofertas compatibles con filtros |
| GET | /empresas/ofertas | ✓ | empresa | Mis ofertas |
| GET | /programadores | ✓ | empresa | Lista programadores |
| GET | /programadores/compatibles | ✓ | empresa | Programadores compatibles con desglose |
| POST | /registro/programador | — | — | Registro programador |
| POST | /registro/empresa | — | — | Registro empresa |
| POST | /login | — | — | Login → JWT |
| GET | /perfil | ✓ | ambos | Ver perfil según rol |
| PUT | /perfil | ✓ | ambos | Actualizar perfil + tecnologías |

---

## Algoritmo de compatibilidad

El algoritmo calcula un porcentaje de compatibilidad entre un programador y una oferta específica. Vive en `services.py` — separado de la capa de datos y de los endpoints HTTP.

```
Compatibilidad total (0-100%)
│
├── Tecnologías — 60%
│     puntos = (tecnologías_coincidentes / tecnologías_oferta) * 60
│
├── Experiencia — 25%
│     cumple (experiencia >= experiencia_minima) → 25 puntos
│     no cumple → (experiencia_programador / experiencia_minima) * 25
│
└── Ciudad — 15%
      misma ciudad → 15 puntos
      mismo país   → 7 puntos
      diferente    → 0 puntos
```

**Respuesta del algoritmo:**

```json
{
  "porcentaje": 78,
  "desglose": {
    "tecnologias_coincidentes": ["Python", "SQL"],
    "tecnologias_faltantes": ["Docker"],
    "experiencia_cumple": true,
    "ciudad_cumple": false,
    "pais_cumple": true
  }
}
```

Los resultados se devuelven **ordenados de mayor a menor compatibilidad**.

---

## Instalación y ejecución

### Requisitos

- Python 3.12+
- Node.js 20+ (incluye npm)
- Angular CLI (`npm install -g @angular/cli`)

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux
pip install flask flask-cors flask-jwt-extended bcrypt
python seed.py                # poblar la base de datos
python app.py                 # arrancar el servidor en localhost:5000
```

### Frontend

```bash
cd frontend
npm install
ng serve                      # arrancar en localhost:4200
```

---

## Datos de prueba

Ejecuta `python seed.py` para poblar la base de datos con:

- **5 empresas** — Raona, Sopra Steria, Ubisoft, NexTReT, ThoughtWorks
- **25 ofertas** — distribuidas entre las empresas con distintos países, salarios y tecnologías
- **15 programadores** — con distintas experiencias, ciudades y tecnologías

**Credenciales de prueba** (todas con contraseña `123456`):

| Email | Tipo |
|-------|------|
| carlos@test.com | Programador |
| ana@test.com | Programador |
| mikel@test.com | Programador |
| laura@test.com | Programador |
| raona@test.com | Empresa |
| sopra@test.com | Empresa |
| ubisoft@test.com | Empresa |

---

## Mejoras futuras

- **Persistencia de sesión** — localStorage + refresh tokens para mantener sesión al recargar
- **Mis ofertas guardadas** — programadores pueden guardar ofertas de interés y hacer seguimiento
- **Contador de aplicaciones** — empresas ven cuántos programadores han solicitado info de cada oferta
- **Variables de entorno** — `JWT_SECRET_KEY` en `.env` en lugar de hardcodeada
- **Validación en Flask** — validar datos del request en el backend, no solo en el frontend
- **Migrar a PostgreSQL** — para entornos de producción
- **Despliegue** — backend en Railway/Render, frontend en Vercel/Netlify
- **País en múltiples idiomas** — aceptar nombres de países en inglés y español indistintamente
- **Refactorizar lógica de tecnologías** — extraer `toggleTecnologia`, `agregarOtra` a un servicio compartido
- **Tests** — tests unitarios en Python (pytest) y Angular (Jasmine)

## Autor

Santiago Nakakawa — Ingeniero en Sistemas Computacionales  
Barcelona, España  
[GitHub](https://github.com/Naka3107)
