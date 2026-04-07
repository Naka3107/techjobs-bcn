from flask  import Flask, jsonify, render_template, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_jwt
import sqlite3
from database import inicializar_db, cargar_ofertas, cargar_oferta, modificar_oferta, cargar_programadores, guardar_oferta, guardar_programador, buscar_ofertas_compatibles, buscar_programadores_compatibles, buscar_programadores_compatibles_empresa, resetear_db
from bolsa import Oferta, Programador, Empresa
from auth import registrar_usuario, login_usuario
from services import calcular_compatibilidad

app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = "techjobs-bcn-secret-key-2026"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 86400  # 24 horas en segundos
jwt = JWTManager(app)

def get_conn():
    conn = sqlite3.connect("buscador.db", timeout=10)
    return conn
    
@app.route("/")
def iniciar():
    return render_template("index.html")

@app.route("/ofertas", methods=["GET"])
@jwt_required(optional=True)  # token opcional — no falla si no hay token
def get_ofertas():
    identity = get_jwt_identity()  # None si no hay token
    claims = get_jwt()             # {} si no hay token
    conn = get_conn()
    ofertas = cargar_ofertas(conn)
    conn.close()
    # Si no hay token o no es programador, devuelve solo 3
    if not identity or claims.get("rol") != "programador":
        ofertas = ofertas[:3]
    return jsonify([vars(o) for o in ofertas])

@app.route("/ofertas/<int:oferta_id>", methods=["GET"])
@jwt_required()
def get_oferta(oferta_id):
    identity = int(get_jwt_identity())
    claims = get_jwt()
    rol = claims.get("rol")
    if rol != "empresa":
        return jsonify({"error": "Solo las empresas pueden ver sus ofertas"}), 403
    conn = get_conn()

    empresa_id = conn.cursor().execute("SELECT id FROM empresas WHERE usuario_id = ?", (identity,)).fetchone()
    if not empresa_id:
        conn.close()
        return jsonify({"error": "Empresa no encontrada para el usuario autenticado"}), 404   
    empresa_id = empresa_id[0]

    oferta_empresa_id = conn.cursor().execute("SELECT empresa_id FROM ofertas WHERE id = ?", (oferta_id,)).fetchone()
    if not oferta_empresa_id:
        conn.close()
        return jsonify({"error": "Oferta no encontrada"}), 404
    oferta_empresa_id = oferta_empresa_id[0]

    if oferta_empresa_id != empresa_id:
        conn.close()
        return jsonify({"error": "No puedes ver una oferta que no es tuya"}), 403

    oferta = cargar_oferta(oferta_id, conn)
    conn.close()
    return jsonify(vars(oferta)), 200

@app.route("/ofertas", methods=["POST"])
@jwt_required()  # token obligatorio
def post_ofertas():
    identity = int(get_jwt_identity())
    claims = get_jwt()
    rol = claims.get("rol")
    if rol != "empresa":
        return jsonify({"error": "Solo las empresas pueden añadir ofertas"}), 403
    datos = request.get_json()
    conn = get_conn()

    empresa_id = conn.cursor().execute("SELECT id FROM empresas WHERE usuario_id = ?", (identity,)).fetchone()
    if not empresa_id:
        conn.close()
        return jsonify({"error": "Empresa no encontrada para el usuario autenticado"}), 404   
    empresa_id = empresa_id[0]  # extrae el id del resultado
    for oferta in datos:
        guardar_oferta(Oferta(id=None, empresa_id=empresa_id, nombre_empresa="", **oferta),conn)
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Ofertas añadidas correctamente"}), 201

@app.route("/ofertas/<int:oferta_id>", methods=["PUT"])
@jwt_required()  # token obligatorio
def put_oferta(oferta_id):
    identity = int(get_jwt_identity())
    claims = get_jwt()
    rol = claims.get("rol")
    if rol != "empresa":
        return jsonify({"error": "Solo las empresas pueden modificar ofertas"}), 403
    datos = request.get_json()
    conn = get_conn()

    empresa_id = conn.cursor().execute("SELECT id FROM empresas WHERE usuario_id = ?", (identity,)).fetchone()
    if not empresa_id:
        conn.close()
        return jsonify({"error": "Empresa no encontrada para el usuario autenticado"}), 404   
    empresa_id = empresa_id[0]

    oferta_empresa_id = conn.cursor().execute("SELECT empresa_id FROM ofertas WHERE id = ?", (oferta_id,)).fetchone()
    if not oferta_empresa_id:
        conn.close()
        return jsonify({"error": "Oferta no encontrada"}), 404
    oferta_empresa_id = oferta_empresa_id[0]

    if oferta_empresa_id != empresa_id:
        conn.close()
        return jsonify({"error": "No puedes modificar una oferta que no es tuya"}), 403
    
    modificar_oferta(oferta_id, datos, conn)
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Oferta modificada correctamente"}), 200

