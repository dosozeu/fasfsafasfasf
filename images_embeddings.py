import openai
import urllib
import requests
import pickle
import os


gpt_key = os.getenv("OPENAI_KEY")
openai.api_key = gpt_key


def load_meme_images():
    image_dict = {}

    data = requests.get('https://api.imgflip.com/get_memes').json()['data']['memes']
    images = [{'name':image['name'],'url':image['url'],'id':image['id'],'count':image['box_count']} for image in data]
    #List all the memes
    #print('Here is the list of available memes : \n')
    ctr = 0
    for img in images:
        #print(ctr,img['name'])
        if img["count"] == 2:
            image_dict[ctr] = {
                "meme":img['name'],
                "embedding":None
            }
        ctr = ctr+1
    
    return images, image_dict
#print("There are {} meme templates".format(len(images)))


def get_embedding(text, model="text-embedding-ada-002"):
   text = text.replace("\n", " ")
   return openai.Embedding.create(input = [text], model=model)['data'][0]['embedding']

def create_embeddings(images, image_dict):
    for key in image_dict.keys():
        image_dict[key]["embedding"] = get_embedding(image_dict[key]["meme"])
    pickle.dump(image_dict, open("meme_embeddings.pkl", 'wb'))
    pickle.dump(images, open("meme_images.pkl", 'wb'))
    
#images, image_dict = load_meme_images()
#create_embeddings(images, image_dict)