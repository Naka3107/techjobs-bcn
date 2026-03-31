import sqlite3
from database import inicializar_db, resetear_db, guardar_oferta
from bolsa import Oferta
from auth import registrar_usuario

def seed():
    conn = sqlite3.connect("buscador.db")
    
    # Resetear y recrear tablas
    resetear_db(conn)
    inicializar_db(conn)
    
    cursor = conn.cursor()
    
    # --- EMPRESAS ---
    empresas = [
        {"email": "raona@test.com", "contraseña": "123456", "nombre": "Raona", "ciudad": "Barcelona", "pais": "Spain", "pagina_web": "raona.com"},
        {"email": "sopra@test.com", "contraseña": "123456", "nombre": "Sopra Steria", "ciudad": "Barcelona", "pais": "Spain", "pagina_web": "soprasteria.com"},
        {"email": "ubisoft@test.com", "contraseña": "123456", "nombre": "Ubisoft", "ciudad": "Paris", "pais": "France", "pagina_web": "ubisoft.com"},
        {"email": "nextret@test.com", "contraseña": "123456", "nombre": "NexTReT", "ciudad": "Barcelona", "pais": "Spain", "pagina_web": "nextret.com"},
    ]
    
    empresa_ids = {}
    for e in empresas:
        usuario_id = registrar_usuario(e["email"], e["contraseña"], "empresa", conn)
        cursor.execute(
            "INSERT INTO empresas (usuario_id, nombre, ciudad, pais, pagina_web) VALUES (?, ?, ?, ?, ?)",
            (usuario_id, e["nombre"], e["ciudad"], e["pais"], e["pagina_web"])
        )
        empresa_ids[e["nombre"]] = cursor.lastrowid
    
    # --- OFERTAS ---
    ofertas = [
        # Raona
        {"empresa": "Raona", "puesto": "Python Developer", "salario": 26000, "pais": "Spain", "capital": "Madrid", "tecnologias": ["Python", "SQL", "Git"]},
        {"empresa": "Raona", "puesto": "Backend Junior", "salario": 22000, "pais": "Spain", "capital": "Barcelona", "tecnologias": ["Java", "Spring Boot", "SQL"]},
        {"empresa": "Raona", "puesto": "Data Analyst", "salario": 24000, "pais": "Spain", "capital": "Madrid", "tecnologias": ["Python", "SQL", "Tableau"]},
        {"empresa": "Raona", "puesto": "DevOps Junior", "salario": 28000, "pais": "Spain", "capital": "Barcelona", "tecnologias": ["Docker", "AWS", "Git"]},
        {"empresa": "Raona", "puesto": "Frontend Developer", "salario": 23000, "pais": "Spain", "capital": "Barcelona", "tecnologias": ["JavaScript", "React", "CSS"]},
        # Sopra Steria
        {"empresa": "Sopra Steria", "puesto": "Java Developer", "salario": 25000, "pais": "Germany", "capital": "Berlin", "tecnologias": ["Java", "Spring Boot", "SQL"]},
        {"empresa": "Sopra Steria", "puesto": "Fullstack Developer", "salario": 30000, "pais": "Germany", "capital": "Berlin", "tecnologias": ["JavaScript", "React", "Node"]},
        {"empresa": "Sopra Steria", "puesto": "Cloud Engineer", "salario": 32000, "pais": "France", "capital": "Paris", "tecnologias": ["AWS", "Docker", "Python"]},
        {"empresa": "Sopra Steria", "puesto": "QA Engineer", "salario": 21000, "pais": "Spain", "capital": "Barcelona", "tecnologias": ["Java", "Selenium", "Git"]},
        {"empresa": "Sopra Steria", "puesto": "Data Engineer", "salario": 29000, "pais": "Germany", "capital": "Berlin", "tecnologias": ["Python", "SQL", "Spark"]},
        # Ubisoft
        {"empresa": "Ubisoft", "puesto": "Game Developer", "salario": 35000, "pais": "France", "capital": "Paris", "tecnologias": ["C++", "Python", "Git"]},
        {"empresa": "Ubisoft", "puesto": "Backend Engineer", "salario": 33000, "pais": "France", "capital": "Paris", "tecnologias": ["Python", "Docker", "AWS"]},
        {"empresa": "Ubisoft", "puesto": "Mobile Developer", "salario": 31000, "pais": "Spain", "capital": "Barcelona", "tecnologias": ["Swift", "Kotlin", "Git"]},
        {"empresa": "Ubisoft", "puesto": "ML Engineer", "salario": 38000, "pais": "France", "capital": "Paris", "tecnologias": ["Python", "TensorFlow", "SQL"]},
        {"empresa": "Ubisoft", "puesto": "Frontend Senior", "salario": 34000, "pais": "Spain", "capital": "Barcelona", "tecnologias": ["React", "TypeScript", "CSS"]},
        # NexTReT
        {"empresa": "NexTReT", "puesto": "Systems Administrator", "salario": 24000, "pais": "Spain", "capital": "Barcelona", "tecnologias": ["Linux", "Docker", "AWS"]},
        {"empresa": "NexTReT", "puesto": "Angular Developer", "salario": 27000, "pais": "Spain", "capital": "Barcelona", "tecnologias": ["Angular", "TypeScript", "CSS"]},
        {"empresa": "NexTReT", "puesto": "SQL Developer", "salario": 23000, "pais": "Spain", "capital": "Madrid", "tecnologias": ["SQL", "Python", "Git"]},
        {"empresa": "NexTReT", "puesto": "Node Developer", "salario": 26000, "pais": "Spain", "capital": "Barcelona", "tecnologias": ["Node", "JavaScript", "SQL"]},
        {"empresa": "NexTReT", "puesto": "Security Analyst", "salario": 30000, "pais": "Spain", "capital": "Barcelona", "tecnologias": ["Python", "Linux", "Git"]},
    ]
    
    for o in ofertas:
        empresa_id = empresa_ids[o["empresa"]]
        guardar_oferta(Oferta(
            id=None,
            empresa_id=empresa_id,
            puesto=o["puesto"],
            salario=o["salario"],
            pais=o["pais"],
            capital=o["capital"],
            tecnologias=o["tecnologias"]
        ), conn)
    
    # --- PROGRAMADORES ---
    programadores = [
        {"email": "carlos@test.com", "contraseña": "123456", "nombre": "Carlos", "ciudad": "Barcelona", "pais": "Spain", "años_experiencia": 0, "tecnologias": ["Python", "SQL", "Git"]},
        {"email": "ana@test.com", "contraseña": "123456", "nombre": "Ana", "ciudad": "Madrid", "pais": "Spain", "años_experiencia": 3, "tecnologias": ["Java", "Spring Boot", "SQL"]},
        {"email": "mikel@test.com", "contraseña": "123456", "nombre": "Mikel", "ciudad": "Bilbao", "pais": "Spain", "años_experiencia": 2, "tecnologias": ["JavaScript", "React", "Docker"]},
        {"email": "laura@test.com", "contraseña": "123456", "nombre": "Laura", "ciudad": "Barcelona", "pais": "Spain", "años_experiencia": 5, "tecnologias": ["Python", "TensorFlow", "SQL", "AWS"]},
    ]
        
    for p in programadores:
        usuario_id = registrar_usuario(p["email"], p["contraseña"], "programador", conn)
        cursor.execute(
            "INSERT INTO programadores (usuario_id, nombre, ciudad, pais, años_experiencia) VALUES (?, ?, ?, ?, ?)",
            (usuario_id, p["nombre"], p["ciudad"], p["pais"], p["años_experiencia"])
        )
        programador_id = cursor.lastrowid
        for tec in p["tecnologias"]:
            cursor.execute(
                "INSERT INTO tecnologias_programador (programador_id, tecnologia) VALUES (?, ?)",
                (programador_id, tec)
            )
    
    conn.commit()
    conn.close()
    print("✅ Base de datos poblada correctamente")
    print(f"   {len(empresas)} empresas")
    print(f"   {len(ofertas)} ofertas")
    print(f"   {len(programadores)} programadores")

seed()