@app.route("/ofertas/<int:oferta_id>", methods=["DELETE"])
@jwt_required()  # token obligatorio
def delete_oferta(oferta_id):
    identity = int(get_jwt_identity())
    claims = get_jwt()
    rol = claims.get("rol")
    if rol != "empresa":
        return jsonify({"error": "Solo las empresas pueden eliminar ofertas"}), 403
    conn = get_conn()

    empresa_id = conn.cursor().execute("SELECT id FROM empresas WHERE usuario_id = ?", (identity,)).fetchone()
    if not empresa_id:
        conn.close()
        return jsonify({"error": "Empresa no encontrada para el usuario autenticado"}), 404   
    empresa_id = empresa_id[0]  # extrae el id del resultado

    oferta_empresa_id = conn.cursor().execute("SELECT empresa_id FROM ofertas WHERE id = ?", (oferta_id,)).fetchone()
    if not oferta_empresa_id:
        conn.close()
        return jsonify({"error": "Oferta no encontrada"}), 404
    oferta_empresa_id = oferta_empresa_id[0]

    if oferta_empresa_id != empresa_id:
        conn.close()
        return jsonify({"error": "No puedes eliminar una oferta que no es tuya"}), 403
    
    conn.cursor().execute("DELETE FROM ofertas WHERE id = ?", (oferta_id,))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Oferta eliminada correctamente"}), 200

@app.route("/ofertas/compatibles", methods=["GET"])
@jwt_required()  # token obligatorio
def get_ofertas_compatibles():
    identity = int(get_jwt_identity())
    claims = get_jwt()
    rol = claims.get("rol")
    if rol != "programador":
        return jsonify({"error": "Solo los programadores pueden buscar ofertas compatibles"}), 403
    conn = get_conn()

    programador_id = conn.cursor().execute("SELECT id FROM programadores WHERE usuario_id = ?", (identity,)).fetchone()
    if not programador_id:
        conn.close()
        return jsonify({"error": "Programador no encontrado para el usuario autenticado"}), 404
    programador_id = programador_id[0]  # extrae el id del resultado
    ofertas = buscar_ofertas_compatibles(programador_id, conn, salario_minimo=request.args.get("salario_minimo"), pais=request.args.get("pais"))
    conn.close()
    return jsonify([vars(o) for o in ofertas])

@app.route("/programadores", methods=["GET"])
@jwt_required()  # token obligatorio
def get_programadores():
    identity = int(get_jwt_identity())
    claims = get_jwt()
    rol = claims.get("rol")
    if rol != "empresa":
        return jsonify({"error": "Solo las empresas pueden ver los programadores"}), 403
    
    conn = get_conn()
    programadores = cargar_programadores(conn)
    conn.close()
    resultados = [vars(programador) for programador in programadores]
    return jsonify(resultados)

@app.route("/programadores/compatibles", methods=["GET"])
@jwt_required()  # token obligatorio
def get_programadores_compatibles():
    identity = int(get_jwt_identity())
    claims = get_jwt()
    rol = claims.get("rol")
    if rol != "empresa":
        return jsonify({"error": "Solo las empresas pueden buscar programadores compatibles"}), 403
    conn = get_conn()
    
    empresa_id = conn.cursor().execute("SELECT id FROM empresas WHERE usuario_id = ?", (identity,)).fetchone()
    if not empresa_id:
        conn.close()
        return jsonify({"error": "Empresa no encontrada para el usuario autenticado"}), 404
    empresa_id = empresa_id[0]  # extrae el id del resultado

    oferta_id = request.args.get("oferta_id")
    if not oferta_id: # Busca compatibilidades de todas las ofertas de la empresa
        programadores = buscar_programadores_compatibles_empresa(empresa_id, conn, experiencia=request.args.get("experiencia"), ciudad=request.args.get("ciudad"))
    else: # Busca compatibilidades de una oferta concreta
        programadores = buscar_programadores_compatibles(oferta_id, conn, experiencia=request.args.get("experiencia"), ciudad=request.args.get("ciudad"))
    
    conn.close()
    return jsonify([vars(p) for p in programadores])

