# Consulta de Precios · El Boom

Aplicación web para consultar precios de artículos con inventario por sucursal. **Funciona sin internet** después de la primera actualización.

## Características

- 🔍 **Búsqueda rápida** por código o descripción
- 🏪 **Stock por sucursal**: Alpuyeca, Tizoc, Acapulco, Chilpancingo
- 📱 **PWA** (instalable en mobile)
- 🔌 **Offline first** - funciona sin internet
- 🎨 **Diseño oscuro y moderno**

## Estructura de datos

La app espera un archivo `datos.json` con este formato:

```json
{
  "fecha": "2026-08-21T10:30:00Z",
  "rows": [
    ["COD001", "Descripción del producto", 1500.00, 10, 5, 8, 3],
    ["COD002", "Otro artículo", 2500.50, 0, 12, 5, 8]
  ]
}
```

### Formato de cada fila:
`[código, descripción, precio, stock_Alpuyeca, stock_Tizoc, stock_Acapulco, stock_Chilpancingo]`

- **código**: SKU único del artículo
- **descripción**: Nombre del producto
- **precio**: Precio en MXN
- **stock_***: Unidades disponibles en cada sucursal (usar `null` si no hay)

## Despliegue en GitHub Pages

1. Los archivos ya están en el repositorio
2. Ve a **Settings → Pages**
3. Selecciona **Source**: Branch: `main`, Folder: `/ (root)`
4. Guarda
5. La app estará disponible en: `https://elboomcel2-droid.github.io/precios-elboom/`

## Desarrollo local

```bash
# Servir con Python
python -m http.server 8000

# O con Node.js
npx http-server
```

Luego abre `http://localhost:8000`

## Iconos PWA

Necesitas subir estos archivos (no incluidos):
- `icon-192.png` (192×192)
- `icon-512.png` (512×512)  
- `icon-maskable-512.png` (512×512, maskable)

Si no tienes los iconos, descomentar las líneas en `manifest.webmanifest` que hace referencia a ellos.

## Notas técnicas

- **IndexedDB**: Almacena los datos locales en el móvil
- **Service Worker** (`sw.js`): Cachea la app, pero NO los datos (para que siempre se actualicen)
- **Búsqueda**: 50 resultados máximo, ordenados por coincidencia exacta
- **Zona horaria**: México Central (es-MX)
