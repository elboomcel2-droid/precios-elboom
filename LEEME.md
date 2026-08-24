# Consulta de precios · El Boom  (modo "PC automática")

Cómo funciona:

```
PC de la oficina (corre la consulta sola cada hora)
        │  publica un archivo de datos
        ▼
GitHub (gratis, guarda datos.json)
        ▼
App en el celular  →  un toque en "Actualizar" y baja los datos
```

La base solo la toca la PC (que ya tiene acceso). El celular nunca se conecta a
la base: solo baja un archivo. Por eso no hace falta servidor ni permiso de
Macronet. Después de bajar, la app funciona **sin internet**.

---

## PARTE A — Preparar GitHub (una sola vez, ~10 min)

1. Crea una cuenta gratis en https://github.com
2. Crea un repositorio **público** llamado `precios-elboom`
   (botón **New** → Repository name: `precios-elboom` → Public → Create).
3. Sube a ese repo estos archivos de la app (arrastrándolos en la web de GitHub,
   botón **Add file → Upload files**):
   `index.html`, `manifest.webmanifest`, `sw.js`,
   `icon-192.png`, `icon-512.png`, `icon-maskable-512.png`
4. Activa **GitHub Pages**: en el repo → **Settings → Pages** →
   Source: *Deploy from a branch* → Branch: `main` / carpeta `/root` → **Save**.
   A los ~2 min te da la dirección de la app:
   `https://TU_USUARIO.github.io/precios-elboom/`
   Esa dirección es la que se instala en los celulares.
5. Crea un **token** para que la PC pueda publicar:
   Foto de perfil → **Settings → Developer settings →
   Personal access tokens → Fine-grained tokens → Generate new token**.
   - Repository access: **Only select repositories** → elige `precios-elboom`.
   - Permissions → Repository permissions → **Contents: Read and write**.
   - Genera y **copia el token** (empieza con `github_pat_...`). Guárdalo, solo
     se ve una vez.

---

## PARTE B — Configurar la PC de la oficina (una sola vez)

Debe ser una PC que:
- esté encendida casi siempre, y
- ya pueda conectarse a la base (la misma donde usas Excel).

1. Instala **Python** desde https://www.python.org/downloads/
   (al instalar, marca la casilla **"Add Python to PATH"**).
2. Abre **Símbolo del sistema** (CMD) y ejecuta:
   ```
   pip install pymysql requests
   ```
3. Copia a una carpeta (por ejemplo `C:\PreciosElBoom\`) los archivos:
   `actualizar_datos.py` y `ejecutar.bat`
4. Abre `actualizar_datos.py` con el Bloc de notas y edita arriba:
   - `DB_PASS` = la contraseña (mejor un usuario de **solo lectura**).
   - `DB_NAME` = el nombre real de tu base de datos.
   - `GITHUB_TOKEN` = el token que copiaste.
   - `GITHUB_REPO` = `TU_USUARIO/precios-elboom`.
5. Prueba: doble clic en `ejecutar.bat`. Se abre una ventana negra, tarda unos
   segundos y se cierra. Revisa el archivo `actualizar.log` que se crea:
   debe decir *"Publicado correctamente"*.
   (Si dice error, ahí explica qué pasó: contraseña, base, o token.)

### Que corra sola cada hora (Programador de tareas)

1. Abre **Programador de tareas** de Windows → **Crear tarea básica**.
2. Nombre: `Actualizar precios El Boom`.
3. Desencadenador: **Diariamente** → repetir cada **1 hora** (en la pantalla de
   configuración avanzada, "Repetir cada: 1 hora" durante "1 día").
4. Acción: **Iniciar un programa** → Programa: busca y elige `ejecutar.bat`.
5. Finalizar. Listo: cada hora actualiza los datos solo.

---

## PARTE C — Instalar la app en los celulares

Abre en el teléfono la dirección de GitHub Pages
(`https://TU_USUARIO.github.io/precios-elboom/`):

- **Android (Chrome):** menú ⋮ → **Instalar aplicación**.
- **iPhone (Safari):** Compartir → **Agregar a pantalla de inicio**.

Dentro de la app:
1. Elige tu **sucursal** arriba (cambia al instante).
2. Toca **"Actualizar datos"** (la primera vez necesita internet).
3. Busca por código o descripción: ves **precio grande**, **existencia de tu
   sucursal**, y en chico la de las otras tres.

Arriba se muestra **"Datos del …"**: la fecha/hora en que la PC generó los datos,
para que sepas qué tan frescos están.

---

## Precios por zona (importante)

El precio sale de `inv_articulo_precio_grupo_almacenes` (nivel `orden = 1`) y hay
**dos precios por artículo**, según la zona, ya con IVA (× 1.16):
- **Zona 1 = Morelos** → Alpuyeca y Tizoc
- **Zona 2 = Guerrero** → Acapulco y Chilpancingo

La app muestra el precio de la zona según la sucursal que elijas. Ejemplo real
(art. 7277, costo 250): Morelos **$439.35**, Guerrero **$462.55**.

Si algún día cambias el % de IVA, se ajusta el `* 1.16` en la consulta del script.

## Notas

- La app baja los datos con un toque; los datos se refrescan tan seguido como
  corra la PC (cada hora, o lo que pongas en el Programador de tareas).
- Tras cada actualización de la PC, GitHub tarda ~1 min en reflejarla.
- Si prefieres que SOLO salgan artículos con existencia, en la consulta del
  script cambia `LEFT JOIN inv_existencia` por `INNER JOIN`.
- Si algún día te autorizan un servidor, se pasa a consulta 100% en vivo y este
  mismo esquema se reemplaza fácil.
- Si cambias `index.html`, sube la versión en `sw.js` (`precios-v4` → `v5`).