@app.route("/empresas/ofertas", methods=["GET"])
@jwt_required()  # token obligatorio
def get_ofertas_empresa():
    identity = int(get_jwt_identity())
    claims = get_jwt()
    rol = claims.get("rol")
    if rol != "empresa":
        return jsonify({"error": "Solo las empresas pueden ver sus ofertas"}), 403
    
    conn = get_conn()
    empresa_id = conn.cursor().execute("SELECT id FROM empresas WHERE usuario_id = ?", (identity,)).fetchone()
    if not empresa_id:
        conn.close()
        return jsonify({"error": "Empresa no encontrada para el usuario autenticado"}), 404
    empresa_id = empresa_id[0]  # extrae el id del resultado

    todas = cargar_ofertas(conn)
    ofertas = [o for o in todas if o.empresa_id == empresa_id]
    conn.close()
    return jsonify([vars(o) for o in ofertas])

@app.route("/registro/programador", methods=["POST"])
def registro_programador():
    datos = request.get_json()
    conn = get_conn()
    
    usuario_id = registrar_usuario(datos["email"], datos["contraseña"], "programador", conn)
    if not usuario_id:
        conn.close()
        return jsonify({"error": "El email ya está registrado"}), 409
    
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO programadores (usuario_id, nombre, ciudad, pais, experiencia) VALUES (?, ?, ?, ?, ?)",
        (usuario_id, datos["nombre"], datos["ciudad"], datos["pais"], datos["experiencia"])
    )
    programador_id = cursor.lastrowid
    
    for tec in datos["tecnologias"]:
        cursor.execute(
            "INSERT INTO tecnologias_programador (programador_id, tecnologia) VALUES (?, ?)",
            (programador_id, tec)
        )
    
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Programador registrado correctamente"}), 201

@app.route("/registro/empresa", methods=["POST"])
def registro_empresa():
    datos = request.get_json()
    conn = get_conn()
    
    usuario_id = registrar_usuario(datos["email"], datos["contraseña"], "empresa", conn)
    if not usuario_id:
        conn.close()
        return jsonify({"error": "El email ya está registrado"}), 409
    
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO empresas (usuario_id, nombre, ciudad, pais, pagina_web) VALUES (?, ?, ?, ?, ?)",
        (usuario_id, datos["nombre"], datos["ciudad"], datos["pais"], datos["pagina_web"])
    )
    
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Empresa registrada correctamente"}), 201

@app.route("/login", methods=["POST"])
def login():
    datos = request.get_json()
    conn = get_conn()
    resultado = login_usuario(datos["email"], datos["contraseña"], conn)
    conn.close()
    
    if not resultado:
        return jsonify({"error": "Email o contraseña incorrectos"}), 401
    
    return jsonify(resultado), 200

@app.route("/perfil", methods=["GET"])
@jwt_required()  # token obligatorio
def get_perfil():
    identity = int(get_jwt_identity())
    claims = get_jwt()
    rol = claims.get("rol")
    conn = get_conn()
    
    if rol == "programador":
        programador_id = conn.cursor().execute("SELECT id FROM programadores WHERE usuario_id = ?", (identity,)).fetchone()
        if not programador_id:
            conn.close()
            return jsonify({"error": "Programador no encontrado para el usuario autenticado"}), 404
        programador_id = programador_id[0]
        perfil = conn.cursor().execute("""
            SELECT p.nombre, p.ciudad, p.pais, p.experiencia, GROUP_CONCAT(tp.tecnologia), u.email
            FROM programadores p 
            JOIN tecnologias_programador tp ON p.id = tp.programador_id
            JOIN usuarios u ON u.id = p.usuario_id
            WHERE p.id = ? 
            GROUP BY p.id
        """, (programador_id,)).fetchone()

        resultado = {
            "nombre": perfil[0],
            "ciudad": perfil[1],
            "pais": perfil[2],
            "experiencia": perfil[3],
            "tecnologias": perfil[4].split(",") if perfil[4] else [],
            "email": perfil[5] 
        }
    else:  # empresa
        empresa_id = conn.cursor().execute("SELECT id FROM empresas WHERE usuario_id = ?", (identity,)).fetchone()
        if not empresa_id:
            conn.close()
            return jsonify({"error": "Empresa no encontrada para el usuario autenticado"}), 404
        empresa_id = empresa_id[0]
        perfil = conn.cursor().execute("""
            SELECT e.nombre, e.ciudad, e.pais, e.pagina_web, u.email
            FROM empresas e
            JOIN usuarios u ON u.id = e.usuario_id 
            WHERE e.id = ?            
            """, (empresa_id,)).fetchone()
        
        resultado = {
            "nombre": perfil[0],
            "ciudad": perfil[1],
            "pais": perfil[2],
            "pagina_web": perfil[3],
            "email": perfil[4]
        }
    
    conn.close()
    return jsonify(resultado), 200

