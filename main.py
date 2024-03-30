import os
import jlrpy
import requests
import webbrowser
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from mis_utilidades import read_credentials_from_file
from mis_utilidades import obtener_archivo_con_siguiente_indice_mas_alto
from mis_utilidades import obtener_archivo_con_indice_mas_alto
from kivy.uix.label import Label
from kivy.animation import Animation

class JaguarLocateApp(App):

    def build(self):
    
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Configurar el icono de la aplicación
        self.icon = 'logo_jaguar.png'

        # Etiqueta para mostrar el mensaje
        self.message_label = Label(text="Ultima localización registrada", size_hint=(1, 0.05), color=(1, 1, 0, 1))

        nombre_archivo = obtener_archivo_con_indice_mas_alto('imagenes/mapa_google_*.png')

        print(nombre_archivo)
        
        # Esto nos muestra el ultimo archivo generado antes de pulsar el botón
        self.map_image = Image(source=nombre_archivo, size_hint=(1, 0.8))

        get_location_button = Button(text='Obtener Localización', size_hint=(1, 0.05))
        get_location_button.bind(on_release=self.obtener_localizacion)
        
        open_maps_button = Button(text='Abrir Google Maps', size_hint=(1, 0.05))
        open_maps_button.bind(on_release=self.abrir_google_maps)

        # Etiqueta para mostrar el nombre de la calle
        self.street_label = Label(text="", size_hint=(1, 0.05), color=(1, 1, 1, 1))

        
        self.layout.add_widget(self.message_label)
        self.layout.add_widget(self.map_image)
        self.layout.add_widget(get_location_button)
        self.layout.add_widget(open_maps_button)

        return self.layout

    def obtener_localizacion(self, instance):
        
        config_file = "config.txt"
        credentials = read_credentials_from_file(config_file)
        username, password = credentials
        
        c = jlrpy.Connection(username, password)
        v = c.vehicles[0]
        
        # Get current position of vehicle
        p = v.get_position()

        latitud = p['position']['latitude']
        print (latitud)
        longitud = p['position']['longitude']
        print (longitud)
        #google_maps_api_key = "TU_CLAVE_DE_API_DE_GOOGLE_MAPS"
        #google_maps_api_key = "AIzaSyB4AanJWCDlytWn27ukUY2nneTxYxiSO5U"
        google_maps_api_key = "AIzaSyCuJqI2_YaahxbwgVRclX3jzveePKB_Ey4"

        # Obtener el nombre de la calle utilizando el servicio de geocodificación de Google Maps
        #api_key_geocoding = "AIzaSyB4AanJWCDlytWn27ukUY2nneTxYxiSO5U"
        api_key_geocoding = "AIzaSyCuJqI2_YaahxbwgVRclX3jzveePKB_Ey4"
        geocoding_url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitud},{longitud}&key={api_key_geocoding}"
        print (geocoding_url)
        
        try:
            response_geocoding = requests.get(geocoding_url)
            data_geocoding = response_geocoding.json()

            if response_geocoding.status_code == 200 and data_geocoding['status'] == 'OK':
                street_name = data_geocoding['results'][0]['formatted_address']
                
                print("La Calle es:",street_name)
                
                self.street_label.text = f"Calle: {street_name}"

            else:
                print("No se pudo obtener la información de geocodificación.")

        except Exception as e:
            
            print(f"Error al obtener información de geocodificación: {e}")


        self.obtener_imagen_mapa(latitud, longitud, google_maps_api_key)


        # Cambiar el texto de la etiqueta después de obtener la localización
        self.message_label.text = "Localización actualizada"
        # Cambiar el color de la etiqueta a rojo con animación
        Animation(color=(1, 0, 0, 1), duration=1).start(self.message_label)




    def abrir_google_maps(self, instance):

        config_file = "config.txt"
        credentials = read_credentials_from_file(config_file)
        username, password = credentials
        
        c = jlrpy.Connection(username, password)
        v = c.vehicles[0]
        p = v.get_position()
        latitud = p['position']['latitude']
        longitud = p['position']['longitude']

        webbrowser.open(f"https://www.google.com/maps/search/?api=1&query={latitud},{longitud}")





    def obtener_imagen_mapa(self, latitud, longitud, api_key):

        url_base = "https://maps.googleapis.com/maps/api/staticmap"
        params = {
            "center": f"{latitud},{longitud}",
            "zoom": 18,
            "size": "400x400",
            "maptype": "roadmap",
            "markers": f"{latitud},{longitud}",
            "key": api_key,
            "key": "AIzaSyB4AanJWCDlytWn27ukUY2nneTxYxiSO5U",  # Tu clave de API de Google Maps
            "key": "AIzaSyCuJqI2_YaahxbwgVRclX3jzveePKB_Ey4",
        }
        response = requests.get(url_base, params=params)

        nombre_archivo_1 = obtener_archivo_con_siguiente_indice_mas_alto('imagenes/mapa_google_*.png')
        #print("Nombre de archivo siguiente al mas alto: ", nombre_archivo_1) 

        if response.status_code == 200:
            with open(nombre_archivo_1, "wb") as f:
                f.write(response.content)
            self.map_image.source = nombre_archivo_1  # Actualiza la propiedad source de la instancia existente

            print(f"Imagen de la localización del coche guardada como '{nombre_archivo_1}'")
        else:
            print(f"Error al obtener la localización del coche. Código de estado: {response.status_code}")
    

if __name__ == '__main__':
    # Verificar si el directorio "imagenes" existe y, si no, crearlo
    if not os.path.exists('imagenes'):
        os.makedirs('imagenes')
    JaguarLocateApp().run()
