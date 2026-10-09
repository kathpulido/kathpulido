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

| Widget | Cómo se genera | Si falla |
| --- | --- | --- |
| Estadísticas y lenguajes | Acción en tu repositorio | Revisa la pestaña Actions |
| Racha de contribuciones | Acción en tu repositorio | Revisa la pestaña Actions |
| Relieve 3D | Acción en tu repositorio | Revisa la pestaña Actions |
| Serpiente (versión clara y oscura) | Acción en tu repositorio | Revisa la pestaña Actions |
| Contador de visitas | Servicio público (komarev.com) | Espera unas horas |
| Gráfica de actividad | Servicio público (Vercel) | Espera unas horas |
| Trofeos | Servicio público (Vercel) | Espera; el autor avisó que el servicio puede cerrar |
| Onda del final | Servicio público (Vercel) | Espera unas horas |

Los que se generan con la acción quedan guardados como archivos y no dependen de nadie. Los de servicio público pueden fallar por ratos cuando hay mucho tráfico.

## Cambiar colores o frases

- **Widgets de la acción:** los colores están en `.github/workflows/widgets.yml` y en `.github/widgets/3d-violeta.json`.
- **Banner y frases animadas:** salen de `generar_svg.py`. Necesita Python con `numpy`, `contourpy` y `pyproj`:

```
pip install numpy contourpy pyproj
python generar_svg.py assets
```

Las frases están en la lista `FRASES` y el correo en `CORREO`. La retícula del banner está anclada al punto de origen de EPSG:9377 (4°N, 73°W), no a una ciudad.