@app.route("/perfil", methods=["PUT"])
@jwt_required()  # token obligatorio
def actualizar_perfil():
    identity = int(get_jwt_identity())
    claims = get_jwt()
    rol = claims.get("rol")
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "No se recibieron datos"}), 400
    conn = get_conn()
        
    if rol == "programador":
        programador_id = conn.cursor().execute("SELECT id FROM programadores WHERE usuario_id = ?", (identity,)).fetchone()
        if not programador_id:
            conn.close()
            return jsonify({"error": "Programador no encontrado para el usuario autenticado"}), 404
        programador_id = programador_id[0]
        conn.cursor().execute(
            "UPDATE programadores SET nombre = ?, ciudad = ?, pais = ?, experiencia = ? WHERE id = ?",
            (datos["nombre"], datos["ciudad"], datos["pais"], datos["experiencia"], programador_id)
        )
    else:  # empresa
        empresa_id = conn.cursor().execute("SELECT id FROM empresas WHERE usuario_id = ?", (identity,)).fetchone()
        if not empresa_id:
            conn.close()
            return jsonify({"error": "Empresa no encontrada para el usuario autenticado"}), 404
        empresa_id = empresa_id[0]
        conn.cursor().execute(
            "UPDATE empresas SET nombre = ?, ciudad = ?, pais = ?, pagina_web = ? WHERE id = ?",
            (datos["nombre"], datos["ciudad"], datos["pais"], datos["pagina_web"], empresa_id)
        )
    
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Perfil actualizado correctamente"}), 200

@app.route("/perfil/tecnologias", methods=["POST"])
@jwt_required()  # token obligatorio
def agregar_tecnologia_perfil():
    identity = int(get_jwt_identity())
    claims = get_jwt()
    rol = claims.get("rol")
    datos = request.get_json()
    if not datos or "tecnologias" not in datos:
        return jsonify({"error": "No se recibieron datos"}), 400
    conn = get_conn()
    
    if rol != "programador":
        conn.close()
        return jsonify({"error": "Solo los programadores pueden agregar tecnologías a su perfil"}), 403
    
    programador_id = conn.cursor().execute("SELECT id FROM programadores WHERE usuario_id = ?", (identity,)).fetchone()
    if not programador_id:
        conn.close()
        return jsonify({"error": "Programador no encontrado para el usuario autenticado"}), 404
    programador_id = programador_id[0]
    
    for tec in datos["tecnologias"]:
        conn.cursor().execute(
            "INSERT INTO tecnologias_programador (programador_id, tecnologia) VALUES (?, ?)",
            (programador_id, tec)
        )
    
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Tecnologías agregadas correctamente"}), 200

@app.route("/perfil/tecnologias", methods=["DELETE"])
@jwt_required()  # token obligatorio
def eliminar_tecnologia_perfil():
    identity = int(get_jwt_identity())
    claims = get_jwt()
    rol = claims.get("rol")
    datos = request.get_json()
    if not datos or "tecnologias" not in datos:
        return jsonify({"error": "No se recibieron datos"}), 400 
    conn = get_conn()
    
    if rol != "programador":
        conn.close()
        return jsonify({"error": "Solo los programadores pueden eliminar tecnologías de su perfil"}), 403
    
    programador_id = conn.cursor().execute("SELECT id FROM programadores WHERE usuario_id = ?", (identity,)).fetchone()
    if not programador_id:
        conn.close()
        return jsonify({"error": "Programador no encontrado para el usuario autenticado"}), 404
    programador_id = programador_id[0]
    
    for tec in datos["tecnologias"]:
        conn.cursor().execute(
            "DELETE FROM tecnologias_programador WHERE programador_id = ? AND tecnologia = ?",
            (programador_id, tec)
        )
    
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Tecnologías eliminadas correctamente"}), 200

@app.route("/reset", methods=["POST"])
def reset_db():
    conn = get_conn()
    resetear_db(conn)
    inicializar_db(conn)
    conn.close()
    return "Base de datos reseteada"

conn = get_conn()
inicializar_db(conn)
conn.close()

if __name__ == "__main__":
    app.run(debug=True)
