import os
import azure.cognitiveservices.speech as speechsdk
from pydub import AudioSegment
from tkinter import Tk, filedialog

# Configurar el servicio con tu clave y región de Azure
speech_key = "04ee5dc0d04e4a1186c076ef83d58d6e"  # Reemplaza con tu clave de suscripción
service_region = "westeurope"  # Reemplaza con tu región de Azure

# Voces seleccionadas de Azure: Ximena y Álvaro
voz_personaje_1 = "es-ES-XimenaMultilingualNeural"  # Voz femenina (Ximena)
voz_personaje_2 = "es-ES-AlvaroNeural"  # Voz masculina (Álvaro)

# Función para sintetizar voz y guardar el archivo
def sintetizar_voz(texto, nombre_voz, nombre_archivo):
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.speech_synthesis_voice_name = nombre_voz  # Especificar la voz
    speech_config.speech_synthesis_voice_rate = "+15%"  # Aumentar la velocidad en un 15%
    audio_output = speechsdk.audio.AudioOutputConfig(filename=nombre_archivo)  # Guardar el archivo de salida
    
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output)
    resultado = synthesizer.speak_text_async(texto).get()
    
    if resultado.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print(f"Sintetizado con éxito: {nombre_archivo}")
    else:
        print(f"Error en la síntesis de voz: {resultado.reason}")

# Función para leer el archivo y alternar entre los personajes
def procesar_podcast(archivo_texto, ruta_guardado):
    with open(archivo_texto, 'r', encoding='utf-8') as f:
        lineas = f.readlines()

    audios = []
    contador = 1

    for linea in lineas:
        if linea.startswith('-'):
            linea = linea[1:].strip()  # Remover el guion al inicio de la línea
            
            # Dividir la línea en frases basadas en los puntos (.) para reducir las pausas entre frases
            frases = [frase.strip() for frase in linea.split('.') if frase.strip()]

            # Alternar entre las dos voces
            if contador % 2 != 0:
                voz = voz_personaje_1
            else:
                voz = voz_personaje_2
            
            for idx, frase in enumerate(frases):
                archivo_salida = f"voz_{voz}_{contador}_{idx}.wav"
                sintetizar_voz(frase + '.', voz, archivo_salida)  # Añadir el punto al final de cada frase para mantener la puntuación
                audios.append(AudioSegment.from_wav(archivo_salida))

            contador += 1

    # Combinar los audios generados con pausas cortas entre frases del mismo hablante
    podcast_final = AudioSegment.empty()
    pausa_frases = AudioSegment.silent(duration=10)  # Pausa de 0.1 segundos entre frases de un mismo hablante
    pausa_entre_personajes = AudioSegment.silent(duration=150)  # Pausa de 0.15 segundos entre diferentes hablantes

    for i, audio in enumerate(audios):
        podcast_final += audio
        # Si el siguiente audio es del mismo hablante, aplicar una pausa más corta
        if i + 1 < len(audios) and (i % 2 == 0):  # i % 2 es para alternar entre personajes
            podcast_final += pausa_frases
        else:
            podcast_final += pausa_entre_personajes

    # Guardar el archivo final en formato MP3
    podcast_final.export(ruta_guardado, format="mp3", bitrate="192k")
    print(f"Podcast final generado en: {ruta_guardado}")

# Función para abrir un cuadro de diálogo y seleccionar el archivo .txt
def seleccionar_archivo():
    root = Tk()
    root.withdraw()  # Ocultar la ventana principal de Tkinter
    archivo_texto = filedialog.askopenfilename(title="Seleccionar archivo de texto", filetypes=[("Archivos de texto", "*.txt")])
    if archivo_texto:
        print(f"Archivo seleccionado: {archivo_texto}")
        
        # Seleccionar la ubicación y nombre del archivo de salida
        ruta_guardado = filedialog.asksaveasfilename(
            title="Guardar podcast como",
            defaultextension=".mp3",
            filetypes=[("Archivo MP3", "*.mp3")]
        )
        if ruta_guardado:
            procesar_podcast(archivo_texto, ruta_guardado)
        else:
            print("No se seleccionó una ubicación para guardar el archivo.")
    else:
        print("No se seleccionó ningún archivo.")

# Ejecutar la interfaz para seleccionar archivo
seleccionar_archivo()
