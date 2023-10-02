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
username_list = [5308836087, 5555288592, 5120539792]

TOKEN: Final = key
BOT_USERNAME: Final = username

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
nb_inscrit = 0
nb_max = 1
dic_inscription = {}
oopen = False

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Salut je suis là pour effectuer le shotgun pour les places de volley de Bordeaux INP. "
                                    "Effectue la commande /inscription pour t'inscrire au créneau.")

async def inscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global nb_inscrit
    global oopen
    user_id = update.message.from_user.full_name
    if oopen: 
        if user_id not in [dic_inscription[k]['name'] for k in dic_inscription]:
            if nb_inscrit >= nb_max:
                nb_inscrit += 1
                dic_inscription[f'{nb_inscrit}'] = {'name' : user_id, 'liste_attente': True} 
                jsonString = json.dumps(dic_inscription)
                jsonFile = open("data.json", "w")
                jsonFile.write(jsonString)
                jsonFile.close()
                await update.message.reply_text("Il n'y a plus de place, désolé... vous êtes " + f'{nb_inscrit - nb_max}' + " sur la liste d'attente")
            else:
                nb_inscrit += 1
                dic_inscription[f'{nb_inscrit}'] = {'name' : user_id, 'liste_attente': False} 
                jsonString = json.dumps(dic_inscription)
                jsonFile = open("data.json", "w")
                jsonFile.write(jsonString)
                jsonFile.close()
                await update.message.reply_text("Vous êtes inscrit !")
        else:
            await update.message.reply_text("Vous êtes déjà inscrit")
    else :
        await update.message.reply_text(" L'inscription n'est pas ouverte.")

async def open_inscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global oopen 
    user_id = update.message.from_user.id
    if user_id in username_list:
        oopen = True
        await update.message.reply_text(" Le Shotgun est bien ouvert !")
    else:
        await update.message.reply_text(" Vous n'avez pas les droits.")

async def recup_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id in username_list:
        fileObject = open("data.json", "r")    
        jsonContent = fileObject.read()
        if jsonContent:
            obj_python = json.loads(jsonContent)
            names = [ obj_python[k]["name"] for k in obj_python if not obj_python[k]["liste_attente"]]
            await update.message.reply_text("Voici les inscrits :\n" + "\n".join(names))
        else :
            await update.message.reply_text(" Personne n'est inscrit pour l'instant")
        fileObject.close()
    else:
        await update.message.reply_text(" Vous n'avez pas les droits.")

async def clear_names(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global dic_inscription, nb_inscrit
    user_id = update.message.from_user.id
    if user_id in username_list:
        jsonFile = open("data.json", "w")
        jsonFile.write("")
        jsonFile.close()
        dic_inscription, nb_inscrit = {}, 0 
        await update.message.reply_text("La liste à été supprimer.")
    else:
        await update.message.reply_text(" Vous n'avez pas les droits.")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id in username_list:
        help_message = "Voici la liste des commandes disponibles :\n"
        help_message += "/start - Démarre le bot et affiche un message de bienvenue.\n"
        help_message += "/inscription - Permet de s'inscrire au créneau de volley de Bordeaux INP.\n"
        help_message += "/open - Ouvre les inscriptions pour le créneau de volley.\n"
        help_message += "/getname - Affiche la liste des personnes inscrites.\n"
        help_message += "/clear - Efface la liste des personnes inscrites.\n"
        help_message += "/nb_change <nombre> - Modifie le nombre maximum d'inscrits.\n"
        #help_message += "/i_need_more_bullets - Affiche un GIF marrant.\n"
        await update.message.reply_text(help_message)
    else: 
        help_message = "Voici la liste des commandes disponibles :\n"
        help_message += "/start - Démarre le bot et affiche un message de bienvenue.\n"
        help_message += "/inscription - Permet de s'inscrire au créneau de volley de Bordeaux INP.\n"
        await update.message.reply_text(help_message)
    

async def i_need_more_bullets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        #await update.message.reply_animation('https://tenor.com/view/i-need-more-bullets-gif-6493979152995335147')
        await update.message.reply_text(update.message.from_user.id)

async def change_nb_personne(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global nb_max
    user_id = update.message.from_user.id
    if user_id in username_list:
        try:
            nb_max = int(context.args[0])
            await update.message.reply_text("Le nouveau nombre maximum d inscrit: "+str(nb_max))
        except (IndexError, ValueError):
            await update.message.reply_text('Incorrect use.')
    else:
        await update.message.reply_text("Vous n'avez pas les droits.")


def main() -> None:
    # Créez l'application avec votre token d'API
    app = Application.builder().token(TOKEN).build()

    # Ajoutez des gestionnaires de commandes
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("inscription", inscription))
    app.add_handler(CommandHandler("open", open_inscription))
    app.add_handler(CommandHandler("getname", recup_name))
    app.add_handler(CommandHandler("clear", clear_names))
    app.add_handler(CommandHandler("get_id", i_need_more_bullets))
    app.add_handler(CommandHandler("nb_change", change_nb_personne))
    app.add_handler(CommandHandler("help", help))





    # Démarrez l'application
    app.run_polling()

if __name__ == '__main__':
    main()


#  close and clear.