# tests/test_services.py
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bolsa import Programador, Oferta
from services import calcular_compatibilidad

def test_compatibilidad_perfecta():
    # Crea un programador y una oferta donde todo coincide
    mock_programador = Programador (
        id=1 ,
        usuario_id= 2,
        nombre= "Programador Test",
        ciudad= "Barcelona",
        pais= "España",
        experiencia=2,
        tecnologias= ["Python", "SQL", "Git"]
    )

    mock_oferta = Oferta (
        id = 2,
        empresa_id= 1,
        nombre_empresa= "Raona",
        puesto = "Python Developer",
        salario = 26000,
        experiencia_minima = 1,
        pais = "España",
        ciudad = "Barcelona",
        tecnologias = ["Python", "SQL", "Git"]
    )

    # mismas tecnologías, experiencia suficiente, misma ciudad
    # El resultado debería ser 100%
    resultado = calcular_compatibilidad(mock_programador, mock_oferta)

    # Verifica el porcentaje
    assert resultado["porcentaje"] == 100

    # Verifica el desglose
    assert resultado["desglose"]["experiencia_cumple"] == True
    assert resultado["desglose"]["ciudad_cumple"] == True
    assert resultado["desglose"]["tecnologias_faltantes"] == []  
    assert "Python" in resultado["desglose"]["tecnologias_coincidentes"]

    pass

def test_sin_tecnologias_coincidentes ():
    # Crea un programador y una oferta donde todo coincide
    mock_programador = Programador (
        id=1 ,
        usuario_id= 2,
        nombre= "Programador Test",
        ciudad= "Barcelona",
        pais= "España",
        experiencia=2,
        tecnologias= ["Python", "SQL", "Git"]
    )

    mock_oferta = Oferta (
        id = 2,
        empresa_id= 1,
        nombre_empresa= "Raona",
        puesto = "Python Developer",
        salario = 26000,
        experiencia_minima = 1,
        pais = "España",
        ciudad = "Barcelona",
        tecnologias = ["Docker", "Angular", "Java"]
    )

    # mismas tecnologías, experiencia suficiente, misma ciudad
    # El resultado debería ser 40%
    resultado = calcular_compatibilidad(mock_programador, mock_oferta)

    # Verifica el porcentaje
    assert resultado["porcentaje"] == 40

    # Verifica el desglose
    assert resultado["desglose"]["experiencia_cumple"] == True
    assert resultado["desglose"]["ciudad_cumple"] == True
    assert "Docker" in resultado["desglose"]["tecnologias_faltantes"]
    assert resultado["desglose"]["tecnologias_coincidentes"] == []  

    pass

def test_experiencia_insuficiente ():
    # Crea un programador y una oferta donde todo coincide
    mock_programador = Programador (
        id=1 ,
        usuario_id= 2,
        nombre= "Programador Test",
        ciudad= "Barcelona",
        pais= "España",
        experiencia=0,
        tecnologias= ["Python", "SQL", "Git"]
    )

    mock_oferta = Oferta (
        id = 2,
        empresa_id= 1,
        nombre_empresa= "Raona",
        puesto = "Python Developer",
        salario = 26000,
        experiencia_minima = 1,
        pais = "España",
        ciudad = "Barcelona",
        tecnologias = ["Python", "SQL", "Git"]
    )

    # mismas tecnologías, experiencia suficiente, misma ciudad
    # El resultado debería ser 75
    resultado = calcular_compatibilidad(mock_programador, mock_oferta)

    # Verifica el porcentaje
    assert resultado["porcentaje"] == 75

    # Verifica el desglose
    assert resultado["desglose"]["experiencia_cumple"] == False
    assert resultado["desglose"]["ciudad_cumple"] == True
    assert resultado["desglose"]["tecnologias_faltantes"] == []  
    assert "Python" in resultado["desglose"]["tecnologias_coincidentes"]


    pass

def test_mismo_pais_diferente_ciudad():
    mock_programador = Programador(
        id=1, usuario_id=2, nombre="Test",
        ciudad="Madrid",
        pais="España",
        experiencia=2,
        tecnologias=["Python", "SQL", "Git"]
    )

    mock_oferta = Oferta(
        id=2, empresa_id=1, nombre_empresa="Raona",
        puesto="Python Developer", salario=26000,
        experiencia_minima=1,
        pais="España",
        ciudad="Barcelona",
        tecnologias=["Python", "SQL", "Git"]
    )

    resultado = calcular_compatibilidad(mock_programador, mock_oferta)


    assert resultado["desglose"]["ciudad_cumple"] == False
    assert resultado["desglose"]["pais_cumple"] == True
    assert resultado["porcentaje"] == 92  

    pass

def test_diferente_pais():
    mock_programador = Programador(
        id=1, usuario_id=2, nombre="Test",
        ciudad="Madrid",
        pais="España",
        experiencia=2,
        tecnologias=["Python", "SQL", "Git"]
    )

    mock_oferta = Oferta(
        id=2, empresa_id=1, nombre_empresa="Raona",
        puesto="Python Developer", salario=26000,
        experiencia_minima=1,
        pais="Francia",
        ciudad="Paris",
        tecnologias=["Python", "SQL", "Git"]
    )

    resultado = calcular_compatibilidad(mock_programador, mock_oferta)


    assert resultado["desglose"]["ciudad_cumple"] == False
    assert resultado["desglose"]["pais_cumple"] == False
    assert resultado["porcentaje"] == 85

    pass  