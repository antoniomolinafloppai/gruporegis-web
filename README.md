# Menhir Recycling — Web corporativa

Sitio web estático de **Menhir Recycling**, empresa dedicada al reciclaje industrial, la sostenibilidad ambiental y la cooperación internacional.

Réplica en HTML/CSS/JS del sitio [menhirrecycling.com](https://www.menhirrecycling.com/), optimizada para SEO y rendimiento.

## Características

- HTML5 semántico con jerarquía correcta de encabezados
- Meta tags, Open Graph, Twitter Cards y datos estructurados (JSON-LD)
- Diseño responsive (móvil, tablet y escritorio)
- Sitio bilingüe (inglés / español) mediante páginas separadas y etiquetas `hreflang`
- `robots.txt` y `sitemap.xml` incluidos
- Banner de cookies con preferencias básicas
- Sin dependencias de build: listo para servir como sitio estático

## Estructura del proyecto

```
menhir-recycling/
├── index.html          # Página principal (inglés)
├── es/
│   └── index.html      # Página principal (español)
├── css/
│   └── styles.css      # Estilos
├── js/
│   └── main.js         # Navegación móvil y cookies
├── images/             # Imágenes del sitio
│   ├── menhir.png
│   ├── menhirrecycling-black.png
│   ├── menhir-logo.svg
│   ├── logo-brand-only.svg
│   ├── hero-bg.png
│   ├── tire-recycling.png
│   ├── plastic-recycling.png
│   ├── marine-protection.jpg
│   └── clean-planet.jpg
├── robots.txt
├── sitemap.xml
├── scrape_images.py    # Script auxiliar para descargar imágenes del sitio original
└── README.md
```

## Cómo ejecutarlo en local

Abre `index.html` directamente en el navegador o usa un servidor local:

```bash
# Python 3
python -m http.server 8080
```

Visita `http://localhost:8080`.

## Script de scraping de imágenes

`scrape_images.py` descarga las imágenes del sitio original. Usa solo la biblioteca estándar de Python.

```bash
# Descargar imágenes
python scrape_images.py

# Ver URLs sin descargar
python scrape_images.py --dry-run

# Carpeta de destino personalizada
python scrape_images.py --output scraped-images
```

Las imágenes se guardan en `scraped-images/` por defecto, fuera de la carpeta `images/` del sitio.

## Despliegue

Al ser un sitio estático, se puede publicar en cualquier hosting de archivos estáticos:

- GitHub Pages
- Netlify
- Vercel
- Servidor web (Nginx, Apache, etc.)

Solo hay que subir el contenido del repositorio manteniendo la estructura de carpetas.

## Contacto

- **Email:** info@menhirrecycling.com
- **Teléfono:** +34 936 711 241
- **N.º identificación reciclaje:** 10902

## Repositorio

[github.com/antoniomolinafloppai/gruporegis-web](https://github.com/antoniomolinafloppai/gruporegis-web)
