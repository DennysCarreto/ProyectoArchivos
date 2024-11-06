# Extractor de Datos GIF

**Autores:**
- Dennys Rolando Y. Carreto Aguilon
- María Luisa Cos Alvarez (Matrícula: 1567519)

## Resumen del Funcionamiento del Código

Este programa permite extraer, visualizar y gestionar datos de archivos GIF, mostrando detalles técnicos y metadatos. Está compuesto de dos clases principales:

### Clase `ExtractorGIF`

Esta clase se encarga de analizar archivos GIF en un directorio y extraer información clave, incluyendo:
- **Versión y dimensiones del GIF**
- **Cantidad de colores y formato de color**
- **Tipo de compresión (LZW)**
- **Fecha de creación y modificación**
- **Detalles de la paleta de colores y modo entrelazado**

Además, registra cualquier cambio realizado en los metadatos y guarda esta información en un archivo de log. Los datos extraídos se almacenan en un archivo JSON para persistencia entre sesiones.

### Clase `Aplicacion`

La interfaz gráfica, construida con `Tkinter`, permite al usuario seleccionar archivos GIF, explorar su información, y visualizar los detalles en una ventana dividida. Los principales componentes son:
- **Árbol de archivos**: Muestra los archivos GIF encontrados en el directorio.
- **Panel de detalles**: Proporciona una visualización de los datos técnicos del GIF, incluyendo botones para editar campos específicos y ver el historial de cambios.
- **Animación GIF**: Reproduce el archivo GIF seleccionado dentro de la aplicación.

### Funcionalidades Principales
- **Escaneo de Directorios**: Busca archivos GIF en el directorio indicado.
- **Visualización de Datos**: Muestra detalles técnicos y permite ver el historial de cambios.
- **Edición de Metadatos**: Posibilita la modificación de campos específicos y guarda los cambios en el archivo de log.
- **Reproducción de GIF**: Muestra la animación del GIF seleccionado en el panel de detalles.

Esta aplicación facilita la administración de archivos GIF y es útil para obtener datos de ellos de forma rápida y organizada.
