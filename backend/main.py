from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, status
from typing import List, Optional
from datetime import datetime, timedelta
import os
import time
import uuid
import google.generativeai as genai

from fastapi.middleware.cors import CORSMiddleware
# Load environment variables
app = FastAPI(title="rne")
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

#my functions

#the step 1 of validation === check for sympboles illegal and numbers
import string

def verify_symboles(name:str):
    """
    verifies if the name has symboles or is all numbers
    if retyrn true then pass jaweb berhi else refue straight up
    """
    if name.isdigit():
        return False,[]  # all numbers
    for char in name:#jhfd@
        if not (char.isalnum() or char in [' ', '&']):
            return False,[char]  # unwanted symbol
    return True,[]


def verify_cursing_named_entity(name:str):
    """
    takes as input the function and verifies it doesnt contain cuss words or named entities
    reutrn false if cant pass
    """
    name = name.lower()
    for word in nonowords:
        if word in name:
            return False
    return True
prompt_template_type = (
    "Vous êtes un assistant juridique utile chargé d'aider l'utilisateur à choisir un nom conforme à son statut juridique.\n\n"
    "Selon les règles suivantes :\n"
    "- Si la société est une succursale d’une entreprise étrangère, le nom doit inclure « فرع تونس » (en arabe) ou « division de Tunisie » (en français). "
    "Veuillez proposer des corrections si ce critère n’est pas respecté.\n"
    
    "- Si la société est une société en nom collectif, le nom doit inclure « و شركاهم » (en arabe) ou « et partenaires » (en français). "
    "Veuillez suggérer des versions conformes si ce critère n’est pas respecté.\n\n"
    "Le type de société indiqué par l’utilisateur est : {input_type}.\n\n"
    "Si l’utilisateur ne connaît pas son type de société, expliquez-lui ceci :\n"
    "    * SARL (Société à Responsabilité Limitée) : Société à responsabilité limitée, adaptée aux petites et moyennes entreprises. "
    "La responsabilité des associés est limitée à leurs apports.\n"
    "    * SA (Société Anonyme) : Société anonyme, généralement destinée aux grandes entreprises. Les actions sont librement négociables.\n"
    "    * SUARL (Société Unipersonnelle à Responsabilité Limitée) : Variante de la SARL avec un seul associé.\n"
    "    * Société en nom collectif : Société où tous les associés ont une responsabilité illimitée envers les dettes de l’entreprise.\n\n"
    "ne demander pas l'utilisatuer de vous donner son non"
)

prompt_template_impact = (
    "Vous êtes un assistant juridique tunisien. Votre tâche est d’évaluer si le nom d’une entreprise est clair et conforme aux exigences du Registre National des Entreprises (RNE) en Tunisie.\n\n"
    "- Nom proposé : {company_name}\n"
    "- Activité principale : {input_type}\n\n"
    "Répondez de manière simple et concise. Évaluez si le nom est :\n"
    "* Trop vague\n"
    "* Trompeur\n"
    "* Inapproprié à l'activité\n\n"
    "Ensuite, proposez 3 à 5 suggestions de noms plus adaptés, sous forme de points clairs. Les noms doivent :\n"
    "- Refléter clairement l’activité\n"
    "- Être en langue française ou arabe\n"
    "- Être conformes aux normes tunisiennes (pas de termes trompeurs ou génériques non justifiés)\n\n"
    "Format attendu :\n"
    "1. Évaluation rapide (1 phrase max)\n"
    "2. Suggestions sous forme de puces"
)

genai.configure(api_key="AIzaSyC6yHwqS0J-5SZP7SNMoBxxfrGjK8a-5rk")
MODEL_NAME = "gemini-2.0-flash"



async def get_response(prompt_company_type, input_user="", loop_length=2, company_name=""):
    """
    send prompt to the model according to each context we are in

    """
    #client = genai.Client(api_key="AIzaSyC6yHwqS0J-5SZP7SNMoBxxfrGjK8a-5rk")
    model = genai.GenerativeModel(MODEL_NAME)
    prompt_filled = prompt_company_type.format(input_type=input_user, company_name=company_name)
    chat = model.start_chat()
    response = await chat.send_message_async(prompt_filled)
    return response.text
    #response = client.models.generate_content(
     #   model="gemini-2.0-flash",
      #  contents=prompt_filled, )
    #return response.text


