import speech_recognition as sr # type: ignore
from deep_translator import GoogleTranslator # type: ignore

def get_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("[Listening for command...]")
        audio = recognizer.listen(source)

    try:
        # Use Google's speech recognition which auto-detects language and accent
        raw_text = recognizer.recognize_google(audio)
        print(f"[Raw Recognized]: {raw_text}")

        # Translate to English if needed
        translated_text = GoogleTranslator(source='auto', target='en').translate(raw_text)
        print(f"[Translated to English]: {translated_text}")
        return translated_text

    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        return f"API Error: {e}"
    except Exception as e:
        return f"Error: {e}"
