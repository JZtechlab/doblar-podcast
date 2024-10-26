import whisper
import os
import librosa
import soundfile as sf
import noisereduce as nr
from tkinter import Tk, filedialog

# Crear una interfaz para seleccionar el archivo MP3 o WAV
root = Tk()
root.withdraw()  # Ocultar la ventana principal
root.attributes('-topmost', True)  # Asegurarse de que la ventana de diálogo esté en primer plano

# Función para reducir el ruido del audio
def reducir_ruido(audio_data, sr):
    return nr.reduce_noise(y=audio_data, sr=sr)

# Función para transcribir el archivo de audio usando Whisper por bloques
def transcribir_audio_por_bloques(audio_file, bloque_duracion=60, sr=16000):
    try:
        # Cargar el modelo Whisper (medium o large para más precisión)
        model = whisper.load_model("medium")  # Cambiar a "large" si prefieres más precisión

        # Cargar el audio y reducir la tasa de muestreo a 16kHz
        y, sr = librosa.load(audio_file, sr=sr)

        # Reducir el ruido del audio antes de la transcripción
        y = reducir_ruido(y, sr)

        duracion_total = librosa.get_duration(y=y, sr=sr)

        transcripcion_completa = ""
        for inicio in range(0, int(duracion_total), bloque_duracion):
            fin = min(inicio + bloque_duracion, duracion_total)
            bloque_audio = y[int(inicio*sr):int(fin*sr)]

            # Transcribir este bloque usando Whisper
            print(f"Transcribiendo bloque de {inicio} a {fin} segundos...")
            temp_file = f"temp_block_{inicio}_{fin}.wav"
            
            # Guardar el bloque de audio temporalmente usando soundfile
            sf.write(temp_file, bloque_audio, sr)
            
            # Transcribir el bloque con precisión
            result = model.transcribe(temp_file, fp16=False, word_timestamps=True, verbose=True)

            # Añadir la transcripción al texto completo
            transcripcion_completa += result['text'].strip() + "\n"
            
            # Borrar el archivo temporal
            os.remove(temp_file)

        return transcripcion_completa
    except Exception as e:
        print(f"Error durante la transcripción: {e}")
        return None

# Función para guardar la transcripción en un archivo de texto
def guardar_transcripcion_en_texto(transcripcion):
    try:
        nombre_archivo_texto = filedialog.asksaveasfilename(
            title="Guardar transcripción como",
            defaultextension=".txt",
            filetypes=[("Archivo de texto", "*.txt")]
        )
        
        if nombre_archivo_texto:
            with open(nombre_archivo_texto, "w", encoding="utf-8") as file:
                file.write("Transcripción del podcast:\n\n")
                file.write(transcripcion)
                print(f"Transcripción guardada en: {os.path.abspath(nombre_archivo_texto)}")
        else:
            print("No se seleccionó una ubicación para guardar el archivo.")
    except Exception as e:
        print(f"Error al guardar la transcripción en un archivo de texto: {e}")

# Función para ejecutar todo el flujo
def procesar_podcast(audio_file):
    # Transcribir el podcast en bloques
    print("Transcribiendo el podcast por bloques...")
    transcripcion = transcribir_audio_por_bloques(audio_file)
    if transcripcion is None:
        print("Error en la transcripción. Proceso detenido.")
        return
    print("Transcripción completada.")

    # Guardar la transcripción en un archivo de texto
    guardar_transcripcion_en_texto(transcripcion)

# Función principal para procesar el archivo
def main():
    archivo_audio = filedialog.askopenfilename(
        title="Selecciona el archivo de audio del podcast", 
        filetypes=[("Archivos de audio", "*.mp3 *.wav")]
    )
    
    if not os.path.isfile(archivo_audio):
        print(f"El archivo '{archivo_audio}' no se encuentra.")
    else:
        procesar_podcast(archivo_audio)

if __name__ == "__main__":
    main()
