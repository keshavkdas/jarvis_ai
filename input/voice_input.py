import speech_recognition as sr # type: ignore

recognizer = sr.Recognizer()

GREETINGS = [
    "hey jarvis", "hello jarvis", "hi jarvis", "yo jarvis", "ok jarvis",
    "hey", "hi", "hello", "yo", "ok"
]

def listen_for_wake_word():
    try:
        with sr.Microphone() as source:
            print("[INFO] Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=0.2)
            print("[INFO] Listening for wake word...")
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=2)

        print(f"[DEBUG] Captured audio: {len(audio.frame_data)} bytes")

        try:
            command = recognizer.recognize_google(audio).lower().strip()
            print(f"[Heard]: {command}")
            return any(greet in command for greet in GREETINGS)
        except sr.UnknownValueError:
            print("[WARN] Could not understand audio.")
            return False
        except sr.RequestError as e:
            print(f"[ERROR] Speech API error: {e}")
            return False

    except sr.WaitTimeoutError:
        print("[WARN] Timeout: No speech detected.")
        return False
