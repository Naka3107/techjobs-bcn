from flask  import Flask, jsonify, render_template, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_jwt
import sqlite3
from database import inicializar_db, cargar_ofertas, cargar_programadores, guardar_oferta, guardar_programador, buscar_ofertas_compatibles, buscar_programadores_compatibles, resetear_db
from bolsa import Oferta, Programador, Empresa
from auth import registrar_usuario, login_usuario

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
        guardar_oferta(Oferta(id=None, empresa_id=empresa_id, **oferta),conn)
    conn.commit()
    conn.close()
    return "Ofertas añadidas"

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
        programadores = []
        ofertas_empresa = conn.cursor().execute("SELECT id FROM ofertas WHERE empresa_id = ?", (empresa_id,)).fetchall()
        for oferta in ofertas_empresa:
            programadores += buscar_programadores_compatibles(oferta[0], conn, años_experiencia_minimo=request.args.get("años_experiencia_minimo"), ciudad=request.args.get("ciudad"))
    else: # Busca compatibilidades de una oferta concreta
        programadores = buscar_programadores_compatibles(oferta_id, conn, años_experiencia_minimo=request.args.get("años_experiencia_minimo"), ciudad=request.args.get("ciudad"))
    
    conn.close()
    return jsonify([vars(p) for p in programadores])

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
        "INSERT INTO programadores (usuario_id, nombre, ciudad, pais, años_experiencia) VALUES (?, ?, ?, ?, ?)",
        (usuario_id, datos["nombre"], datos["ciudad"], datos["pais"], datos["años_experiencia"])
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