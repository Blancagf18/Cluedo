import json
import random
import os
from collections import deque

# =============================================================================
# 1. BASE DE DATOS ESTRICTA
# =============================================================================

CONEXIONES = [
    ("Entrada", "Pista de Baile"), ("Pista de Baile", "Ropero"),
    ("Pista de Baile", "Baños"), ("Pista de Baile", "Barra"),
    ("Pista de Baile", "Terraza"), ("Pista de Baile", "Reservados"),
    ("Pista de Baile", "Sala de Seguridad"), ("Pista de Baile", "Cabina del DJ"),
    ("Baños", "Almacén"), ("Almacén", "Barra"), ("Almacén", "Terraza"),
    ("Terraza", "Barra"), ("Terraza", "Sala de Seguridad"),
    ("Sala de Seguridad", "Reservados"), ("Reservados", "Ropero")
]

# MOTIVOS ESPECÍFICOS (Recuperados de tu diseño original)
MOTIVOS_POR_SOSPECHOSO = {
    "Sergio":   ["Una mujer", "Venganza", "Un bizum"],
    "Edu":      ["Un cigarro", "Borrachera", "Un bizum"],
    "Javi":     ["Venganza", "Apuestas", "Un cigarro"],
    "Fernando": ["Un bizum", "Apuestas", "Venganza"],
    "Blanca":   ["Borrachera", "Una mujer", "Un cigarro"],
    "Alberto":  ["Apuestas", "Borrachera", "Una mujer"]
}
SOSPECHOSOS = list(MOTIVOS_POR_SOSPECHOSO.keys())

# ARMAS (Con palabras clave para el matcheo flexible)
DATA_ARMAS = {
    # CONTUNDENTES
    "Botella de Recompensa": {"cat": "Contundentes", "sintomas": ["Contusión Letal", "Abundante Sangre"], "lugar": "Barra"},
    "Balón de VolleyBall":   {"cat": "Contundentes", "sintomas": ["Contusión Letal", "Shock"], "lugar": "Terraza"}, # Corregido a Shock
    "Polla de Plástico":     {"cat": "Contundentes", "sintomas": ["Contusión Letal", "Abundante Sangre"], "lugar": "Sala de Seguridad"},
    "Hielo del cubata":      {"cat": "Contundentes", "sintomas": ["Contusión Letal", "Quemaduras"], "lugar": "Barra"},
    # VENENOS
    "Durum":                 {"cat": "Venenos", "sintomas": ["Envenenamiento", "Olores Fuertes"], "lugar": "Ropero"},
    "Un Pelotazo":           {"cat": "Venenos", "sintomas": ["Envenenamiento", "Shock"], "lugar": "Ropero"}, # Corregido a Shock
    "Zurraspa":              {"cat": "Venenos", "sintomas": ["Envenenamiento", "Olores Fuertes"], "lugar": "Baños"},
    "Condón Usado":          {"cat": "Venenos", "sintomas": ["Envenenamiento", "Asfixia"], "lugar": "Baños"},
    # ASFIXIA
    "Pedo":                  {"cat": "Asfixiantes", "sintomas": ["Asfixia", "Olores Fuertes"], "lugar": "Entrada"},
    "Lefada de Gustavo":     {"cat": "Asfixiantes", "sintomas": ["Asfixia", "Envenenamiento"], "lugar": "Baños"},
    "Sobaco Sudado":         {"cat": "Asfixiantes", "sintomas": ["Asfixia", "Olores Fuertes"], "lugar": "Terraza"},
    "Un vello púbico":       {"cat": "Asfixiantes", "sintomas": ["Asfixia", "Abundante Sangre"], "lugar": "Baños"},
    # COLAPSO (Antes llamado Shock en el código)
    "Foto de la Bellido":    {"cat": "Colapso", "sintomas": ["Shock", "Abundante Sangre"], "lugar": "Barra"},
    "Beso de la Nana":       {"cat": "Colapso", "sintomas": ["Shock", "Contusión Letal"], "lugar": "Reservados"},
    "Uña del Pie":           {"cat": "Colapso", "sintomas": ["Shock", "Abundante Sangre"], "lugar": "Reservados"},
    "Clausulazo":            {"cat": "Colapso", "sintomas": ["Shock", "Restos de Pólvora"], "lugar": "Reservados"},
    # FUEGO
    "Cigarro":               {"cat": "Armas de Fuego", "sintomas": ["Quemaduras", "Olores Fuertes"], "lugar": "Sala de Seguridad"},
    "Mechero Trucado":       {"cat": "Armas de Fuego", "sintomas": ["Quemaduras", "Restos de Pólvora"], "lugar": "Almacén"},
    "Eructo en la Oreja":    {"cat": "Armas de Fuego", "sintomas": ["Quemaduras", "Restos de Pólvora"], "lugar": "Terraza"},
    "Montapuercos":          {"cat": "Armas de Fuego", "sintomas": ["Quemaduras", "Restos de Pólvora"], "lugar": "Terraza"}
}

