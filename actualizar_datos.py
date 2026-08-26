# -*- coding: utf-8 -*-
"""
============================================================
actualizar_datos.py  ·  El Boom Tractopartes
Corre en una PC de la oficina (la que ya tiene acceso a la base).
1) Consulta precio + existencia de las 4 sucursales.
2) Arma un archivo datos.json compacto.
3) Lo publica en GitHub (desde ahí lo baja la app con un toque).

El token de GitHub vive SOLO en esta PC. La app nunca lo usa.
============================================================
Requisitos (una sola vez, en la PC):
    pip install pymysql requests
"""

import base64
import datetime
import json
import sys

import pymysql
import requests

# ===================== CONFIGURACIÓN =====================
# --- Base de datos (usa de preferencia un usuario de SOLO LECTURA) ---
DB_HOST = "104.192.4.18"
DB_USER = "sistemas"
DB_PASS = "Sis26teb"                 # <-- cámbiala; y mejor un usuario solo-lectura
DB_NAME = "tractopartes"        # <-- PON AQUÍ el nombre real de tu base

# --- GitHub (dónde se publica el archivo que baja la app) ---
GITHUB_TOKEN  = "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"         # token fino con permiso Contents: Read and write
GITHUB_REPO   = "elboomcel2-droid/precios-elboom" # usuario/repositorio
GITHUB_PATH   = "datos.json"                # nombre del archivo dentro del repo
GITHUB_BRANCH = "main"

# --- Mapa de sucursal -> id de inv_almacen ---
# Confirma que coincidan con tu tabla inv_almacen (3=Acapulco ya confirmado).
SUCURSALES = {1: "Alpuyeca", 2: "Tizoc", 3: "Acapulco", 4: "Chilpancingo"}
# =========================================================

CONSULTA = """
SELECT
    a.codigo        AS codigo,
    a.descripcion   AS descripcion,
    px.precio_morelos,
    px.precio_guerrero,
    COALESCE(ex.e1, 0) AS e1,
    COALESCE(ex.e2, 0) AS e2,
    COALESCE(ex.e3, 0) AS e3,
    COALESCE(ex.e4, 0) AS e4
FROM inv_articulo a
INNER JOIN inv_articulo_parametro p
    ON a.id = p.inv_articulo_id AND p.descontinuado <> 1
-- Precios agregados a UNA fila por artículo (grupo 1 = Morelos, grupo 2 = Guerrero), con IVA
INNER JOIN (
    SELECT articulo_id,
           ROUND(MAX(CASE WHEN grupo_id = 1 THEN precio END) * 1.16, 2) AS precio_morelos,
           ROUND(MAX(CASE WHEN grupo_id = 2 THEN precio END) * 1.16, 2) AS precio_guerrero
    FROM inv_articulo_precio_grupo_almacenes
    WHERE orden = 1 AND grupo_id IN (1, 2) AND moneda_id = 1
    GROUP BY articulo_id
) px ON px.articulo_id = a.id
-- Existencias agregadas a UNA fila por artículo (por separado, para no multiplicar)
LEFT JOIN (
    SELECT inv_articulo_id,
           SUM(CASE WHEN inv_almacen_id = 1 THEN cantidad_existencia END) AS e1,
           SUM(CASE WHEN inv_almacen_id = 2 THEN cantidad_existencia END) AS e2,
           SUM(CASE WHEN inv_almacen_id = 3 THEN cantidad_existencia END) AS e3,
           SUM(CASE WHEN inv_almacen_id = 4 THEN cantidad_existencia END) AS e4
    FROM inv_existencia
    GROUP BY inv_articulo_id
) ex ON ex.inv_articulo_id = a.id
"""


def log(msg):
    hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{hora}] {msg}", flush=True)


def consultar_datos():
    log("Conectando a la base de datos...")
    conn = pymysql.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME,
        charset="utf8mb4", cursorclass=pymysql.cursors.Cursor, connect_timeout=20,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(CONSULTA)
            filas = cur.fetchall()
    finally:
        conn.close()
    log(f"Se obtuvieron {len(filas)} artículos.")

    # Compacto: cada fila =
    #   [codigo, descripcion, precio_morelos, precio_guerrero, e1, e2, e3, e4]
    rows = []
    for f in filas:
        codigo = "" if f[0] is None else str(f[0]).strip()
        if not codigo:
            continue
        desc = "" if f[1] is None else str(f[1]).strip()
        precio_mor = round(float(f[2]), 2) if f[2] is not None else 0.0
        precio_gro = round(float(f[3]), 2) if f[3] is not None else 0.0
        e1 = float(f[4]) if f[4] is not None else 0.0
        e2 = float(f[5]) if f[5] is not None else 0.0
        e3 = float(f[6]) if f[6] is not None else 0.0
        e4 = float(f[7]) if f[7] is not None else 0.0
        rows.append([codigo, desc, precio_mor, precio_gro, e1, e2, e3, e4])

    return {
        "fecha": datetime.datetime.now().isoformat(timespec="minutes"),
        "sucursales": {str(k): v for k, v in SUCURSALES.items()},
        # zona de cada sucursal: 1 = Morelos, 2 = Guerrero
        "zonas": {"1": 1, "2": 1, "3": 2, "4": 2},
        "rows": rows,
    }


def publicar_en_github(datos):
    contenido = json.dumps(datos, ensure_ascii=False, separators=(",", ":"))
    contenido_b64 = base64.b64encode(contenido.encode("utf-8")).decode("ascii")

    api = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{GITHUB_PATH}"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    # ¿Ya existe el archivo? (para obtener su SHA y actualizarlo)
    sha = None
    r = requests.get(api, headers=headers, params={"ref": GITHUB_BRANCH}, timeout=30)
    if r.status_code == 200:
        sha = r.json().get("sha")

    cuerpo = {
        "message": f"Actualiza datos {datos['fecha']}",
        "content": contenido_b64,
        "branch": GITHUB_BRANCH,
    }
    if sha:
        cuerpo["sha"] = sha

    log(f"Publicando en GitHub ({'actualizar' if sha else 'crear'})...")
    r = requests.put(api, headers=headers, data=json.dumps(cuerpo), timeout=60)
    if r.status_code in (200, 201):
        kb = len(contenido.encode("utf-8")) / 1024
        log(f"Publicado correctamente ({kb:.0f} KB, {len(datos['rows'])} artículos).")
    else:
        log(f"ERROR al publicar: {r.status_code} {r.text[:300]}")
        sys.exit(1)


def main():
    try:
        datos = consultar_datos()
        if not datos["rows"]:
            log("La consulta no devolvió artículos. No se publica nada.")
            sys.exit(1)
        publicar_en_github(datos)
        log("Listo.")
    except Exception as e:
        log(f"FALLÓ: {type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

