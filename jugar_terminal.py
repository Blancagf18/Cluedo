import os
import time
# CAMBIO AQUÍ: Importamos MOTIVOS_POR_SOSPECHOSO en vez de MOTIVOS
from motor import construir_mazo, SOSPECHOSOS, MOTIVOS_POR_SOSPECHOSO, DATA_ARMAS

def limpiar():
    os.system('cls' if os.name == 'nt' else 'clear')

def imprimir_titulo():
    print("╔════════════════════════════════════════════╗")
    print("║      🕵️  DETECTIVE EN LA TERMINAL  🕵️      ║")
    print("╚════════════════════════════════════════════╝")

# Generamos una lista única de motivos para mostrar al jugador
# (Junta todos los motivos de todos los sospechosos y quita duplicados)
LISTA_MOTIVOS_VISUAL = sorted(list(set(m for lista in MOTIVOS_POR_SOSPECHOSO.values() for m in lista)))

def mostrar_mazo_ordenado(mazo):
    print("\n📦 TUS PISTAS (MAZO DE INVESTIGACIÓN):")
    print("-" * 50)
    
    categorias = {
        "Forense": [],
        "Cámaras": [],
        "Lugares": [], 
        "Social": []   
    }

    for c in mazo:
        t = c["tipo"]
        texto = f"[ID {c['id']:03}] {c['texto']}"
        
        if t in ["descarte_arma", "informe_categoria", "sintoma_negativo", "sintoma_positivo", "evidencia_motivo"]:
            categorias["Forense"].append(texto)
        elif "camara" in t:
            categorias["Cámaras"].append(texto)
        elif t in ["lugar_limpio", "bloqueo_paso"]:
            categorias["Lugares"].append(texto)
        else:
            categorias["Social"].append(texto)

    for cat, cartas in categorias.items():
        if cartas:
            print(f"\n--- {cat.upper()} ---")
            for carta in cartas:
                print(carta)
    print("\n" + "="*50)

def resolver(verdad):
    print("\n🤔 MOMENTO DE LA DEDUCCIÓN")
    print("Escribe tu teoría con exactitud (o partes del nombre).")
    
    # 1. ACUSAR ASESINO
    print(f"\nSospechosos: {', '.join(SOSPECHOSOS)}")
    asesino_input = input("👉 ¿Quién es el ASESINO?: ").strip().lower()
    
    # 2. ACUSAR ARMA
    print(f"\nArmas posibles: {', '.join(list(DATA_ARMAS.keys())[:5])}...") 
    arma_input = input("👉 ¿Cuál es el ARMA?: ").strip().lower()
    
    # 3. ACUSAR MÓVIL
    print(f"\nMóviles posibles: {', '.join(LISTA_MOTIVOS_VISUAL)}")
    movil_input = input("👉 ¿Cuál es el MÓVIL?: ").strip().lower()

    # COMPROBACIÓN
    check_asesino = asesino_input == verdad['culpable'].lower()
    check_arma = arma_input in verdad['arma'].lower() 
    check_motivo = movil_input == verdad['motivo'].lower()

    limpiar()
    imprimir_titulo()
    
    if check_asesino and check_arma and check_motivo:
        print("\n🎉 ¡ENHORABUENA DETECTIVE! 🎉")
        print("¡Has resuelto el caso perfectamente!")
    else:
        print("\n💀 ¡FALLASTE! El asesino escapa...")
        print("Tus aciertos:")
        print(f"   - Asesino: {'✅' if check_asesino else '❌'}")
        print(f"   - Arma:    {'✅' if check_arma else '❌'}")
        print(f"   - Móvil:   {'✅' if check_motivo else '❌'}")

    print("\n🤫 LA VERDAD ERA:")
    print(f"   • Culpable: {verdad['culpable']}")
    print(f"   • Arma:     {verdad['arma']} (Origen: {verdad['origen_arma']})")
    print(f"   • Móvil:    {verdad['motivo']}")
    if verdad['complice']:
        print(f"   • Cómplice: {verdad['complice']}")

def main():
    limpiar()
    imprimir_titulo()
    print("1. Fácil")
    print("2. Intermedio")
    print("3. Difícil")
    print("4. Crimen Maestro")
    
    dif = input("\nElige dificultad (1-4): ").strip()
    if dif not in ["1", "2", "3", "4"]: dif = "2"

    print("\n⚙️  Generando caso... (Ignora los logs del motor)")
    time.sleep(1)
    
    # LLAMADA AL MOTOR
    verdad, mazo, nombre_dif = construir_mazo(dif)
    
    if not verdad:
        print("Error generando la partida.")
        return

    limpiar()
    imprimir_titulo()
    print(f"Dificultad: {nombre_dif.upper()} | {len(mazo)} Cartas")
    
    while True:
        print("\nOpciones:")
        print(" [1] Ver Cartas (Mazo)")
        print(" [2] RESOLVER EL CRIMEN")
        print(" [3] Rendirse (Ver solución)")
        print(" [0] Salir")
        
        accion = input("\n> ").strip()
        
        if accion == "1":
            mostrar_mazo_ordenado(mazo)
            input("\n[Presiona ENTER para volver al menú]")
            limpiar()
            imprimir_titulo()
        
        elif accion == "2":
            resolver(verdad)
            break
            
        elif accion == "3":
            print(f"\nSOLUCIÓN: {verdad['culpable']} mató con {verdad['arma']} por {verdad['motivo']}.")
            break
            
        elif accion == "0":
            print("Adiós.")
            break

if __name__ == "__main__":
    main()