UBICACION_ARMAS = {}
for nombre, datos in DATA_ARMAS.items():
    UBICACION_ARMAS.setdefault(datos["lugar"], []).append(nombre)

# =============================================================================
# 2. UTILIDADES DE NORMALIZACIÓN
# =============================================================================

def slugify(text):
    """Limpia tildes, espacios y caracteres raros para comparaciones."""
    text = str(text).lower()
    replacements = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ü": "u", "ñ": "n",
        " ": "_", "'": "", ".": "", ":": "", ",": ""
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

def hay_conflicto_categoria(cat_real, tag_carta):
    """
    Compara de forma inteligente (fuzzy matching).
    Devuelve TRUE si hay conflicto (es decir, si son la misma categoría).
    """
    real = slugify(cat_real)          # ej: armas_de_fuego
    carta = slugify(tag_carta.replace("no_categoria_", "")) # ej: de_fuego
    
    # 1. Coincidencia exacta
    if real == carta: return True
    
    # 2. Coincidencia de palabras clave
    keywords = ["fuego", "veneno", "asfixi", "shock", "contundente", "colapso"]
    for k in keywords:
        if k in real and k in carta:
            return True
            
    return False

def cargar_cartas():
    if not os.path.exists("cartas_final.json"):
        print("❌ Error: Falta 'cartas_final.json'")
        return []
    with open("cartas_final.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        return data["cartas"] if isinstance(data, dict) else data

# =============================================================================
# 3. PATHFINDING
# =============================================================================

def rutas_con_minimo_pasos(inicio, fin, min_habitaciones_intermedias):
    grafo = {}
    for a, b in CONEXIONES:
        grafo.setdefault(a, []).append(b)
        grafo.setdefault(b, []).append(a)

    cola = deque([(inicio, [inicio])])
    rutas_validas = []

    while cola:
        nodo_actual, camino = cola.popleft()
        if nodo_actual == fin:
            if len(camino) >= (2 + min_habitaciones_intermedias):
                rutas_validas.append(camino)
            continue
        
        if len(camino) > 8: continue
        for vecino in grafo.get(nodo_actual, []):
            if vecino not in camino:
                cola.append((vecino, camino + [vecino]))
    
    rutas_validas.sort(key=len)
    return rutas_validas[0] if rutas_validas else None

def check_paso_bloqueado(ruta, bloqueo_a, bloqueo_b):
    b_a = slugify(bloqueo_a)
    b_b = slugify(bloqueo_b)
    for i in range(len(ruta) - 1):
        origen = slugify(ruta[i])
        destino = slugify(ruta[i+1])
        if (origen == b_a and destino == b_b) or (origen == b_b and destino == b_a):
            return True
    return False

# =============================================================================
# 4. GENERADOR DE VERDAD (CORREGIDO MÓVILES)
# =============================================================================

def generar_verdad(dificultad):
    culpable = random.choice(SOSPECHOSOS)
    
    # --- FIX 1: MÓVIL ESPECÍFICO ---
    # El móvil DEBE ser uno de los que tiene el personaje, no uno random global.
    motivo_real = random.choice(MOTIVOS_POR_SOSPECHOSO[culpable])
    
    arma_real_nombre = random.choice(list(DATA_ARMAS.keys()))
    arma_datos = DATA_ARMAS[arma_real_nombre]
    origen_arma = arma_datos["lugar"]
    lugar_crimen = "Cabina del DJ"

    complice = None
    motivo_complice = None # NUEVO
    cabeza_turco = None
    motivo_turco = None # NUEVO
    if dificultad in ["3", "4"]:
        complice = random.choice([s for s in SOSPECHOSOS if s != culpable])
        motivo_complice = random.choice(MOTIVOS_POR_SOSPECHOSO[complice]) # NUEVO
        
        cabeza_turco = random.choice([s for s in SOSPECHOSOS if s != culpable and s != complice])
        motivo_turco = random.choice(MOTIVOS_POR_SOSPECHOSO[cabeza_turco]) # NUEVO

    # Rivalidades
    rivalidades = {}
    for s in SOSPECHOSOS:
        otros = [o for o in SOSPECHOSOS if o != s]
        rivalidades[s] = random.sample(otros, k=random.choice([1, 2]))

    if cabeza_turco:
        rivalidades[culpable] = [cabeza_turco]
        if complice: rivalidades[complice] = [cabeza_turco]

    posiciones = {culpable: lugar_crimen}
    lugares_validos = list(UBICACION_ARMAS.keys()) + ["Pista de Baile"]
    if "Entrada" in lugares_validos: lugares_validos.remove("Entrada")

    for s in SOSPECHOSOS:
        if s != culpable:
            posiciones[s] = random.choice([l for l in lugares_validos if l != lugar_crimen])
            
    # EL PARCHE: Forzar al cómplice a ir a la tapadera para que las cámaras le graben allí
    if complice:
        posiciones[complice] = origen_arma

    rutas = {}
    ruta_a = rutas_con_minimo_pasos("Entrada", origen_arma, 1) or ["Entrada", origen_arma]
    ruta_b = rutas_con_minimo_pasos(origen_arma, lugar_crimen, 0)
    rutas[culpable] = ruta_a[:-1] + ruta_b
    
    for s in SOSPECHOSOS:
        if s != culpable:
            r = rutas_con_minimo_pasos("Entrada", posiciones[s], 0)
            if not r: r = rutas_con_minimo_pasos("Entrada", posiciones[s], 0)
            rutas[s] = r

    return {
        "culpable": culpable,
        "complice": complice,
        "cabeza_turco": cabeza_turco,
        "rivalidades": rivalidades,
        "motivo": motivo_real,
        "motivo_complice": motivo_complice, # NUEVO
        "motivo_turco": motivo_turco, # NUEVO
        "arma": arma_real_nombre,
        "datos_arma": arma_datos,
        "origen_arma": origen_arma,
        "lugar_crimen": lugar_crimen,
        "posiciones": posiciones,
        "rutas": rutas
    }

# =============================================================================
# 5. VALIDADOR DE CARTAS (CORREGIDO CATEGORÍAS)
# =============================================================================

def es_carta_valida(carta, verdad):
    tags = carta.get("tags", [])
    tipo = carta.get("tipo")
    texto = carta.get("texto", "")

    # --- FIX 2: CATEGORÍAS ---
    if tipo == "informe_categoria":
        cat_real = verdad["datos_arma"]["cat"]
        tag_carta = tags[0]
        
        # Si hay conflicto (coinciden semánticamente), la carta miente al descartarlo.
        # Por tanto, devolvemos FALSE.
        if hay_conflicto_categoria(cat_real, tag_carta):
            return False
        return True

# --- DESCARTE ARMA ---
    if tipo == "descarte_arma":
        texto_slug = slugify(texto)
        tags_norm = " ".join([slugify(t) for t in tags])
        arma_real = slugify(verdad['arma'])
        
        # 1. Chequeo exacto
        if f"no_arma_{arma_real}" in tags_norm: return False
        if arma_real in texto_slug: return False
        
        # 2. Parche salvavidas para erratas del JSON (Durum y Bellido)
        if "durum" in arma_real and ("durum" in texto_slug or "durum" in tags_norm): return False
        if "bellido" in arma_real and ("bellido" in texto_slug or "bellido" in tags_norm): return False
        
        return True

# --- EVIDENCIA DE MÓVIL ---
    if tipo == "evidencia_motivo":
        tag_carta = tags[0]
        
        combo_asesino = f"evidencia_motivo_{slugify(verdad['motivo'])}_{slugify(verdad['culpable'])}"
        
        combo_complice = ""
        if verdad.get('complice'):
            combo_complice = f"evidencia_motivo_{slugify(verdad['motivo_complice'])}_{slugify(verdad['complice'])}"
            
        combo_turco = ""
        if verdad.get('cabeza_turco'):
            combo_turco = f"evidencia_motivo_{slugify(verdad['motivo_turco'])}_{slugify(verdad['cabeza_turco'])}"
            
        # Si la evidencia apunta al asesino, al cómplice o al cabeza de turco, la metemos para liar
        if tag_carta in [combo_asesino, combo_complice, combo_turco]:
            return True
            
        return False


    # --- BLOQUEOS ---
    if tipo == "bloqueo_paso":
        tag_bloqueo = tags[0]
        bloqueo_detectado = False
        for u, v in CONEXIONES:
            # Ajustamos los nombres exactamente a como los escribiste en cartas_final.json
            nombre_u = slugify(u).replace("pista_de_baile", "pista_baile").replace("banos", "baños")
            nombre_v = slugify(v).replace("pista_de_baile", "pista_baile").replace("banos", "baños")
            
            tag_a = f"bloqueo_paso_{nombre_u}_{nombre_v}"
            tag_b = f"bloqueo_paso_{nombre_v}_{nombre_u}"
            
            if tag_bloqueo == tag_a or tag_bloqueo == tag_b:
                for personaje, ruta in verdad["rutas"].items():
                    if check_paso_bloqueado(ruta, u, v): return False 
                bloqueo_detectado = True
                break
        if not bloqueo_detectado: return False
        return True

    # --- CÁMARAS ---
    if "camara" in tipo:
        all_tags = " ".join(tags)
        es_afirmativa = "paso_si" in all_tags
        personas = [s for s in SOSPECHOSOS if slugify(s) in all_tags]
        
        lugar_carta = None
        salas = set([c[0] for c in CONEXIONES] + [c[1] for c in CONEXIONES] + ["Almacén", "Cabina del DJ"])
        for sala in salas:
            if slugify(sala) in all_tags:
                lugar_carta = sala
                break
        if not lugar_carta: return False 

        pasaron = []
        for p in personas:
            ruta = verdad["rutas"].get(p, [])
            pasaron.append(lugar_carta in ruta)
        
        todos_pasaron = all(pasaron)
        ninguno_paso = not any(pasaron)

        if es_afirmativa and not todos_pasaron: return False
        if not es_afirmativa and not ninguno_paso: return False
        return True

    # --- SÍNTOMAS ---
    if tipo == "sintoma_negativo":
        sintomas_reales = [slugify(s) for s in verdad["datos_arma"]["sintomas"]]
        sintoma_carta = tags[0].replace("no_sintoma_", "")
        if slugify(sintoma_carta) in sintomas_reales: return False
        return True

    if tipo == "sintoma_positivo":
        sintomas_reales = [slugify(s) for s in verdad["datos_arma"]["sintomas"]]
        sintoma_carta = tags[0].replace("si_sintoma_", "")
        if slugify(sintoma_carta) not in sintomas_reales: return False
        return True

    # --- LUGAR LIMPIO ---
    if tipo == "lugar_limpio":
        lugar_carta = tags[0].replace("limpio_", "")
        if slugify(lugar_carta) == slugify(verdad["origen_arma"]): return False
        return True

    # --- DESCARTES DE MOTIVO ---
    if tipo == "descarte_motivo":
        if f"no_motivo_{slugify(verdad['motivo'])}" in tags: return False
        if verdad.get("motivo_complice") and f"no_motivo_{slugify(verdad['motivo_complice'])}" in tags: return False

    if tipo == "descarte_motivo_especifico":
        combo_asesino = f"no_motivo_{slugify(verdad['motivo'])}_{slugify(verdad['culpable'])}"
        if combo_asesino in tags: return False
        
        if verdad.get("complice"):
            combo_complice = f"no_motivo_{slugify(verdad['motivo_complice'])}_{slugify(verdad['complice'])}"
            if combo_complice in tags: return False

    if tipo == "descarte_motivo_especifico":
        # Descarte específico: "No fue venganza de Fernando"
        combo = f"no_motivo_{slugify(verdad['motivo'])}_{slugify(verdad['culpable'])}"
        if combo in tags: return False

    # --- ACUSACIONES ---
    if tipo == "acusacion_motivo":
        acusador = next(t for t in tags if t.startswith("acusador_")).replace("acusador_", "").capitalize()
        acusado = next(t for t in tags if t.startswith("acusado_")).replace("acusado_", "").capitalize()
        rivales = verdad["rivalidades"].get(acusador, [])
        if acusado not in rivales: return False
        
        # VALIDACIÓN EXTRA: El acusado debe tener ese motivo en su lista real
        # Si la carta acusa a "Fernando por Borrachera", pero Fernando no tiene ese móvil -> Falso (inconsistente)
        motivo_tag = next(t for t in tags if t.startswith("motivo_")).replace("motivo_", "")
        
        # Recuperamos la lista de motivos posibles del acusado
        motivos_posibles_acusado = [slugify(m) for m in MOTIVOS_POR_SOSPECHOSO.get(acusado, [])]
        
        if motivo_tag not in motivos_posibles_acusado:
            return False # Carta absurda: acusa de algo imposible para ese pj

        return True

    # --- SOCIAL ---
    if tipo == "coartada_union":
        p1 = tags[0].split("_")[1].capitalize()
        p2 = tags[0].split("_")[3].capitalize()
        if verdad["complice"]:
            pareja = {p1, p2}
            if verdad["complice"] in pareja and verdad["culpable"] in pareja:
                return True
        lugar1 = verdad["posiciones"].get(p1)
        lugar2 = verdad["posiciones"].get(p2)
        if lugar1 != lugar2: return False

    if tipo == "coartada":
        p = next(t.replace("nombre_", "") for t in tags if "nombre_" in t)
        l = next(t.replace("fin_en_", "") for t in tags if "fin_en_" in t)
        
        # EL ASESINO Y EL CÓMPLICE MIENTEN JUNTOS: Usan el origen del arma como coartada
        if p == verdad["culpable"] or p == verdad.get("complice"):
            if slugify(verdad["origen_arma"]) != l: return False
        else:
            # LOS INOCENTES DICEN LA VERDAD: Declaran su posición final real
            if slugify(verdad["posiciones"][p]) != l: return False
        
        if p == verdad["culpable"]:
            # EL ASESINO MIENTE: Usa como coartada la sala donde robó el arma
            if slugify(verdad["origen_arma"]) != l: return False
        else:
            # LOS INOCENTES DICEN LA VERDAD: Declaran su posición final real
            if slugify(verdad["posiciones"][p]) != l: return False

    if tipo == "declaracion_soledad":
        p = next(t.replace("nombre_", "") for t in tags if "nombre_" in t)
        
        # LOS MALOS: Si son dos, NO pueden decir que estaban solos. Si el asesino actuó sin cómplice, usa la tapadera.
        if p == verdad["culpable"] or p == verdad.get("complice"):
            if verdad.get("complice"): return False # Se delatarían a sí mismos
            
            lugar_p = verdad["origen_arma"]
            testigos = list(verdad["posiciones"].values()).count(lugar_p)
            if testigos > 0: return False 
        else:
            # LOS INOCENTES: Dicen la verdad
            lugar_p = verdad["posiciones"][p]
            gente = list(verdad["posiciones"].values()).count(lugar_p)
            if gente > 1: return False

    if tipo == "evidencia_motivo":
        combo = f"evidencia_motivo_{slugify(verdad['motivo'])}_{slugify(verdad['culpable'])}"
        if combo not in tags: return False

    return True

# =============================================================================
# 6. CONSTRUCTOR Y MAIN
# =============================================================================

def construir_mazo(dificultad_str):
    dificultad_map = {"1": "Fácil", "2": "Intermedio", "3": "Difícil", "4": "Crimen Maestro"}
    nombre_dif = dificultad_map[dificultad_str]
    
    mazo_completo = cargar_cartas()
    if not mazo_completo: return None, None, None

    verdad = generar_verdad(dificultad_str)
    validas = [c for c in mazo_completo if es_carta_valida(c, verdad)]
    
    prob_lugar_limpio = 1.0
    prob_camara = 1.0
    max_camaras = 25
    
    if dificultad_str == "3": 
        prob_lugar_limpio = 0.6
        prob_camara = 0.6
        max_camaras = 15
    elif dificultad_str == "4": 
        prob_lugar_limpio = 0.3
        prob_camara = 0.4
        max_camaras = 10

    buckets = {"forense_clave": [], "lugar_limpio": [], "camaras": [], "bloqueos": [], "testimonios": [], "acusaciones": []}

    for c in validas:
        t = c["tipo"]
        if t == "lugar_limpio":
            if random.random() < prob_lugar_limpio: buckets["lugar_limpio"].append(c)
        elif "camara" in t:
            if random.random() < prob_camara: buckets["camaras"].append(c)
        elif t in ["bloqueo_paso"]:
            buckets["bloqueos"].append(c)
        elif "acusacion" in t:
            buckets["acusaciones"].append(c)
        elif t in ["coartada", "coartada_union", "declaracion_soledad"]:
            buckets["testimonios"].append(c)
        else:
            buckets["forense_clave"].append(c)

    seleccion = []
    seleccion.extend(buckets["forense_clave"])
    seleccion.extend(buckets["bloqueos"])
    seleccion.extend(buckets["lugar_limpio"])
    random.shuffle(buckets["camaras"])
    seleccion.extend(buckets["camaras"][:max_camaras])
    random.shuffle(buckets["acusaciones"])
    seleccion.extend(buckets["acusaciones"][:15])
    
    faltan = 100 - len(seleccion)
    random.shuffle(buckets["testimonios"])
    if faltan > 0:
        seleccion.extend(buckets["testimonios"][:faltan])
        
    if len(seleccion) < 100:
        extra = [c for c in validas if c not in seleccion]
        random.shuffle(extra)
        seleccion.extend(extra[:(100 - len(seleccion))])

    seleccion = seleccion[:100]
    seleccion.sort(key=lambda x: x['id'])
    return verdad, seleccion, nombre_dif

def main():
    print("\n🕵️  GENERADOR V11 (STRICT MODE) 🕵️")
    print("Selecciona Dificultad: [1-4]")
    opcion = input("> Opción: ").strip()
    if opcion not in ["1", "2", "3", "4"]: opcion = "2"
    
    verdad, mazo, nombre_dif = construir_mazo(opcion)
    if not verdad: return

    archivo_salida = f"partida_generada_{slugify(nombre_dif)}.json"
    output_data = {
        "metadata": {"dificultad": nombre_dif, "cartas_total": len(mazo)},
        "SOLUCION_SECRETA": {
            "Asesino": verdad['culpable'],
            "Arma": f"{verdad['arma']} (Origen: {verdad['origen_arma']})",
            "Móvil": verdad['motivo'],
            "Cómplice": verdad['complice'],
            "Rutas": {k: " -> ".join(v) for k, v in verdad['rutas'].items()}
        },
        "MAZO_DE_JUEGO": [{"id": c["id"], "tipo": c["tipo"], "texto": c["texto"]} for c in mazo]
    }
    with open(archivo_salida, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)
    print(f"\n✅ Guardado en {archivo_salida}")

if __name__ == "__main__":
    main()