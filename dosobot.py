import os
import pickle
import numpy as np

import telebot
import openai

from meme_generator import*
from images_embeddings import*
from prompts import*

gpt_key = os.getenv("OPENAI_KEY")
openai.api_key = gpt_key

bot_token = os.getenv("BOT_KEY")
bot = telebot.TeleBot(bot_token)    


#Fetch the available memes
def load_resource(filename):
    return pickle.load(open(filename, 'rb'))

images = load_resource("meme_images.pkl")
image_dict = load_resource("meme_embeddings.pkl")

def get_similar_meme_id(prompt, image_dict):
    embedding = get_embedding(prompt)
    id = 0
    maxi = 0
    for key in image_dict.keys():
        meme = image_dict[key]["embedding"]
        sim = np.dot(meme, embedding) / (np.linalg.norm(meme) * np.linalg.norm(embedding))
        if sim > maxi:
            maxi = sim
            id = key
    return id

def gpt_response(msg):
    resp = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [
            {"role":"system", "content":CHAT_BEHAVIOR_PROMPT},
            {"role":"user", "content":msg}
        ],
        max_tokens = 200
        )
    usage = resp["usage"]
    cost = usage["total_tokens"]
    print("This message costed: {}$".format((0.002/1000) * cost))
    text = resp['choices'][0]['message']['content']
    return text

def premise_generator(msg, meme):
    user_premise = "The premise for a meme is the following: " + msg + " \n The meme for the caption has the following title: " + meme
    
    resp = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [
            {"role":"system", "content":PREMISE_BEGIN_PROMPT},
            {"role":"user", "content":user_premise}
        ],
        max_tokens = 30,
        temperature = 0.7
        )
    usage = resp["usage"]
    cost1 = usage["total_tokens"]
    print("This message costed: {}$".format((0.002/1000) * cost1))
    premise1 = resp['choices'][0]['message']['content']
    
    resp = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [
            {"role":"system", "content":PREMISE_END_PROMPT.format(premise1)},
            {"role":"assistant", "content":premise1},
            {"role":"user", "content":user_premise}
        ],
        max_tokens = 30,
        temperature = 0.7
        )
    usage = resp["usage"]
    cost2 = usage["total_tokens"]
    premise2 = resp['choices'][0]['message']['content']
    
    print("This message costed: {}$".format((0.002/1000) * (cost1 + cost2)))
    return premise1, premise2
    

@bot.message_handler(commands=["start", "hello"])
def send_welcome(msg):
    bot.reply_to(msg, "Hola!")

@bot.message_handler(commands=["chat"])
def begin_chat(msg):
    text = "Tell me what is bothering you. Write /end when you want to finish the conversation."
    sent_msg = bot.send_message(msg.chat.id, text, parse_mode='Markdown')
    bot.register_next_step_handler(sent_msg, bot_response)
    
def bot_response(msg):
    #text = "Naspa vericu. Dar sa stii ca nu e arma ca agheu si masina ca bemveu."
    text = gpt_response(msg.text)
    sent_msg = bot.reply_to(msg, text, parse_mode='Markdown')
    if msg.text != "/end":
        bot.register_next_step_handler(sent_msg, bot_response)
    else:
        return
 
@bot.message_handler(commands=["meme"])    
def create_meme(msg):
    print("Meme requested...")
    premise = msg.text
    print("Looking for an image to make a meme...")
    #id = get_similar_meme_id(premise, image_dict)
    id = random.choice(list(image_dict.keys()))
    p1, p2 = premise_generator(premise, image_dict[id]["meme"])
    print("Got the premise...")
    filename = generate_meme(username, passwd, user_agent, p1, p2, images, id)
    #print(filename)
    print("Meme generated...")
    bot.send_photo(msg.chat.id, photo=open(filename, 'rb'))
    os.remove(filename)

try:
    print("Bot running...")
    bot.infinity_polling()
except:
    print("Bot stopped")

#p1, p2 = premise_generator("A normal day for a BMW driver")
#print(p1)
#print(p2)

#print(get_similar_meme_id("BMW meme", image_dict))