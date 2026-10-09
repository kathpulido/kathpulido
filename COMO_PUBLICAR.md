# Cómo publicar el perfil

## 1. Crear el repositorio

En GitHub, crea un repositorio **público** con el mismo nombre de tu usuario (si tu usuario es `kpulido`, el repositorio se llama `kpulido`). GitHub te avisa que es un repositorio especial.

## 2. Subir los archivos

Sube todo lo que trae esta carpeta, **incluida la carpeta oculta `.github`**. Si la subes arrastrando archivos en la web de GitHub, revisa que `.github/workflows/widgets.yml` y `.github/widgets/3d-violeta.json` hayan quedado.

## 3. Poner tu usuario

En `README.md`, cambia `TU_USUARIO` por tu usuario. Aparece 3 veces: contador de visitas, gráfica de actividad y trofeos.

## 4. Encender los widgets

1. Ve a **Settings → Actions → General → Workflow permissions** y elige **Read and write permissions**. Guarda.
2. Ve a la pestaña **Actions**, abre **Widgets del perfil** y pulsa **Run workflow**.
3. En uno o dos minutos aparecen las estadísticas, los lenguajes, la racha, el relieve 3D y la serpiente. Mientras tanto se ve un marcador con el nombre de cada widget.

Después la acción se repite sola todos los días.

## Qué widget sale de dónde

| Widget | Cómo se genera |
| --- | --- |
| Estadísticas, lenguajes y racha | Acción en el repositorio (proyectos de código abierto) |
| Relieve 3D y serpiente | Acción en el repositorio (proyectos de código abierto) |
| Perfil de actividad y logros | Acción en el repositorio (`.github/widgets/widgets_propios.py`) |
| Banner, frase animada, separadores y onda final | Archivos fijos en `assets/` |
| Contador de visitas | Servicio público (komarev.com) |

La acción corre sola todos los días. Para forzarla: pestaña **Actions → Widgets del perfil → Run workflow**.

## Cambiar colores o frases

- **Widgets de la acción:** los colores están en `.github/workflows/widgets.yml` y en `.github/widgets/3d-violeta.json`.
- **Banner y frases animadas:** salen de `generar_svg.py`. Necesita Python con `numpy`, `contourpy` y `pyproj`:

```
pip install numpy contourpy pyproj
python generar_svg.py assets
```

Las frases están en la lista `FRASES` y el correo en `CORREO`. La retícula del banner está anclada al punto de origen de EPSG:9377 (4°N, 73°W), no a una ciudad.
