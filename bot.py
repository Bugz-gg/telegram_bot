from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, Updater
import logging
import json
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('KEY_BOT_API')
username = os.getenv('KEY_BOT_USERNAME')
id_admin1 = os.getenv('ID_ADMIN1') 
id_admin2 = os.getenv('ID_ADMIN2')
id_admin3 = os.getenv('ID_ADMIN3')
username_list = [id_admin1, id_admin2, id_admin3]
groupe_id = os.getenv('GROUPE_ID')

TOKEN: Final = key
BOT_USERNAME: Final = username

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
nb_inscrit = 0
nb_max = 10
dic_inscription = {}
oopen = False

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if pas_dans_le_groupe(update, context):
        await update.message.reply_text("Salut je suis là pour effectuer le shotgun pour les places de volley de Bordeaux INP. "
                                    "Effectue la commande /inscription pour t'inscrire au créneau.")
    else:
        await asyncio.sleep(0)


async def get_group_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #Obtenez l'ID du chat (groupe) à partir de l'objet Update
    chat_id = update.message.chat_id
    print(chat_id)
    await asyncio.sleep(0)
    # Répondez à l'utilisateur avec l'ID du groupe



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
                if nb_inscrit == nb_max:
                    await context.bot.send_message(chat_id=groupe_id, text="Le nombre maximum d'inscrit à été atteint.")
                dic_inscription[f'{nb_inscrit}'] = {'name' : user_id, 'liste_attente': False}
                jsonString = json.dumps(dic_inscription)
                jsonFile = open("data.json", "w")
                jsonFile.write(jsonString)
                jsonFile.close()
                await update.message.reply_text("Vous êtes inscrit !")
        else:
            await update.message.reply_text("Vous êtes déjà inscrit")
    else :
        await asyncio.sleep(0)

async def open_inscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global oopen
    user_id = update.message.from_user.id
    if user_id in username_list and pas_dans_le_groupe(update, context):
        oopen = True
        await update.message.reply_text(" Le Shotgun est bien ouvert !")
        await context.bot.send_message(chat_id=groupe_id, text="Chers volleyeurs de Bordeaux INP, le Shotgun pour le créneau du \
        vendredi est désormais disponible. Pour participer, il vous suffit de m'envoyer un message privé (https://t.me/VolleyBordeauxINPbot) et de taper la commande /inscription.\
        Les places sont limitées à " + f'{nb_max}' + ". Si vous n'avez pas réussi à obtenir votre place, ne vous inquiétez pas, vous pourrez réessayer la semaine prochaine !")
    else:
        await asyncio.sleep(0)

async def recup_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id in username_list and pas_dans_le_groupe(update, context):
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
        await asyncio.sleep(0)

async def get_name_waitinglist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if user_id in username_list and pas_dans_le_groupe(update, context):
        fileObject = open("data.json", "r")
        jsonContent = fileObject.read()
        if jsonContent:
            obj_python = json.loads(jsonContent)
            names = [ obj_python[k]["name"] for k in obj_python if obj_python[k]["liste_attente"]]
            await update.message.reply_text("Voici les personnes en liste d'attente :\n" + "\n".join(names))
        else :
            await update.message.reply_text(" Personne n'est inscrit ou ne liste d'attente pour l'instant")
        fileObject.close()
    else:
        await asyncio.sleep(0)


async def clear_names(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global dic_inscription, nb_inscrit
    user_id = update.message.from_user.id
    if user_id in username_list and pas_dans_le_groupe(update, context):
        jsonFile = open("data.json", "w")
        jsonFile.write("")
        jsonFile.close()
        dic_inscription, nb_inscrit = {}, 0
        await update.message.reply_text("La liste à été supprimée.")
    else:
        await asyncio.sleep(0)

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    if pas_dans_le_groupe(update, context):
        if user_id in username_list:
            help_message = "Voici la liste des commandes disponibles :\n"
            help_message += "/start - Démarre le bot et affiche un message de bienvenue.\n"
            help_message += "/inscription - Permet de s'inscrire au créneau de volley de Bordeaux INP.\n"
            help_message += "/open - Ouvre les inscriptions pour le créneau de volley.\n"
            help_message += "/getname - Affiche la liste des personnes inscrites.\n"
            help_message += "/clear - Efface la liste des personnes inscrites.\n"
            help_message += "/nb_change <nombre> - Modifie le nombre maximum d'inscrits.\n"
            help_message += "/liste_attente pour avoir la liste d'attente."
            #help_message += "/i_need_more_bullets - Affiche un GIF marrant.\n"
            await update.message.reply_text(help_message)
        else:
            help_message = "Voici la liste des commandes disponibles :\n"
            help_message += "/start - Démarre le bot et affiche un message de bienvenue.\n"
            help_message += "/inscription - Permet de s'inscrire au créneau de volley de Bordeaux INP.\n"
            await update.message.reply_text(help_message)
    else:
        await asyncio.sleep(0)

async def change_nb_personne(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global nb_max
    user_id = update.message.from_user.id
    if user_id in username_list and pas_dans_le_groupe(update, context):
        try:
            nb_max = int(context.args[0])
            await update.message.reply_text("Le nouveau nombre maximum d inscrit: "+str(nb_max))
        except (IndexError, ValueError):
            await update.message.reply_text('Incorrect use.')
    else:
        await asyncio.sleep(0)

def pas_dans_le_groupe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    chat_id = update.message.chat_id
    if chat_id == int(groupe_id):
        return False
    else:
        return True
    


def main() -> None:
    # Créez l'application avec votre token d'API
    app = Application.builder().token(TOKEN).build()

    # Ajoutez des gestionnaires de commandes
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("inscription", inscription))
    app.add_handler(CommandHandler("open", open_inscription))
    app.add_handler(CommandHandler("getname", recup_name))
    app.add_handler(CommandHandler("clear", clear_names))
    app.add_handler(CommandHandler("nb_change", change_nb_personne))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("tst", get_group_id))
    app.add_handler(CommandHandler("liste_attente" ,get_name_waitinglist))





    # Démarrez l'application
    app.run_polling()

if __name__ == '__main__':
    main()


#  close and clear.