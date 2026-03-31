import sqlite3
from bolsa import Programador, Oferta

def inicializar_db(conn):
    # Conectar — crea el archivo si no existe
    cursor = conn.cursor()

    # Ejecutar SQL
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        contraseña_hash TEXT NOT NULL,
        rol TEXT NOT NULL
        );
                         
    CREATE TABLE IF NOT EXISTS empresas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        nombre TEXT NOT NULL,
        ciudad TEXT NOT NULL,
        pais TEXT NOT NULL,
        pagina_web TEXT NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );

    CREATE TABLE IF NOT EXISTS programadores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        nombre TEXT NOT NULL,
        ciudad TEXT NOT NULL,
        pais TEXT NOT NULL,
        años_experiencia INTEGER NOT NULL,
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        );

    CREATE TABLE IF NOT EXISTS tecnologias_programador (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        programador_id INTEGER NOT NULL,
        tecnologia TEXT NOT NULL,
        FOREIGN KEY (programador_id) REFERENCES programadores(id)
        );
                         
    CREATE TABLE IF NOT EXISTS ofertas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        empresa_id INTEGER NOT NULL,
        puesto TEXT NOT NULL,
        salario INTEGER NOT NULL,
        pais TEXT,
        capital TEXT,
        FOREIGN KEY (empresa_id) REFERENCES empresas(id)
        );
    
    CREATE TABLE IF NOT EXISTS tecnologias_oferta (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        oferta_id INTEGER NOT NULL,
        tecnologia TEXT NOT NULL,
        FOREIGN KEY (oferta_id) REFERENCES ofertas(id)
        );                 
    """)
    
def guardar_oferta(oferta, conn):

    cursor = conn.cursor()

    cursor.execute(
    "INSERT INTO ofertas (empresa_id, puesto, salario, pais, capital) VALUES (?, ?, ?, ?, ?)",
    (oferta.empresa_id, oferta.puesto, oferta.salario, oferta.pais, oferta.capital)
    )
    oferta_id = cursor.lastrowid
    for tecnologia in oferta.tecnologias:
        cursor.execute(
        "INSERT INTO tecnologias_oferta (oferta_id, tecnologia) VALUES (?, ?)",
        (oferta_id, tecnologia)
        )

def guardar_programador(programador,conn):

    cursor = conn.cursor()

    cursor.execute(
    "INSERT INTO programadores (nombre, ciudad, pais, años_experiencia) VALUES (?, ?, ?, ?)",
    (programador.nombre, programador.ciudad, programador.pais, programador.años_experiencia)
    )
    programador_id = cursor.lastrowid
    for tecnologia in programador.tecnologias:
        cursor.execute(
        "INSERT INTO tecnologias_programador (programador_id, tecnologia) VALUES (?, ?)",
        (programador_id, tecnologia)
        )

def _construir_oferta_desde_db(oferta_db, tecnologias_db):
    resultados = []
    for oferta in oferta_db:
        tecnologias = [t[2] for t in tecnologias_db if t[1] == oferta[0]] # t[1] es oferta_id en tecnologias_oferta, oferta[0] es id en ofertas
        oferta = Oferta(
            id=oferta[0],
            empresa_id=oferta[1],
            puesto=oferta[2],
            salario=oferta[3],
            pais=oferta[4],
            capital=oferta[5],
            nombre_empresa=oferta[6],
            tecnologias=tecnologias
        )
        resultados.append(oferta)
    return resultados

def _construir_programador_desde_db(programador_db, tecnologias_db):
    programadores = []
    for programador in programador_db:
        tecnologias = [t[2] for t in tecnologias_db if t[1] == programador[0]] # t[1] es programador_id en tecnologias_programador, programador[0] es id en programadores
        programador = Programador(
            id=programador[0],
            usuario_id=programador[1],
            nombre=programador[2],
            ciudad=programador[3],
            pais=programador[4],
            años_experiencia=programador[5],
            tecnologias=tecnologias
        )
        programadores.append(programador)
    return programadores

def cargar_ofertas(conn):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.*, e.nombre as nombre_empresa
        FROM ofertas o
        JOIN empresas e ON e.id = o.empresa_id
    """)
    ofertas_db = cursor.fetchall()  # devuelve lista de tuplas
    cursor.execute("SELECT * FROM tecnologias_oferta")
    tecnologias_db = cursor.fetchall()
    return _construir_oferta_desde_db(ofertas_db, tecnologias_db)

