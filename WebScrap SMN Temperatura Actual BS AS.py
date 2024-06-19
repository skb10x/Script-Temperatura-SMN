from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from pywinauto import Desktop, Application

def check_chromedriver():
    try:
        # Configurar las opciones de Chrome para deshabilitar la geolocalización
        chrome_options = Options()
        chrome_options.add_argument("--disable-geolocation")

        # Inicializar el servicio de ChromeDriver con las opciones
        service = Service(ChromeDriverManager().install())

        # Inicializar el navegador Chrome con las opciones y el servicio
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("ChromeDriver encontrado en el sistema.")
        return driver
    except:
        print("ChromeDriver no encontrado en el sistema.")
        return install_chromedriver()

def install_chromedriver():
    print("Intentando instalar ChromeDriver...")
    try:
        # Instalar ChromeDriver automáticamente utilizando webdriver_manager
        driver = webdriver.Chrome(ChromeDriverManager().install())
        print("ChromeDriver instalado correctamente.")
        return driver
    except Exception as e:
        print("Error al instalar ChromeDriver:", e)
        return None

def set_location(driver, latitude, longitude, accuracy):
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "accuracy": accuracy
    }
    driver.execute_cdp_cmd("Page.setGeolocationOverride", params)

def format_data(temperatura_text, sensacion_termica_text, humedad_text):
    # Formatear la temperatura
    temperatura = temperatura_text.replace("°c", "").replace("°C", "").strip()
    if temperatura:
        temperatura = " {:.1f}° ".format(float(temperatura))
    else:
        temperatura = " N/A "

    # Formatear la sensación térmica
    sensacion_termica = sensacion_termica_text.replace("ST ", "").replace("°C", "").strip()
    if sensacion_termica:
        sensacion_termica = " ST {:.1f}° ".format(float(sensacion_termica))
    else:
        # Si la sensación térmica es nula, asignar el valor de la temperatura
        sensacion_termica = " ST {} ".format(temperatura)

    # Formatear la humedad
    humedad = humedad_text.replace("%", "").strip()
    if humedad:
        humedad = " H {}% ".format(int(humedad))
    else:
        humedad = " N/A "

    return temperatura, sensacion_termica, humedad

def scrape_smn():
    driver = check_chromedriver()
    if driver:
        try:
            # Establecer la ubicación en Ciudad Autónoma de Buenos Aires
            set_location(driver, -34.603683, -58.381557, 100)

            # URL del sitio web
            url = "https://www.smn.gob.ar/"

            # Obtener la página
            driver.get(url)

            # Minimizar la ventana del navegador
            minimize_browser_window(driver)

            # Esperar un momento para que se cargue la página completamente
            time.sleep(5)  # Puedes ajustar este tiempo según la velocidad de tu conexión

            # Encontrar los elementos de interés y obtener sus textos
            temperatura_text = driver.find_element(By.ID, "estado_tempDesc").text
            sensacion_termica_text = driver.find_element(By.ID, "estado_st").text
            humedad_text = driver.find_element(By.ID, "estado_humidity").text
            ultima_actualizacion = driver.find_element(By.ID, "estado_actualizado").text

            # Cerrar el navegador
            driver.quit()

            # Formatear los datos
            temperatura, sensacion_termica, humedad = format_data(temperatura_text, sensacion_termica_text, humedad_text)

            # Imprimir los datos obtenidos
            print("Temperatura:", temperatura)
            print("Sensación térmica:", sensacion_termica)
            print("Humedad:", humedad)
            print("Última actualización:", ultima_actualizacion)

            # Exportar los datos a archivos txt en formato UTF-8
            with open("temperatura.txt", "w", encoding="utf-8") as file:
                file.write(temperatura)
            with open("sensacion_termica.txt", "w", encoding="utf-8") as file:
                file.write(sensacion_termica)
            with open("humedad.txt", "w", encoding="utf-8") as file:
                file.write(humedad)
        except Exception as e:
            print("Error al realizar scraping:", e)

def minimize_browser_window(driver):
    # Obtener el handle de la ventana de Chrome
    app = Application(backend="uia").connect(title_re=".*Chrome.*")
    window = app.top_window()
    window.minimize()

def main():
    while True:
        scrape_smn()
        time.sleep(300)  # Esperar una hora antes de volver a realizar el scraping

if __name__ == "__main__":
    main()