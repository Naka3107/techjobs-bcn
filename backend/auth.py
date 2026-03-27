import bcrypt
from flask_jwt_extended import create_access_token
import sqlite3

def hashear_contraseña(contraseña: str) -> str:
    return bcrypt.hashpw(contraseña.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verificar_contraseña(contraseña: str, hash: str) -> bool:
    return bcrypt.checkpw(contraseña.encode('utf-8'), hash.encode('utf-8'))

def registrar_usuario(email: str, contraseña: str, rol: str, conn) -> int:
    cursor = conn.cursor()
    
    # Verificar si el email ya existe
    cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
    if cursor.fetchone():
        return None  # email ya registrado
    
    hash = hashear_contraseña(contraseña)
    cursor.execute(
        "INSERT INTO usuarios (email, contraseña_hash, rol) VALUES (?, ?, ?)",
        (email, hash, rol)
    )
    return cursor.lastrowid

def login_usuario(email: str, contraseña: str, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, contraseña_hash, rol FROM usuarios WHERE email = ?", (email,))
    usuario = cursor.fetchone()
    
    if not usuario:
        return None  # usuario no existe
    
    if not verificar_contraseña(contraseña, usuario[1]):
        return None  # contraseña incorrecta
    
    # Genera el token JWT con el id y rol del usuario
    token = create_access_token(
        identity=str(usuario[0]),
        additional_claims={"rol": usuario[2]}
    )
    return {"token": token, "rol": usuario[2], "usuario_id": usuario[0]}