# LogiQD · .github

Perfil público de la organización en [github.com/LogiQD](https://github.com/LogiQD), con el mismo estilo que [logiqd.me](https://logiqd.me).

- `profile/README.md`: la presentación que se ve en la página de la organización. Las imágenes usan URL absolutas (`raw.githubusercontent.com`) para que también se vean en la app de GitHub del móvil.
- `profile/assets/`: secciones en SVG (claro y oscuro; la portada y la cinta de sectores van animadas), sus copias en PNG y los iconos.
- `scripts/build_profile.py`: regenera los SVG con las fuentes (Poppins e Inter, licencia OFL), el logo y las imágenes incrustadas.

```sh
pip install fonttools brotli
python3 scripts/build_profile.py
```

Las PNG de respaldo se sacan de los SVG (las versiones `-static`, sin animación) con un navegador a 2x.
