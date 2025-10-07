import flet as ft
import requests
import os 
from murf import Murf
from api_key import API_KEY


#API Clients

client = Murf(api_key=API_KEY)

# voices = client.text_to_speech.get_voices()
# for voice in voices:
#     print(f"Voice ID: {voice.voice_id}, Name: {voice.display_name}Moods: {voice.available_styles}")


#Voice settings
VOICE_MOODS = {
        "Luisa" : {
            "voice_id" : "es-MX-luisa",
            "moods" : ['Conversational', 'Promo', 'Calm', 'Sad']
        },
        "Kabir" : {
            "voice_id" : "hi-IN-kabir",
            "moods" :  ['Conversational']
                 },
        "Cooper" : {
            "voice_id" : "en-US-cooper",
            "moods" : ['Conversational', 'Promo', 'Angry', 'Inspirational', 'Sad', 'Newscast'] },

    }

#Build the app 
def main(page: ft.Page):
    page.title = "AI Voice Generator"
    page.padding = 40
    page.bgcolor = "#1E1E2F"

if page.web: # This property only exists when running in a browser
        page.web.meta = {
            "viewport": "width=device-width, initial-scale=1.0",
        }



    #Create UI Widgets
    title = ft.Text("AI Voice Generator", size=42, weight=ft.FontWeight.BOLD, color="#FFD700")
    text_input = ft.TextField(
            label="Enter some text here....",
            width=350,
            bgcolor="#2A2A3B",
            color="#ffffff",
            border_radius=15,
            border_color="#FFD700"
    )

    voice_selection = ft.Dropdown(
            label="Choose Voice",
            options=[ft.dropdown.Option(voice) for voice in VOICE_MOODS.keys()],
            width=350,
            bgcolor="#2A2A3B",
            color="#ffffff",
            value="Kabir"
    )

    mood_selection = ft.Dropdown(
        label="Choose Mood",
        width=350,
        bgcolor="#2A2A3B",
        color="#ffffff"
    )
    def update_moods(e=None):
        selected_voice = voice_selection.value
        mood_selection.options = [ft.dropdown.Option(mood) for mood in VOICE_MOODS.get(selected_voice, {}).get("moods", [])
            ]
        mood_selection.value = mood_selection.options[0].text if mood_selection.options else None

        page.update()

    voice_selection.on_change = update_moods
    update_moods()

    voice_speed = ft.Slider(
         min=-30, max=30, value=0, divisions=10, label="{value}%", active_color="#FFD700"
    )



    #Generate AI Voices
    def generate_audio():
         selected_voice = voice_selection.value
         voice_id = VOICE_MOODS.get(selected_voice, {}).get("voice_id")

         if not text_input.value.strip():
              print("ERROR, you need some text...")
              return None
         try:
              response = client.text_to_speech.generate(
                   format="MP3",
                   sample_rate=48000.00,
                   channel_type="STEREO",
                   text=text_input.value,
                   voice_id=voice_id,
                   style=mood_selection.value,
                   pitch=voice_speed.value
              )
              return response.audio_file if hasattr(response, "audio_file") else None
         except Exception as e:
              print(f"Error: {e}")
              return None
         
    def save_and_play(e):
        audio_url = generate_audio()
        if not audio_url:
            print("Error: no audio found....")
            return
        try:
            response = requests.get(audio_url, stream=True)
            if response.status_code == 200:
                file_path = os.path.abspath("audio.mp3")
                with open(file_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=1024):
                            file.write(chunk)
                print("Audio saved As:", file_path)
                page.overlay.clear()
                page.overlay.append(ft.Audio(src="audio.mp3", autoplay=True))
                page.update()
            else:
                print("Failed to get Audio")
        except Exception as e:
            print("ERROR", e)
                             
              

    btn_enter = ft.ElevatedButton(
         "Generate Voice",
         bgcolor="#FFD700",
         color="#1E1E2F",
         on_click=save_and_play,
         style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=15))
    )





    #Build a UI Container

    input_container = ft.Container(
        content=ft.Column(
                controls=[title, text_input,voice_selection, mood_selection,ft.Text("Adjust Pitch", size=18, weight=ft.FontWeight.BOLD, color="#FFD700"), voice_speed, btn_enter],
                spacing=15,
                alignment=ft.MainAxisAlignment.CENTER

        ),
        padding=20,
        border_radius=20,
        bgcolor="#2A2A3B",
        shadow=ft.BoxShadow(blur_radius=12, spread_radius=2, color="#FFD700")
    )


    
    page.add(
            ft.Column(
                    controls= [title,input_container],
                    spacing=20,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
    )
    page.update()

#Run App
        
if __name__ == "__main__":
        ft.app(target=main, assets_dir=".")
