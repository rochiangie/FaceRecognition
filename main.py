import face_recognition
import os
import shutil
from PIL import Image, UnidentifiedImageError


# Rutas
carpeta_modelo = "C:\\Users\\rocio\\Documents\\Caras\\personaCami"
carpeta_backup = "D:\\AQUI TODO EL BACKUP"
carpeta_resultados = "C:\\Users\\rocio\\Documents\\Caras\\FotosEncontradasCami"
registro_procesadas = "procesadas.txt"  # Archivo para registrar imágenes procesadas

# Crear la carpeta de resultados si no existe
if not os.path.exists(carpeta_resultados):
    os.makedirs(carpeta_resultados)

# Cargar el registro de imágenes procesadas
if os.path.exists(registro_procesadas):
    with open(registro_procesadas, "r") as f:
        imagenes_procesadas = set(f.read().splitlines())
else:
    imagenes_procesadas = set()

# Función para cargar las caras de referencia
def cargar_caras_referencia(carpeta):
    rostros_referencia = []
    for archivo in os.listdir(carpeta):
        ruta_imagen = os.path.join(carpeta, archivo)
        imagen = face_recognition.load_image_file(ruta_imagen)
        try:
            encoding = face_recognition.face_encodings(imagen)[0]
            rostros_referencia.append(encoding)
        except IndexError:
            print(f"No se encontró ninguna cara en la imagen de referencia: {ruta_imagen}")
    return rostros_referencia

# Cargar las caras de referencia
rostros_referencia = cargar_caras_referencia(carpeta_modelo)

# Función para analizar y copiar fotos con coincidencia
def buscar_y_copiar_fotos(carpeta_busqueda, rostros_referencia):
    with open(registro_procesadas, "a") as f:  # Abre el archivo en modo de anexado
        for root, _, archivos in os.walk(carpeta_busqueda):
            for archivo in archivos:
                if archivo.lower().endswith(('.jpg', '.jpeg', '.png')):
                    ruta_imagen = os.path.join(root, archivo)
                    ruta_destino = os.path.join(carpeta_resultados, archivo)
                    
                    # Si la imagen ya está en el registro de procesadas o en la carpeta de resultados, omitir
                    if ruta_imagen in imagenes_procesadas or os.path.exists(ruta_destino):
                        print(f"Imagen ya procesada o existente en destino: {ruta_imagen}, omitiendo.")
                        continue
                    
                    print(f"Analizando {ruta_imagen}")
                    
                    # Intentar cargar la imagen
                    try:
                        imagen = face_recognition.load_image_file(ruta_imagen)
                        rostros_encontrados = face_recognition.face_encodings(imagen)
                    except (PIL.Image.DecompressionBombError, UnidentifiedImageError):
                        print(f"Imagen {archivo} es demasiado grande o inválida, omitiendo.")
                        imagenes_procesadas.add(ruta_imagen)
                        f.write(ruta_imagen + "\n")  # Guardar el registro de la imagen omitida
                        continue
                    
                    for rostro in rostros_encontrados:
                        coincidencias = face_recognition.compare_faces(rostros_referencia, rostro)
                        if True in coincidencias:
                            # Copiar la imagen si hay coincidencia
                            shutil.copy2(ruta_imagen, ruta_destino)
                            print(f"Foto encontrada y copiada a {ruta_destino}")
                            break  # No es necesario revisar más caras en esta foto
                    
                    # Guardar el registro de la imagen procesada
                    imagenes_procesadas.add(ruta_imagen)
                    f.write(ruta_imagen + "\n")

# Ejecutar la función de búsqueda y copia
buscar_y_copiar_fotos(carpeta_backup, rostros_referencia)
