import os
import time
from groq import Groq
from gtts import gTTS

# ----------------- Hardcoded API Key -----------------
api_key = "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"  # <-- put your real key here
groq_client = Groq(api_key=api_key)

# ----------------- Audio Transcription -----------------
def transcribe_audio(filepath ):
    with open(filepath, "rb") as f:
        response = groq_client.audio.transcriptions.create(
            model="whisper-large-plant_disease_model.pthv3-turbo",
            file=f,
        )
    return response.text

# ----------------- Question Answering -----------------
def get_answer(question):
    try:
        # Primary model
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a helpful agriculture chatbot for Indian farmers."},
                {"role": "user", "content": "Give a Brief Of Agriculture Seasons in India"},
                {"role": "system", "content": "In India, the agricultural season consists of three major seasons: the Kharif (monsoon), the Rabi (winter), and the Zaid (summer)."},
                {"role": "user", "content": question}
            ]
        )
    except Exception:
        # Fallback model
        print("⚠️ Primary model failed, falling back to llama-3.1-8b-instant...")
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful agriculture chatbot for Indian farmers."},
                {"role": "user", "content": "Give a Brief Of Agriculture Seasons in India"},
                {"role": "system", "content": "In India, the agricultural season consists of three major seasons: the Kharif (monsoon), the Rabi (winter), and the Zaid (summer)."},
                {"role": "user", "content": question}
            ]
        )
    return response.choices[0].message.content

# ----------------- Typing Effect -----------------
def typing_effect(text, delay=0.03):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()  # newline at end

# ----------------- Text to Speech -----------------
def text_to_speech(text, filename):
    tts = gTTS(text)
    output_path = f"{filename}.mp3"
    tts.save(output_path)
    return output_path

# ----------------- Main Program -------------------
def main():
    mode = input("Choose input type ('text' or 'audio'): ").strip().lower()

    if mode == 'text':
        question = input("Enter your question: ").strip()

    elif mode == 'audio':
        filepath = input("Enter the path to your audio file: ").strip()
        if not os.path.exists(filepath):
            print("❌ File not found.")
            return
        print("🎤 Transcribing audio...")
        question = transcribe_audio(filepath)
        print(f"📝 Transcribed Text: {question}")

    else:
        print("❌ Invalid input type. Use 'text' or 'audio'.")
        return

    print("🤖 Getting response from LLM...")
    answer = get_answer(question)

    print("\n✅ Answer:")
    typing_effect(answer)

    print("\n🔊 Converting answer to speech...")
    audio_file = text_to_speech(answer, "response_audio")
    print(f"🎧 Voice saved to: {audio_file}")

# ----------------- Run Program -----------------
if __name__ == "__main__":
    main()
