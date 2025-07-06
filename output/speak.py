import pyttsx3

engine = pyttsx3.init()
engine.setProperty("rate", 170)    # Speed of speech
engine.setProperty("volume", 1.0)  # Volume (0.0 to 1.0)

def respond(text):
    print(f"JARVIS (speaking): {text}")
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"[TTS Error]: {e}")