from pydantic import BaseModel

nonowords = [
    # 🇫🇷 French – Light Cursing & Bad Language
    "con", "connard", "conne", "merde", "putain", "chiant", "salope",
    "enculé", "bordel", "débile", "abruti", "crétin", "naze", "gros con",

    # 🇫🇷 French – Institutional or Misleading
    "ministère", "institut", "université", "école", "lycée",
    "universite", "ecole", "lycee", "police", "armée", "république",
    "banque centrale", "présidence", "ambassade", "justice",
    "gouvernement", "sécurité", "douane", "cnrs", "caf", "cpam",

    # 🇫🇷 French – Drugs & Slang
    "shit", "beuh", "cannabis", "weed", "drogue", "drogues",
    "coke", "cocaïne", "héroïne", "lsd", "ecstasy", "mdma",
    "joint", "pétard", "pilule", "psychotrope", "trip", "stoné", "défoncé",

    # 🇸🇦 Arabic – Light Cursing
    "كلب", "حمار", "تافه", "غبي", "قذر", "وسخ", "مجنون", "ابله",
    "لعنة", "سافل", "وقح", "زبالة", "حقير",

    # 🇸🇦 Arabic – Institutional or Misleading
    "الشرطة", "الجيش", "الوزارة", "الحكومة", "المعهد", "الجامعة",
    "المدرسة", "رئاسة", "السفارة", "القنصلية", "وزارة الداخلية",
    "وزارة الخارجية", "البنك المركزي", "العدالة", "الجمارك",
    "الضمان الاجتماعي", "الديوان",

    # 🇸🇦 Arabic – Drugs & Slang
    "مخدرات", "حشيش", "بانغو", "ماريجوانا", "كوكاين", "هيروين",
    "إكستاسي", "حبوب", "دواء نفسي", "مدمن", "متعاطي", "مكيف", "سُكران", "نشوان"
]


def main_conversation_flow2():
    conversation_history = []
    # flow step one verify rules according to type
    company_type = get_user_input(
        "\nWhat type of company are you planning to create? (SARL, SA, SUARL, société en nom collectif), or are you a division of a foreign international company? If you're unsure, type 'help'.")
    get_response(prompt_template_type, company_type)
    # flow step 2 verify name is not too vague according to context of acitvity
    activity_type = get_user_input("\n Can you now tell me more details about your activity?")
    # print(activity_type,type(activity_type))
    get_response(
        prompt_company_type=prompt_template_impact,
        input_user=activity_type,
        company_name="vetement du noor"
    )


class company_type(BaseModel):
    name: str
@app.post("/verify-namestage1")
async def verify_name(input: company_type):
    listt=[]
    is_valid,listt = verify_symboles(input.name)
    if is_valid :
        text= "Le nom que vous avez choisie est  valide : Il n'ya pas des characteres speciaux"
        passs=True
    else:
        text=f"Le nom que vous avez choisie n'est pas valide : Choisir un nom sans{listt[0]} "
        passs = False

    return {"text": text,"pass":passs}


class company_type(BaseModel):
    name: str
@app.post("/verify-namestage2")
async def verify_name(input: company_type):

    is_valid = verify_cursing_named_entity(input.name)
    if is_valid:
        text=" Le mot est valide et ne comporte aucun mots interdites}"
    else:
        text="Ce nom n'est pas permis ,il va etre rejete car il contient des mots interdites"

    return {"text": text}
class company_type(BaseModel):
    name: str
@app.post("/verify-namestage3.1")
async def verify_name(input: company_type):

    text= await get_response(prompt_template_type, input_user=input.name)

    return {"text": text}




#my routes
@app.get("/home")
async def health_check():
    """API health check endpoint."""
    return "home homeee"

@app.get("/")
async def health_check():
    """API health check endpoint."""
    return "home"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
