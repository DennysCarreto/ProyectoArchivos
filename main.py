import os
import struct
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, simpledialog
import json
from datetime import datetime

class ExtractorGIF:
    def __init__(self):
        self.archivo_datos = "datos_gif.json"
        self.datos_gif = {}
        
    def leer_datos_gif(self, ruta_archivo):
        try:
            with open(ruta_archivo, 'rb') as f:
                # Leer cabecera GIF
                cabecera = f.read(6)
                version = cabecera[3:6].decode('ascii')
                
                # Leer descriptor de pantalla lógica
                datos_pantalla = struct.unpack("<HHBBB", f.read(7))
                ancho, alto, empaquetado, color_fondo, ratio_aspecto = datos_pantalla
                
                # Decodificar información empaquetada
                tabla_colores_global = (empaquetado & 0x80) != 0
                resolucion_color = ((empaquetado & 0x70) >> 4) + 1
                ordenado = (empaquetado & 0x08) != 0
                tam_tabla_colores = 2 << (empaquetado & 0x07)
                
                # Leer tabla de colores global si existe
                colores_globales = []
                if tabla_colores_global:
                    for i in range(tam_tabla_colores):
                        colores_globales.append(struct.unpack("BBB", f.read(3)))
                
                # Leer bloques
                contador_imagenes = 0
                comentarios = []
                tipo_compresion = "LZW"
                
                while True:
                    tipo_bloque = f.read(1)
                    
                    if tipo_bloque == b'\x2C':  # Descriptor de imagen
                        contador_imagenes += 1
                        # Leer datos de imagen
                        img_x, img_y, img_ancho, img_alto, img_empaquetado = struct.unpack("<HHHHB", f.read(9))
                        
                        # Procesar flags de imagen
                        tabla_local = (img_empaquetado & 0x80) != 0
                        entrelazado = (img_empaquetado & 0x40) != 0
                        ordenado_local = (img_empaquetado & 0x20) != 0
                        tam_tabla_local = 2 << (img_empaquetado & 0x07)
                        
                        if tabla_local:
                            f.read(3 * tam_tabla_local)  # Saltar tabla local
                            
                        # Leer datos de imagen comprimidos
                        f.read(1)  # Tamaño mínimo LZW
                        while True:
                            tam_bloque = ord(f.read(1))
                            if tam_bloque == 0:
                                break
                            f.read(tam_bloque)
                            
                    elif tipo_bloque == b'\x21':  # Bloque de extensión
                        tipo_ext = f.read(1)
                        if tipo_ext == b'\xFE':  # Comentario
                            tam = ord(f.read(1))
                            comentarios.append(f.read(tam).decode('ascii', errors='replace'))
                        else:
                            # Saltar otros tipos de extensión
                            while True:
                                tam = ord(f.read(1))
                                if tam == 0:
                                    break
                                f.read(tam)
                                
                    elif tipo_bloque == b'\x3B' or not tipo_bloque:  # Fin de archivo
                        break
                
                # Obtener metadatos del archivo
                info_archivo = os.stat(ruta_archivo)
                fecha_creacion = datetime.fromtimestamp(info_archivo.st_ctime)
                fecha_modificacion = datetime.fromtimestamp(info_archivo.st_mtime)
                
                # Información adicional útil
                paleta_adaptativa = "Sí" if tabla_colores_global else "No"
                modo_entrelazado = "Sí" if 'entrelazado' in locals() and entrelazado else "No"
                tam_archivo = os.path.getsize(ruta_archivo)
                
                return {
                    # Información requerida
                    "Versión": version,
                    "Dimensiones": f"{ancho}x{alto} píxeles",
                    "Cantidad de colores": tam_tabla_colores,
                    "Tipo de compresión": tipo_compresion,
                    "Formato numérico": f"{resolucion_color} bits por color",
                    "Color de fondo": color_fondo,
                    "Cantidad de imágenes": contador_imagenes,
                    "Fecha de creación": fecha_creacion.strftime("%d/%m/%Y %H:%M:%S"),
                    "Fecha de modificación": fecha_modificacion.strftime("%d/%m/%Y %H:%M:%S"),
                    "Comentarios": comentarios,
                    
                    # Información adicional
                    "Tamaño de archivo": f"{tam_archivo/1024:.2f} KB",
                    "Paleta adaptativa": paleta_adaptativa,
                    "Modo entrelazado": modo_entrelazado,
                    "Ratio de aspecto": ratio_aspecto,
                    "Orden de colores": "Ordenado" if ordenado else "No ordenado",
                    "Ruta del archivo": ruta_archivo
                }
        except Exception as e:
            print(f"Error al leer {ruta_archivo}: {str(e)}")
            return None

    def escanear_directorio(self, directorio):
        for raiz, dirs, archivos in os.walk(directorio):
            for archivo in archivos:
                if archivo.lower().endswith('.gif'):
                    ruta_archivo = os.path.join(raiz, archivo)
                    datos = self.leer_datos_gif(ruta_archivo)
                    if datos:
                        self.datos_gif[ruta_archivo] = datos
        
        self.guardar_datos()

    def guardar_datos(self):
        with open(self.archivo_datos, 'w', encoding='utf-8') as f:
            json.dump(self.datos_gif, f, indent=2, ensure_ascii=False)

    def cargar_datos(self):
        if os.path.exists(self.archivo_datos):
            with open(self.archivo_datos, 'r', encoding='utf-8') as f:
                self.datos_gif = json.load(f)

    def actualizar_datos_gif(self, ruta_archivo, clave, valor):
        if ruta_archivo in self.datos_gif:
            self.datos_gif[ruta_archivo][clave] = valor
            self.guardar_datos()

