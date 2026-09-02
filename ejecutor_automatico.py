# -*- coding: utf-8 -*-
import subprocess
import schedule
import time
import datetime
import sys
import os

INTERVALO_HORAS = 6
RUTA_SCRIPT = os.path.join(os.path.dirname(__file__), "actualizar_datos.py")
ARCHIVO_LOG = os.path.join(os.path.dirname(__file__), "automatico.log")

def log(msg):
    hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mensaje = f"[{hora}] {msg}"
    print(mensaje, flush=True)
    try:
        with open(ARCHIVO_LOG, "a", encoding="utf-8") as f:
            f.write(mensaje + "\n")
    except Exception as e:
        print(f"No se pudo escribir en log: {e}", flush=True)

def ejecutar_actualizacion():
    log("=" * 60)
    log("Iniciando actualización de datos...")
    try:
        resultado = subprocess.run(
            [sys.executable, RUTA_SCRIPT],
            capture_output=True,
            text=True,
            timeout=300
        )
        if resultado.stdout:
            log("SALIDA:")
            for linea in resultado.stdout.strip().split("\n"):
                log(f"  {linea}")
        if resultado.returncode == 0:
            log("✓ Actualización completada exitosamente")
        else:
            log(f"✗ ERROR: código {resultado.returncode}")
            if resultado.stderr:
                log("ERRORES:")
                for linea in resultado.stderr.strip().split("\n"):
                    log(f"  {linea}")
    except subprocess.TimeoutExpired:
        log("✗ ERROR: Timeout (>5 minutos)")
    except FileNotFoundError:
        log(f"✗ ERROR: No encontré {RUTA_SCRIPT}")
    except Exception as e:
        log(f"✗ ERROR: {type(e).__name__}: {e}")
    log("=" * 60)

def main():
    log("EJECUTOR AUTOMÁTICO - El Boom Tractopartes")
    log(f"Intervalo: cada {INTERVALO_HORAS} horas")
    log("Ejecutando actualización inicial...")
    ejecutar_actualizacion()
    
    schedule.every(INTERVALO_HORAS).hours.do(ejecutar_actualizacion)
    log(f"Servicio iniciado. Presiona Ctrl+C para detener.\n")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        log("\nServicio detenido.")
        sys.exit(0)

if __name__ == "__main__":
    main()
