#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validador.py (Versión FINAL + Lógica de Accesibilidad/Veto)
"""

from __future__ import annotations
import json
import itertools
from typing import List, Dict, Any

CARTAS_FILE = "cartas.json"

# --- CONSTANTES ---
SOSPECHOSOS = ["Blanca", "Sergio", "Edu", "Alberto", "Fernando", "Javi"]
LUGAR_ASESINATO = "Cabina del DJ"

MOTIVOS = ["Una mujer", "Venganza", "Un bizum", "Un cigarro", "Borrachera", "Apuestas"]

MOTIVOS_POR_SOSPECHOSO: Dict[str, List[str]] = {
    "Sergio":   ["Una mujer", "Venganza", "Un bizum"],
    "Edu":      ["Un cigarro", "Borrachera", "Un bizum"],
    "Javi":     ["Venganza", "Apuestas", "Un cigarro"],
    "Fernando": ["Un bizum", "Apuestas", "Venganza"],
    "Blanca":   ["Borrachera", "Una mujer", "Un cigarro"],
    "Alberto":  ["Apuestas", "Borrachera", "Una mujer"]
}

LUGARES_ORIGEN = ["Ropero", "Baños", "Barra", "Terraza", "Sala de Seguridad", "Reservados"]

# 1. CATEGORÍAS DE ARMAS CORREGIDAS (SIN 'Colapso')
ARMAS_POR_CATEGORIA: Dict[str, List[str]] = {
    "Contundentes": ["Botella de Recompensa", "Balón de volleyball", "Polla de plástico", "Hielo del cubata"],
    "Venenos": ["Durum", "Un pelotazo", "Zurraspa", "Condón usado"],
    "Asfixiantes": ["Pedo", "Lefada de Gustavo", "Sobaco sudado", "Un vello púbico"],
    "Shock": ["Foto de la Bellido", "Beso de la Nana", "Uña del pie", "Clausulazo"],
    "De fuego": ["Cigarro", "Mechero trucado", "Eructo en la oreja", "Montapuercos"]
}

UBICACION_ARMAS: Dict[str, str] = {
    "Durum": "Ropero", "Un pelotazo": "Ropero", "Pedo": "Ropero",
    "Condón usado": "Baños", "Un vello púbico": "Baños", "Lefada de Gustavo": "Baños", "Zurraspa": "Baños",
    "Mechero trucado": "Barra", "Botella de Recompensa": "Barra", "Foto de la Bellido": "Barra", "Hielo del cubata": "Barra",
    "Sobaco sudado": "Terraza", "Montapuercos": "Terraza", "Balón de volleyball": "Terraza", "Eructo en la oreja": "Terraza",
    "Cigarro": "Sala de Seguridad", "Polla de plástico": "Sala de Seguridad",
    "Uña del pie": "Reservados", "Clausulazo": "Reservados", "Beso de la Nana": "Reservados"
}

# --- MATRIZ DE SÍNTOMAS ---
ARMAS_SINTOMAS = {
    # Contundentes
    "Botella de Recompensa": ["Contusión letal", "Abundante sangre"],
    "Balón de volleyball":   ["Contusión letal", "Colapso"], # Colapso como SÍNTOMA
    "Polla de plástico":     ["Contusión letal", "Abundante sangre"],
    "Hielo del cubata":      ["Contusión letal", "Quemaduras"],

    # Venenos
    "Durum":                 ["Envenenamiento", "Olores fuertes"],
    "Un pelotazo":           ["Envenenamiento", "Colapso"], # Colapso como SÍNTOMA
    "Zurraspa":              ["Envenenamiento", "Olores fuertes"],
    "Condón usado":          ["Envenenamiento", "Asfixia"],

    # Asfixiantes
    "Pedo":                  ["Asfixia", "Olores fuertes"],
    "Lefada de Gustavo":     ["Asfixia", "Envenenamiento"],
    "Sobaco sudado":         ["Asfixia", "Olores fuertes"],
    "Un vello púbico":       ["Asfixia", "Abundante sangre"],

    # Shock
    "Foto de la Bellido":    ["Shock", "Abundante sangre"],
    "Beso de la Nana":       ["Shock", "Contusión letal"],
    "Uña del pie":           ["Shock", "Abundante sangre"],
    "Clausulazo":            ["Shock", "Restos de pólvora"],

    # De fuego
    "Cigarro":               ["Quemaduras", "Olores fuertes"],
    "Mechero trucado":       ["Quemaduras", "Restos de pólvora"],
    "Eructo en la oreja":    ["Quemaduras", "Restos de pólvora"],
    "Montapuercos":          ["Quemaduras", "Restos de pólvora"]
}

# 2. CATÁLOGO DE SÍNTOMAS (Contiene 'Colapso', pero solo como síntoma)
SINTOMAS_CATALOGO = [
    "Contusión letal",
    "Abundante sangre",
    "Quemaduras",
    "Envenenamiento",
    "Olores fuertes",
    "Asfixia",
    "Colapso",
    "Restos de pólvora"
]

ARMAS = sorted(list(UBICACION_ARMAS.keys()))

def cargar_cartas(path: str = CARTAS_FILE) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

CARTAS = cargar_cartas()

def slugify(text: str) -> str:
    return text.lower().replace(" ", "_").replace("'", "").replace("ñ", "n")

def contradice(carta: Dict[str, Any], culpable: str, arma: str, lugar_origen: str, motivo: str) -> bool:
    tags = carta.get("tags", [])
    sintomas_solucion = ARMAS_SINTOMAS.get(arma, [])

    # 0. Imagen Personajes
    posibles_motivos = MOTIVOS_POR_SOSPECHOSO.get(culpable, [])
    if motivo not in posibles_motivos: return True 

    # 1. Culpable
    for s in SOSPECHOSOS:
        if f"inocente_{s}" in tags and culpable == s: return True
        if f"culpable_{s}" in tags and culpable != s: return True

    # 2. Mapa (Alibi - Ya existente)
    for l in LUGARES_ORIGEN:
        if f"lugar_sospechoso_{l}" in tags:
            persona_carta = next((t.replace("nombre_", "") for t in tags if t.startswith("nombre_")), None)
            if persona_carta == culpable:
                # Si el culpable estaba en L, y el arma estaba en lugar_origen, y son distintos...
                # El culpable NO pudo coger el arma.
                if lugar_origen != l: return True

    # 3. Armas
    for a in ARMAS:
        if f"arma_{a}" in tags and arma != a: return True
        if f"no_arma_{slugify(a)}" in tags and arma == a: return True

    # 4. Categorías
    for cat, lista_armas in ARMAS_POR_CATEGORIA.items():
        if f"categoria_{cat}" in tags and arma not in lista_armas: return True
        if f"no_categoria_{cat}" in tags and arma in lista_armas: return True

    # 5. Lugares (Descarte general)
    for l in LUGARES_ORIGEN:
        if f"lugar_{l}" in tags and lugar_origen != l: return True
        if f"no_lugar_{slugify(l)}" in tags and lugar_origen == l: return True

    # 6. Motivos
    for m in MOTIVOS:
        if f"motivo_{m}" in tags and motivo != m: return True
        if f"no_motivo_{slugify(m)}" in tags and motivo == m: return True

    # 7. Síntomas
    carta_sintomas = carta.get("sintomas", [])
    if carta_sintomas:
        for s in carta_sintomas:
            if s not in sintomas_solucion: return True
    for s in SINTOMAS_CATALOGO:
        if f"no_sintoma_{slugify(s)}" in tags and s in sintomas_solucion: return True

    # 8. --- NUEVO: ACCESIBILIDAD / VETO ---
    # "Si Sergio tenía vetado el Ropero, y el arma es el Durum (Ropero) -> Contradicción"
    tag_veto_origen = f"vetado_{slugify(lugar_origen)}_{culpable}"
    if tag_veto_origen in tags:
        return True
    
    # "Si Sergio tenía vetada la Cabina del DJ -> Contradicción (No pudo matar)"
    tag_veto_escena = f"vetado_{slugify(LUGAR_ASESINATO)}_{culpable}"
    if tag_veto_escena in tags:
        return True

    return False

def categoria_de_arma(arma: str) -> str | None:
    for categoria, armas in ARMAS_POR_CATEGORIA.items():
        if arma in armas: return categoria
    return None

def soluciones_compatibles(cartas_ids: List[int]) -> List[Dict[str, str]]:
    compatibles = []
    cartas_map = {c["id"]: c for c in CARTAS}
    cartas_seleccionadas = [cartas_map[cid] for cid in cartas_ids if cid in cartas_map]

    for culpable, arma, motivo in itertools.product(SOSPECHOSOS, ARMAS, MOTIVOS):
        if motivo not in MOTIVOS_POR_SOSPECHOSO[culpable]: continue
        lugar_origen = UBICACION_ARMAS.get(arma)
        if not lugar_origen: continue 

        contradice_algo = False
        for carta in cartas_seleccionadas:
            if contradice(carta, culpable, arma, lugar_origen, motivo):
                contradice_algo = True
                break
        
        if not contradice_algo:
            compatibles.append({
                "culpable": culpable,
                "arma": arma,
                "categoria_arma": categoria_de_arma(arma),
                "lugar_origen": lugar_origen,
                "lugar_asesinato": LUGAR_ASESINATO,
                "motivo": motivo,
                "sintomas": ARMAS_SINTOMAS.get(arma, [])
            })
    return compatibles