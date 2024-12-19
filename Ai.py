"""
Install the Google AI Python SDK

$ pip install google-generativeai
"""

import os
import google.generativeai as genai

#dit stuk code (het opzetten van de api) komt rechtstreeks uit de documentatie#
# zie https://ai.google.dev/gemini-api/docs
genai.configure(api_key="AIzaSyANDvi-hHTOmC-WFUzhGFin6W07Dwe7TAk")#api key
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 1400,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",#het model
  generation_config=generation_config,
)
#----------------------#
def generate_quiz(thema):
    # Start een chatsessie
    chat_session = model.start_chat()
    response = chat_session.send_message(
    f"Genereer een quiz met 20 vragen in het volgende formaat: elke vraag bestaat uit 6 regels. Regel 1 bevat de vraag, regels 2 tot en met 5 bevatten de opties, en regel 6 geeft het juiste antwoord (A, B, C of D, alleen één letter). De vragen zijn niet genummerd en bevatten geen speciale tekens of emoji’s; alleen letters, cijfers en het vraagteken mogen worden gebruikt. Zorg ervoor dat de vragen en antwoorden kort en klein mogenlijk zijn. Vermijd lege regels. Thema: {thema}"

    )
    print(response.text)

    file_path = f"{thema}.txt"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(response.text)

#----------------------#
    if validate_quiz_file(file_path):
        with open("catogory.txt", "a", encoding="utf-8") as cat_file:
            cat_file.write(f"{file_path}\n")
        return file_path
    else:
        os.remove(file_path)
        return -1
# Controleer of het bestand correct is opgesteld
def validate_quiz_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    with open(file_path, "w", encoding="utf-8") as file:
        for line in lines:
            if line.strip():
                file.write(line)
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        if len(lines) % 6 != 0:
             return False
        for i in range(0, len(lines), 6):
            if lines[i + 5].strip() not in {'A', 'B', 'C', 'D'}:
                return False
    return True