import urllib
import requests
import random
import time

username = "memestation"
passwd = "Memestation136!"

user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"


def generate_meme(username, passwd, user_agent, premise1, premise2, images, id):
        
    #id = random.choice(range(len(images)))

    #Fetch the generated meme
    URL = 'https://api.imgflip.com/caption_image'
    params = {
        'username':username,
        'password':passwd,
        'template_id':images[id-1]['id'],
        'text0':premise1,
        'text1':premise2
    }
    response = requests.request('POST', URL, params=params).json()
    print(response)

    #Save the meme
    opener = urllib.request.URLopener()
    opener.addheader('User-Agent', user_agent)
    fname = str(int(time.time()))
    filename, headers = opener.retrieve(response['data']['url'], "temp/meme-" + fname +'.jpg')
    return filename
    
    
#generate_meme(username, passwd, user_agent, "BMW", "Audi")