import requests
import zipfile
import io
import datetime
import time

CALMA_STR = 'Calma'
URL_DESCARGA = 'https://ssl.smn.gob.ar/dpd/zipopendata.php?dato='
PARAM_TIEMPO = 'tiepre'
TEXT_ENCODING = 'latin-1'

def descargar_datos(param):
    r = requests.get(URL_DESCARGA + param)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    nombre = z.namelist()[0]
    return list(io.TextIOWrapper(z.open(nombre), TEXT_ENCODING))

def extraer_datos_climaticos():
    data = [renglon.lstrip().rstrip()[:-2].split(';') for renglon
            in descargar_datos(PARAM_TIEMPO)]
    tiempo = {}
    for linea in data:
        estacion = linea[0]
        temperatura_str = linea[5]
        if temperatura_str == '---':
            # Puedes establecer un valor predeterminado, por ejemplo, None
            temperatura = None
        else:
            temperatura = round(float(temperatura_str), 1)
        
        sensacion_termica_str = linea[6]
        if sensacion_termica_str == '---' or 'No se calcula' in sensacion_termica_str:
            # Si no hay sensación térmica, toma el valor de la temperatura
            sensacion_termica = temperatura
        else:
            sensacion_termica = round(float(sensacion_termica_str), 1)
        
        tiempo[estacion] = {'temperatura': temperatura, 'sensacion_termica': sensacion_termica}
    return tiempo

def actualizar_datos_climaticos_en_archivos():
    while True:
        datos_climaticos = extraer_datos_climaticos()
        if 'Buenos Aires' in datos_climaticos:
            temperatura_actual = datos_climaticos['Buenos Aires']['temperatura']
            sensacion_termica_actual = datos_climaticos['Buenos Aires']['sensacion_termica']
            
            # Mostrar en la consola
            print(f' {temperatura_actual}° ')
            if sensacion_termica_actual is not None:
                print(f' ST {sensacion_termica_actual}° ')
            else:
                print('ST No disponible ')
            
            # Guardar en el archivo de temperatura
            with open('temperatura_actual_buenos_aires.txt', 'w', encoding='utf-8') as archivo_temperatura:
                if temperatura_actual is not None:
                    archivo_temperatura.write(f' {temperatura_actual}° ')
                else:
                    archivo_temperatura.write(' No disponible ')
                
            # Guardar en el archivo de sensación térmica
            with open('sensacion_termica_buenos_aires.txt', 'w', encoding='utf-8') as archivo_sensacion_termica:
                if sensacion_termica_actual is not None:
                    archivo_sensacion_termica.write(f' ST {sensacion_termica_actual}° ')
                else:
                    archivo_sensacion_termica.write(' No disponible ')
                
        time.sleep(300)  # Espera 5 minutos antes de la próxima actualización

if __name__ == "__main__":
    actualizar_datos_climaticos_en_archivos()