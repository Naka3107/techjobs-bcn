class Usuario:
    def __init__(self, id, email, rol):
        self.id = id
        self.email = email
        self.rol = rol

class Empresa:
    def __init__(self, id, usuario_id, nombre, ciudad, pais, pagina_web):
        self.id = id
        self.usuario_id = usuario_id
        self.nombre = nombre
        self.ciudad = ciudad
        self.pais = pais
        self.pagina_web = pagina_web

class Programador:
    def __init__(self, id, usuario_id, nombre, ciudad, pais, años_experiencia, tecnologias):
        self.id = id
        self.usuario_id = usuario_id
        self.nombre = nombre
        self.ciudad = ciudad
        self.pais = pais
        self.años_experiencia = años_experiencia
        self.tecnologias = tecnologias

class Oferta:
    def __init__(self, id, empresa_id, puesto, salario, pais, capital, tecnologias, nombre_empresa=None):
        self.id = id
        self.empresa_id = empresa_id
        self.puesto = puesto
        self.salario = salario
        self.pais = pais
        self.capital = capital
        self.tecnologias = tecnologias
        self.nombre_empresa = nombre_empresa


    