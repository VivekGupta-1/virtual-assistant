
from PIL import Image, ImageDraw, ImageFont
import speech_recognition as sr
from gtts import gTTS
import playsound
import os
import random
import datetime
import requests
from bs4 import BeautifulSoup
from googletrans import Translator
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import pywhatkit
import wikipedia
from duckduckgo_search import ddg

# Initialize DialoGPT model
tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-small")

LANG_PREF_FILE = "language.txt"
NAME_FILE = "name.txt"

# === Voice Input ===
def listen(lang_code='en', max_attempts=3):
    r = sr.Recognizer()
    for attempt in range(max_attempts):
        with sr.Microphone() as source:
            print("Listening... (Attempt", attempt + 1, ")")
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        try:
            command = r.recognize_google(audio, language=lang_code)
            print("You said:", command)
            return command.lower()
        except sr.UnknownValueError:
            speak("I didn't catch that. Please try again.", lang_code)
        except sr.RequestError:
            speak("Speech service is not available.", lang_code)
            return "error"

    # After 3 failed attempts
    speak("Voice input failed multiple times. Please type your command.", lang_code)
    command = input("Enter your command: ")
    return command.lower()

# === Voice Output ===
def speak(text, lang='en'):
    if not text.strip():
        return
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save("response.mp3")
        playsound.playsound("response.mp3")
        os.remove("response.mp3")
    except Exception as e:
        print("Speaking error:", e)

# === Language & Name Preferences ===
def get_language_preference():
    if os.path.exists(LANG_PREF_FILE):
        with open(LANG_PREF_FILE, "r") as f:
            return f.read().strip()
    else:
        speak("Which language do you prefer? English, Hindi, French, Spanish, or German?", 'en')
        lang = listen('en')
        lang_map = {
            "english": "en", "hindi": "hi",
            "french": "fr", "spanish": "es", "german": "de"
        }
        selected = lang_map.get(lang.lower(), "en")
        with open(LANG_PREF_FILE, "w") as f:
            f.write(selected)
        return selected

def get_name():
    if os.path.exists(NAME_FILE):
        with open(NAME_FILE, "r") as f:
            return f.read().strip()
    else:
        speak("What is your name?", 'en')
        name = listen('en')
        with open(NAME_FILE, "w") as f:
            f.write(name)
        return name

# === Jokes ===
jokes_en = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "Why did the scarecrow win an award? He was outstanding in his field.",
    "I'm on a seafood diet. I see food and I eat it.",
    "Why don’t skeletons fight each other? They don’t have the guts.",
    "I told my computer I needed a break, and it said 'No problem — I’ll go to sleep.'",
    "Why was the math book sad? It had too many problems.",
    "What do you call fake spaghetti? An Impasta!",
    "I would tell you a construction joke, but I’m still working on it.",
    "Parallel lines have so much in common. It’s a shame they’ll never meet.",
    "Why can’t your nose be 12 inches long? Because then it would be a foot."
]

jokes_hi = [
    "टीचर: होमवर्क क्यों नहीं किया? छात्र: Google डाउन था!",
    "पप्पू: मम्मी, शादी कैसे होती है? मम्मी: बेटा, जैसे किसी ऐप की टर्म्स और कंडीशन्स बिना पढ़े Accept कर लेते हो!",
    "गोलू: मम्मी, मुझे भूख लगी है। मम्मी: चुप हो जा, मोबाइल चार्ज कर रही हूं!",
    "पंडित: शादी में विलंब क्यों? लड़का: अभी मोबाइल अपडेट कर रहा हूं!",
    "टीचर: बताओ पृथ्वी क्यों गोल है? छात्र: ताकि घूमने में मजा आए!",
    "पत्नी: सुनिए, मेरा जन्मदिन आ रहा है। पति: क्या चाहिए? पत्नी: प्यार। पति: वो तो 365 दिन मिलता है, कुछ और बोलो!",
    "राजू: Exam में चीटिंग करूं? दोस्त: भगवान देख रहा है! राजू: भगवान तो सबका है, टीचर सामने बैठा है!",
    "बच्चा: पापा मोबाइल दो! पापा: क्यों? बच्चा: गेम खेलनी है। पापा: ज़िंदगी ही एक गेम है बेटा!",
    "पप्पू: फेसबुक पर सब कुछ मिलता है। टीचर: पढ़ाई भी? पप्पू: नहीं, वो तो स्कूल में भी नहीं मिलती!"
]


# === Basic Replies ===
basic_responses = {
    "hello": "Hello! How can I help you?",
    "hi": "Hi there!",
    "good morning": "Good morning!",
    "good night": "Good night!",
    "how are you": "I am great!",
    "i love ": "Aww, I love talking to you too!",
    "thank ": "You’re welcome!",
    "bye": "Goodbye!"
}

# === Other Functions (Image, Search, etc.) ===

def search_image_online(query):
    try:
        with ddg() as ddgs:
            results = ddgs.images(query)
            for r in results:
                return r["image"]
        return "No image found."
    except Exception as e:
        return f"Image search error: {e}"

def generate_image_from_text(text, filename="generated_image.png"):
    img = Image.new('RGB', (600, 200), color=(73, 109, 137))
    fnt = ImageFont.load_default()
    d = ImageDraw.Draw(img)
    d.text((10, 90), text, font=fnt, fill=(255, 255, 0))
    img.save(filename)
    return filename

def get_weather(city="Delhi"):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
    geo_response = requests.get(url).json()
    if 'results' in geo_response:
        lat = geo_response['results'][0]['latitude']
        lon = geo_response['results'][0]['longitude']
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_data = requests.get(weather_url).json()
        if 'current_weather' in weather_data:
            temp = weather_data['current_weather']['temperature']
            wind = weather_data['current_weather']['windspeed']
            return f"The temperature in {city} is {temp}°C with wind speed of {wind} km/h."
    return "Sorry, couldn't fetch the weather info."


