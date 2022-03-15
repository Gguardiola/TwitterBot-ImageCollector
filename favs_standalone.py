from codecs import utf_16_be_encode
from encodings import utf_8
from fileinput import filename
from xml.etree.ElementInclude import include
import tweepy
import glob
import random
import os
import schedule
from schedule import every, repeat, run_pending
import time
import configparser
import sys
import wget
import re


config = configparser.ConfigParser()
try:
    config.read('config.ini')
except FileNotFoundError:
    "ERROR: CONFIG NO ENCONTRADO"
    sys.exit()

api_key = config.get('auth', 'api_key')
api_secret = config.get('auth', 'api_secret')
oauth_token  = config.get('auth', 'oauth_token')
oauth_token_secret = config.get('auth', 'oauth_token_secret')

log = config.get("files","log")
favlog = config.get("files","favlog")
joseo_favs_dir = config.get("files","joseo_favs_dir")
joseo_favs_txt = config.get("files","joseo_favs_txt")
joseo_manual_dir = config.get("files","joseo_manual_dir")


auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(oauth_token, oauth_token_secret)
api = tweepy.API(auth)



def favs(max):
    f = open(file=joseo_favs_txt,mode="a+",encoding="utf-8")
    f.truncate(0)
    for favorite in tweepy.Cursor(api.get_favorites).items(max):##selecciona los X ultimos favs 
        
        stat = api.get_status(favorite.id,tweet_mode="extended") 
        ##EN CASO DE TENER VIDEO: guarda el url del video
        vidcheck = False
        try:
            vidurl = stat.extended_entities["media"][0]["video_info"]["variants"][1]["url"]
            if "container=fmp4" in vidurl:
                print("ERROR EN ENLACE, SKIP TUIT")
                continue
            else:    
                vidcheck = True
        except:
            pass
        
        stat = str(stat.full_text);stat = stat.split("https://t.co/");stat = stat[0]##elimina el enlace de imagen malo

        ##quitamos las mentions
        mentions = re.findall("@([a-zA-Z0-9_]{1,50})", stat)
        for i in mentions:
            stat = stat.replace(i,"")
            
        stat = stat.replace("@","")
        media = favorite.entities.get('media', [])

        if(len(media) > 0):##busca si hay imagen
            #si existe video, lo cambia como media           
            if not vidcheck:
                media = favorite.entities['media'][0]['media_url']
            else:
                media = vidurl             
            try:
                wget.download(media,joseo_favs_dir)##guardamos imagenes en imgtxt
            except FileNotFoundError:
                try:
                    os.mkdir("imgtxt")
                    wget.download(media,joseo_favs_dir)
                except:
                    pass
            if len(stat) == 0:
                stat = "\n"
            tuit = str(stat)+"_PIC_"+media##saca la imagen real y la concatena al tuit
        else:
            tuit = str(stat)
        #print(tuit)
        f.write(tuit+"\n")

    print("FAVS EXTRAIDOS")
    f.close()



print("----------------------------------")
print("EXTRAER FAVS STANDALONE v1.0 ")
print("----------------------------------")


opt = input("Extraer favs? [s/n]: ")
opt = opt.lower()
if opt == "s":
   try:
       max = int(input("Cantitad de items?: "))
   except ValueError:
       max = 20

   favs(max)
