def calcular_compatibilidad(programador, oferta):
    # TECNOLOGIAS (60%)
    tecs_oferta = set(oferta.tecnologias)
    tecs_programador = set(programador.tecnologias)
    coincidencias = tecs_oferta & tecs_programador

    if len (tecs_oferta)>0:
        puntos_tecs = (len(coincidencias) / len(tecs_oferta)) * 60
    else:
        puntos_tecs = 60 # si la oferta no requiere tecnologías, puntuación completa

    # EXPERIENCIA (25%)
    minim_exp = oferta.experiencia_minima or 0
    if minim_exp == 0 or programador.experiencia >= minim_exp:
        puntos_exp = 25
    else:
        puntos_exp = (programador.experiencia/minim_exp) * 25

    # UBICACION (15%)
    if programador.ciudad.lower() == oferta.ciudad.lower():
        puntos_ciudad = 15
    elif programador.pais.lower() == oferta.pais.lower():
        puntos_ciudad = 7
    else:
        puntos_ciudad = 0

    total = round(puntos_tecs + puntos_exp + puntos_ciudad)

    return {
        "porcentaje": total,
        "desglose": {
            "tecnologias": round(puntos_tecs),
            "tecnologias_coincidentes": list(coincidencias),
            "tecnologias_faltantes": list(tecs_oferta - tecs_programador),
            "experiencia": round(puntos_exp),
            "ciudad": round(puntos_ciudad)
        }
    } 