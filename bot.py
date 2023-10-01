from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, Updater
import logging
import json
import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('KEY_BOT_API')
username = os.getenv('KEY_BOT_USERNAME')

TOKEN: Final = key
BOT_USERNAME: Final = username

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
nb_inscrit = 0
nb_max = 48
dic_inscription = {}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Salut je suis là pour effectuer le shotgun pour les places de volley de Bordeaux INP. "
                                    "Effectue la commande /inscription pour t'inscrire au créneau.")

async def inscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global nb_inscrit
    user_id = update.message.from_user.full_name
    if nb_inscrit >= nb_max:
        nb_inscrit += 1
        dic_inscription['${nb_inscrit}'] = {'name' : user_id, 'list_attente': 'oui'} 
        jsonString = json.dumps(dic_inscription)
        jsonFile = open("data.json", "w")
        jsonFile.write(jsonString)
        jsonFile.close()
        await update.message.reply_text("Il n'y a plus de place, désolé...")
    elif user_id not in [dic_inscription[k]['name'] for k in dic_inscription]:
        nb_inscrit += 1
        dic_inscription[f'{nb_inscrit}'] = {'name' : user_id, 'liste_attente': 'non'} 
        jsonString = json.dumps(dic_inscription)
        jsonFile = open("data.json", "w")
        jsonFile.write(jsonString)
        jsonFile.close()
        await update.message.reply_text("Vous êtes inscrit !")
    else:
        await update.message.reply_text("Vous êtes déjà inscrit")

def main() -> None:
    # Créez l'application avec votre token d'API
    app = Application.builder().token(TOKEN).build()

    # Ajoutez des gestionnaires de commandes
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("inscription", inscription))

    # Démarrez l'application
    app.run_polling()

if __name__ == '__main__':
    main()
    #annuler les requtes faites en amont. et lancer àpres quelques secondes.