def product_search(query):
    # Format query for URL (replace spaces with +)
    formatted_query = query.replace(' ', '+')
    url = f"https://www.flipkart.com/search?q={formatted_query}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Send a request to the Flipkart search URL
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the product names and prices
        product_names = soup.find_all("a", class_="IRpwTa")
        product_prices = soup.find_all("div", class_="_30jeq3")

        # Check if results were found
        if product_names and product_prices:
            # Get the first product and its price
            first_product = product_names[0].text.strip()
            first_price = product_prices[0].text.strip()
            return f"{first_product} is priced at {first_price}"
        else:
            return "Sorry, no products found."
    except Exception as e:
        return f"An error occurred while searching: {e}"



def google_search(query):
    try:
        results = ddg(query, max_results=1)
        if results:
            return results[0].get('body') or results[0].get('snippet') or "No snippet available."
        return "No result found."
    except Exception as e:
        return f"Search error: {e}"

def chat_with_user(prompt):
    inputs = tokenizer.encode(prompt + tokenizer.eos_token, return_tensors="pt")
    reply_ids = model.generate(inputs, max_length=100, pad_token_id=tokenizer.eos_token_id)
    reply = tokenizer.decode(reply_ids[:, inputs.shape[-1]:][0], skip_special_tokens=True)
    return reply

def translate_text(text, dest_lang='hi'):
    translator = Translator()
    try:
        translated = translator.translate(text, dest=dest_lang)
        return translated.text
    except:
        return "Translation failed."

def generate_email(purpose):
    return f"Subject: Regarding {purpose}\n\nDear Sir/Madam,\n\nMy self [name] from your [organisation].\nI would like to {purpose.lower()}.\n\nThank you.\n[Your Name]"

def get_wikipedia_summary(query):
    try:
        summary = wikipedia.summary(query, sentences=2)
        return summary
    except:
        return "Sorry, no information found."

# === Main Function ===
def main():
    lang = get_language_preference()
    name = get_name()
    speak(f"Hello {name}, I am Alpha. How can I help you today?", lang)

    while True:
        command = listen(lang)

        if 'exit' in command or 'bye' in command or 'बाय' in command:
            speak("Goodbye! Have a nice day!", lang)
            break

        elif 'joke' in command or 'joke batao' in command or 'मजाक' in command:
            joke = random.choice(jokes_hi if command == 'batao' else jokes_en)
            speak(joke, lang)

        elif any(word in command for word in ["search", "google", "सर्च", "खोजो"]):
            speak("What should I search?", lang)
            query = listen(lang)
            result = google_search(query)
            speak(result, lang)

        elif any(word in command for word in ["weather", "sky", "mausam", "मौसम"]):
            speak("Please tell me the city name.", lang)
            city = listen(lang)
            weather = get_weather(city)
            speak(weather, lang)

        elif any(word in command for word in ["product", "price", "cheez", "सामान", "कीमत"]):
            speak("Tell me the product name.", lang)
            product = listen(lang)
            result = product_search(product)
            speak(result, lang)

        elif any(word in command for word in ["time", "समय", "kitna baj gaya"]):
            now = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"The time is {now}", lang)

        elif any(word in command for word in ["talk to me", "baat karo", "बात करो"]):
            speak("Sure, let's chat. Say something!", lang)
            while True:
                user_input = listen(lang)
                if 'stop' in user_input or 'bas' in user_input:
                    speak("Okay, chat closed.", lang)
                    break
                response = chat_with_user(user_input)
                speak(response, lang)

        elif "email" in command:
            speak("Tell me the purpose of the email.", lang)
            purpose = listen(lang)
            email = generate_email(purpose)
            print(email)
            speak("Email generated. Please check the screen.", lang)

        elif "wikipedia" in command:
            speak("What do you want to know?", lang)
            query = listen(lang)
            result = get_wikipedia_summary(query)
            speak(result, lang)

        elif "create image" in command or "image banao" in command or "चित्र बनाओ" in command:
            speak("What should be written on the image?", lang)
            text = listen(lang)
            filename = generate_image_from_text(text)
            speak("Image created. Please check your folder.", lang)
            print(f"Image saved as {filename}")

        elif "image" in command or "photo" in command or "तस्वीर" in command:
            speak("What image should I search?", lang)
            query = listen(lang)
            image_url = search_image_online(query)
            print("Image URL:", image_url)
            speak("Here is the image I found. Please check your screen.", lang)

        elif "translate" in command or "अनुवाद" in command:
            speak("What should I translate?", lang)
            text = listen(lang)
            speak("Which language to translate to?", lang)
            target_lang_name = listen('en')
            lang_map = {"english": "en", "hindi": "hi", "french": "fr", "spanish": "es", "german": "de"}
            dest_lang = lang_map.get(target_lang_name.lower(), 'en')
            translated = translate_text(text, dest_lang)
            speak(translated, dest_lang)

        elif "play" in command or "गाना चलाओ" in command:
            speak("Which song should I play?", lang)
            song = listen(lang)
            if song:
                speak(f"Playing {song} on YouTube", lang)
                pywhatkit.playonyt(song)

        else:
            translated_command = translate_text(command, dest_lang='en').lower()
            found = False
            for key in basic_responses:
                if key in translated_command:
                    speak(basic_responses[key], lang)
                    found = True
                    break
            if not found:
                speak("Sorry, I did not understand.", lang)

if __name__ == "__main__":
    main()