class Aplicacion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Extractor de datos GIF")
        self.geometry("1200x700")
        
        self.extractor = ExtractorGIF()
        self.ruta_actual = None

        if not os.path.exists(self.extractor.archivo_datos):
            self.solicitar_directorio()
        else:
            self.extractor.cargar_datos()
        
        self.crear_widgets()
        self.estilo = ttk.Style()
        self.estilo.configure("Treeview", rowheight=25)

    def solicitar_directorio(self):
        directorio = filedialog.askdirectory(title="Seleccionar directorio con archivos GIF")
        if directorio:
            self.extractor.escanear_directorio(directorio)

    def crear_widgets(self):
        # Panel principal dividido
        self.panel_principal = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.panel_principal.pack(fill=tk.BOTH, expand=1)

        # Panel izquierdo: Árbol de archivos
        self.frame_arbol = ttk.Frame(self.panel_principal)
        self.panel_principal.add(self.frame_arbol, weight=1)

        # Etiqueta de archivos
        ttk.Label(self.frame_arbol, text="Archivos GIF encontrados:", font=('Helvetica', 10, 'bold')).pack(pady=5)

        # Árbol de archivos con scrollbar
        self.arbol = ttk.Treeview(self.frame_arbol, columns=("tamaño", "fecha"))
        self.arbol.heading("#0", text="Nombre")
        self.arbol.heading("tamaño", text="Tamaño")
        self.arbol.heading("fecha", text="Fecha modificación")
        
        scrollbar_arbol = ttk.Scrollbar(self.frame_arbol, orient="vertical", command=self.arbol.yview)
        self.arbol.configure(yscrollcommand=scrollbar_arbol.set)
        
        self.arbol.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_arbol.pack(side=tk.RIGHT, fill=tk.Y)

        # Panel derecho: Detalles
        self.frame_detalles = ttk.Frame(self.panel_principal)
        self.panel_principal.add(self.frame_detalles, weight=2)

        # Canvas para scroll en detalles
        self.canvas_detalles = tk.Canvas(self.frame_detalles)
        scrollbar_detalles = ttk.Scrollbar(self.frame_detalles, orient="vertical", command=self.canvas_detalles.yview)
        
        self.frame_interno = ttk.Frame(self.canvas_detalles)
        self.canvas_detalles.create_window((0, 0), window=self.frame_interno, anchor="nw")
        
        self.canvas_detalles.configure(yscrollcommand=scrollbar_detalles.set)
        self.frame_interno.bind("<Configure>", lambda e: self.canvas_detalles.configure(scrollregion=self.canvas_detalles.bbox("all")))
        
        self.canvas_detalles.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_detalles.pack(side=tk.RIGHT, fill=tk.Y)

        # Barra de herramientas
        frame_botones = ttk.Frame(self)
        frame_botones.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        ttk.Button(frame_botones, text="Agregar directorio", command=self.agregar_directorio).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Actualizar datos", command=self.actualizar_datos).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botones, text="Acerca de", command=self.mostrar_acerca_de).pack(side=tk.RIGHT, padx=5)

        self.arbol.bind("<<TreeviewSelect>>", self.al_seleccionar)
        self.actualizar_arbol()

    def actualizar_arbol(self):
        for item in self.arbol.get_children():
            self.arbol.delete(item)

        for ruta, datos in self.extractor.datos_gif.items():
            nombre = os.path.basename(ruta)
            tamaño = datos.get("Tamaño", "")
            fecha = datos.get("Fecha de modificación", "")
            self.arbol.insert("", "end", text=nombre, values=(tamaño, fecha), tags=(ruta,))

    def al_seleccionar(self, evento):
        seleccion = self.arbol.selection()
        if not seleccion:
            return
            
        self.ruta_actual = self.arbol.item(seleccion[0])['tags'][0]
        datos = self.extractor.datos_gif[self.ruta_actual]
        
        # Limpiar frame de detalles
        for widget in self.frame_interno.winfo_children():
            widget.destroy()

        # Título
        ttk.Label(self.frame_interno, text="Información del archivo GIF", 
                 font=('Helvetica', 12, 'bold')).pack(pady=10)
        ttk.Label(self.frame_interno, text=os.path.basename(self.ruta_actual), 
                 font=('Helvetica', 10)).pack(pady=(0,10))

        # Mostrar datos en grupos
        self.mostrar_grupo_datos("Información básica", {
            k: datos[k] for k in [
                "Versión", "Dimensiones", "Tamaño de archivo", 
                "Cantidad de colores", "Formato numérico"
            ]
        })
        
        self.mostrar_grupo_datos("Características técnicas", {
            k: datos[k] for k in [
                "Tipo de compresión", "Paleta adaptativa", 
                "Modo entrelazado", "Orden de colores"
            ]
        })
        
        self.mostrar_grupo_datos("Metadatos", {
            k: datos[k] for k in [
                "Fecha de creación", "Fecha de modificación", 
                "Cantidad de imágenes", "Comentarios"
            ]
        })

        self.canvas_detalles.update_idletasks()
        self.canvas_detalles.configure(scrollregion=self.canvas_detalles.bbox("all"))

    def mostrar_grupo_datos(self, titulo, datos):
        frame_grupo = ttk.LabelFrame(self.frame_interno, text=titulo, padding=10)
        frame_grupo.pack(fill=tk.X, padx=10, pady=5)

        for clave, valor in datos.items():
            frame = ttk.Frame(frame_grupo)
            frame.pack(fill=tk.X, pady=2)

            ttk.Label(frame, text=f"{clave}:", width=20).pack(side=tk.LEFT)
            
            if isinstance(valor, list):
                valor_str = ", ".join(map(str, valor)) if valor else "Ninguno"
            else:
                valor_str = str(valor)

            ttk.Label(frame, text=valor_str).pack(side=tk.LEFT, padx=5)
            ttk.Button(frame, text="Editar", 
                      command=lambda k=clave, v=valor: self.editar_valor(k, v, self.ruta_actual)).pack(side=tk.RIGHT)

    def editar_valor(self, clave, valor, ruta):
        if isinstance(valor, list):
            nuevo_valor = simpledialog.askstring(
                "Editar valor", 
                f"Editar {clave} (separar elementos con coma):",
                initialvalue=", ".join(map(str, valor))
            )
            if nuevo_valor is not None:
                nuevo_valor = [item.strip() for item in nuevo_valor.split(",")]
        else:
            nuevo_valor = simpledialog.askstring(
                "Editar valor", 
                f"Editar {clave}:",
                initialvalue=str(valor)
            )
        
        if nuevo_valor is not None:
            self.extractor.actualizar_datos_gif(ruta, clave, nuevo_valor)
            self.al_seleccionar(None)

    def agregar_directorio(self):
        directorio = filedialog.askdirectory(
            title="Seleccionar directorio con archivos GIF",
            mustexist=True
        )
        if directorio:
            self.extractor.escanear_directorio(directorio)
            self.actualizar_arbol()
            messagebox.showinfo(
                "Éxito",
                f"Directorio agregado correctamente\nArchivos GIF encontrados: {len(self.extractor.datos_gif)}"
            )

    def actualizar_datos(self):
        archivos_eliminados = 0
        archivos_actualizados = 0
        
        # Verificar archivos existentes y actualizar datos
        for ruta in list(self.extractor.datos_gif.keys()):
            if not os.path.exists(ruta):
                del self.extractor.datos_gif[ruta]
                archivos_eliminados += 1
            else:
                nuevos_datos = self.extractor.leer_datos_gif(ruta)
                if nuevos_datos:
                    self.extractor.datos_gif[ruta] = nuevos_datos
                    archivos_actualizados += 1
        
        self.extractor.guardar_datos()
        self.actualizar_arbol()
        
        messagebox.showinfo(
            "Actualización completada",
            f"Proceso finalizado:\n"
            f"- Archivos actualizados: {archivos_actualizados}\n"
            f"- Archivos eliminados: {archivos_eliminados}"
        )

    def mostrar_acerca_de(self):
        ventana_acerca = tk.Toplevel(self)
        ventana_acerca.title("Acerca de")
        ventana_acerca.geometry("400x300")
        ventana_acerca.resizable(False, False)
        
        # Hacer la ventana modal
        ventana_acerca.transient(self)
        ventana_acerca.grab_set()
        
        # Contenido
        ttk.Label(
            ventana_acerca,
            text="Extractor de datos GIF",
            font=('Helvetica', 14, 'bold')
        ).pack(pady=20)
        
        ttk.Label(
            ventana_acerca,
            text="Versión 1.0",
            font=('Helvetica', 10)
        ).pack()
        
        ttk.Label(
            ventana_acerca,
            text=("Esta aplicación permite extraer y visualizar\n"
                  "información técnica de archivos GIF,\n"
                  "incluyendo metadatos y características específicas."),
            justify=tk.CENTER
        ).pack(pady=20)
        
        ttk.Label(
            ventana_acerca,
            text="Características principales:",
            font=('Helvetica', 10, 'bold')
        ).pack(pady=(10, 5))
        
        caracteristicas = [
            "• Lectura de archivos GIF sin bibliotecas externas",
            "• Análisis recursivo de directorios",
            "• Edición de metadatos",
            "• Actualización automática de datos",
            "• Interfaz gráfica intuitiva"
        ]
        
        for caracteristica in caracteristicas:
            ttk.Label(
                ventana_acerca,
                text=caracteristica
            ).pack()
        
        ttk.Button(
            ventana_acerca,
            text="Cerrar",
            command=ventana_acerca.destroy
        ).pack(pady=20)

    def confirmar_salida(self):
        if messagebox.askokcancel("Salir", "¿Desea salir de la aplicación?"):
            self.quit()

    def iniciar(self):
        self.protocol("WM_DELETE_WINDOW", self.confirmar_salida)
        self.mainloop()

class ExcepcionGIF(Exception):
    """Excepción personalizada para errores relacionados con archivos GIF"""
    pass

def main():
    try:
        app = Aplicacion()
        app.iniciar()
    except Exception as e:
        messagebox.showerror(
            "Error fatal",
            f"Ha ocurrido un error inesperado:\n{str(e)}\n\nLa aplicación se cerrará."
        )
        raise

if __name__ == "__main__":
    main()