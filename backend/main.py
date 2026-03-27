import sqlite3
from bolsa import Oferta, Programador, BolsaDeEmpleo
from validators import pedir_texto, pedir_entero, pedir_lista
from database import guardar_programador, cargar_programadores, guardar_oferta, cargar_ofertas, inicializar_db

def menu():
    bolsa = BolsaDeEmpleo()

    conn = sqlite3.connect("buscador.db")
    inicializar_db(conn)
    bolsa.ofertas = cargar_ofertas(conn)
    bolsa.programadores = cargar_programadores(conn)
    
    while True:
        print("\n=== Buscador de Empleo CLI ===")
        print("1. Añadir oferta")
        print("2. Añadir programador")
        print("3. Buscar ofertas compatibles")
        print("4. Ver todas las ofertas")
        print("5. Salir")
        
        opcion = input("\nElige una opción: ")
        
        if opcion == "1":
            # pide datos al usuario e llama a bolsa.agregar_oferta
            empresa = pedir_texto("\nDame el nombre de la empresa: ")
            puesto = pedir_texto("\nDame el nombre del puesto: ")
            salario = pedir_entero("\nDame el salario: ")
            tecnologias = pedir_lista("\nDame las tecnologias que piden en la oferta: ")
            pais = pedir_texto("\nDame el nombre del país donde está la oferta: ")
            oferta = Oferta(empresa, puesto, salario, tecnologias)
            bolsa.agregar_oferta(oferta)

            guardar_oferta(oferta, conn)
            conn.commit()

        elif opcion == "2":
            # añade programadores a la bolsa
            nombre = pedir_texto("\nDame el nombre del programador: ")
            ciudad = pedir_texto("\nDame la ciudad donde vive el programador: ")
            tecnologias = pedir_lista("\nDame las tecnologias que maneja el programador: ")
            años_experiencia = pedir_entero("\nDame cuántos años de experiencia tiene el programador: ")
            prog = Programador(nombre, ciudad, tecnologias, años_experiencia)
            bolsa.agregar_programador(prog)
            guardar_programador(prog, conn)
            conn.commit()
            
        elif opcion == "3":
            nombre = pedir_texto("\nDame el nombre del programador: ")
            programador_obj = next((p for p in bolsa.programadores if p.nombre == nombre), None)
            if not programador_obj  :
                print ("Programador sin registrar, presione 6 para registrarlo")
            else:
                salario_minimo = pedir_entero("\nDame cuál es el salario mínimo que quiere el programador: ")
                resultados = bolsa.buscar_ofertas(programador_obj, salario_minimo)
                for resultado in resultados:
                    print(f"✓ {resultado['datos_oferta'].empresa} | {resultado['datos_oferta'].salario}€ | coincide en: {resultado['coincidencias']}")  
            # pide tecnologias y salario minimo, crea Programador y llama a buscar_ofertas
                
        elif opcion == "4":
            # recorre bolsa.ofertas y llama a oferta.mostrar()
            for oferta in bolsa.ofertas:
                oferta.mostrar()

        elif opcion == "5":
            print("¡Hasta luego!")
            conn.close()
            break
        else:
            print("Opción no válida")

menu()