def cargar_programadores(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM programadores")
    programadores_db = cursor.fetchall()
    cursor.execute("SELECT * FROM tecnologias_programador")
    tecnologias_db = cursor.fetchall()
    return _construir_programador_desde_db(programadores_db, tecnologias_db)

def buscar_ofertas_compatibles(programador_id, conn, salario_minimo=None, pais=None):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tecnologia FROM tecnologias_programador WHERE programador_id = ?
        """, (programador_id,))
    tecnologias_programador = [row[0] for row in cursor.fetchall()]

    if not tecnologias_programador:
        return []  # El programador no tiene tecnologías registradas
    
    placeholders = ','.join('?' for _ in tecnologias_programador)
    query = f"""
        SELECT DISTINCT o.*, e.nombre as nombre_empresa
        FROM ofertas o
        JOIN empresas e ON e.id = o.empresa_id
        JOIN tecnologias_oferta tof ON tof.oferta_id = o.id
        WHERE tof.tecnologia IN ({placeholders})
        """
    
    params = list(tecnologias_programador)

    if salario_minimo:
        query += " AND o.salario >= ?"
        params.append(salario_minimo)

    if pais:
        query += " AND o.pais = ?"
        params.append(pais)

    query += " GROUP BY o.id"

    cursor.execute(query, params)
    ofertas_db = cursor.fetchall() # Resultado del query, lista de tuplas con las ofertas compatibles
    # Crear objetos Oferta a partir de los resultados y devolverlos
    
    # Cargar todas las tecnologías de las ofertas encontradas
    oferta_ids = [o[0] for o in ofertas_db]
    if not oferta_ids:
        return []

    placeholders_ids = ','.join('?' for _ in oferta_ids)
    cursor.execute(f"SELECT * FROM tecnologias_oferta WHERE oferta_id IN ({placeholders_ids})", oferta_ids)
    tecnologias_db = cursor.fetchall()

    return _construir_oferta_desde_db(ofertas_db, tecnologias_db)

def buscar_programadores_compatibles(oferta_id, conn, años_experiencia_minimo=None, ciudad=None):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT tecnologia FROM tecnologias_oferta WHERE oferta_id = ?
        """, (oferta_id,))
    
    tecnologias_oferta = [row[0] for row in cursor.fetchall()]

    if not tecnologias_oferta:
        return []  
    
    placeholders = ','.join('?' for _ in tecnologias_oferta)
    query = f"""
        SELECT DISTINCT p.*
        FROM programadores p
        JOIN tecnologias_programador tp ON tp.programador_id = p.id
        WHERE tp.tecnologia IN ({placeholders})
        """
    
    params = list(tecnologias_oferta)

    if años_experiencia_minimo:
        query += " AND p.años_experiencia >= ?"
        params.append(años_experiencia_minimo)

    if ciudad:
        query += " AND p.ciudad = ?"
        params.append(ciudad)

    query += " GROUP BY p.id"

    cursor.execute(query, params)
    programadores_db = cursor.fetchall()

    # Crear objetos Programador a partir de los resultados y devolverlos
    # Cargar todas las tecnologías de los programadores encontrados
    programador_ids = [p[0] for p in programadores_db]
    if not programador_ids:
        return []
    placeholders_ids = ','.join('?' for _ in programador_ids)
    cursor.execute(f"SELECT * FROM tecnologias_programador WHERE programador_id IN ({placeholders_ids})", programador_ids)
    tecnologias_db = cursor.fetchall()

    return _construir_programador_desde_db(programadores_db, tecnologias_db)

def resetear_db(conn):
    conn.executescript("""
        DROP TABLE IF EXISTS tecnologias_oferta;
        DROP TABLE IF EXISTS ofertas;               
        DROP TABLE IF EXISTS tecnologias_programador;
        DROP TABLE IF EXISTS programadores;
        DROP TABLE IF EXISTS empresas;
        DROP TABLE IF EXISTS usuarios;
    """)
    conn.commit()
