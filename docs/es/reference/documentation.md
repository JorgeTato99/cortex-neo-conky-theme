# Mantener la documentación traducida

El `README.md` principal, su alias explícito `README.en.md` y `README.es.md` comparten una estructura Markdown. Cambiar de idioma traduce el mismo contenido; no selecciona secciones, capturas o ejemplos diferentes.

- Edita estructura, badges, referencias de imágenes, tablas y ejemplos ejecutables en `docs/readme/template.md.in`.
- Edita los textos en línea de `docs/readme/en.json` y `docs/readme/es.json`. Las claves deben coincidir. Los bloques de estructura Markdown y las imágenes pertenecen a la plantilla.
- Las dimensiones y el escalado provienen de `assets/screenshots/manifest.json`; no transcribas esos valores por separado en cada idioma.

```bash
python3 scripts/generate_readme.py
python3 scripts/generate_readme.py --check
python3 scripts/check_docs.py
```

Incluye catálogos/plantilla y README regenerados en el mismo commit. CI rechaza divergencias manuales, claves sin traducción y enlaces locales rotos. Para otro idioma del README, traduce el mismo catálogo y mantén sus rutas de documentación. Añadir un idioma al dashboard también requiere los catálogos y opciones de idioma de la aplicación; traducir el README no implementa por sí solo un idioma de ejecución.

El resumen muestra las mismas dos capturas recientes y reales en todos los idiomas. La [galería de paletas](appearance.md) mantiene las diez variantes y su procedencia fuera del README principal. Actualiza ambas galerías juntas, con el mismo orden e imágenes. Guarda únicamente capturas comprimidas sin pérdida tras comparar dimensiones y todos los píxeles decodificados con el original. Conserva PNG originales y evidencias operativas en `temp/`, excluido de Git.
