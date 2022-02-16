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



def picRandomizer():
    print("HORA JOSEO")

    toss = random.randint(0,20)#decisión random de si lee los favs o la carpeta de joseos

    #txt favs
    if toss >= 0 and toss <= 9:
        print("TXT FAVS")
        try:
            f = open(file=joseo_favs_txt,mode="r+",encoding="utf-8")
        except FileNotFoundError:
            print("CREANDO TUITS.TXT")
            f = open(file=joseo_favs_txt,mode="a+",encode="utf-8")
            f.close()
            f = open(file=joseo_favs_txt,mode="r+",encode="utf-8")
        
        lines = f.readlines()##lee las lineas        
        tuit = lines[random.randint(0,len(lines))-1]
        try:
            flog = open(file=favlog,mode="r+",encoding="utf-8")##Abre el log en read write
            flines = flog.readlines()
            i = 0
            if len(lines) != len(flines):
                while i < len(flines):##recorre las lineas buscando el joseo
                    if flines[i] == (tuit):  
                        print("REPETIDO. BUSCAR NUEVO JOSEO ->(",tuit,")")
                        tuit = lines[random.randint(0,len(lines))-1] #selecciona una linea random
                        i = 0
                    else: 
                        i = i+1
            else:
                print("YA NO HAY MEMES EN TXT")
                api.update_status(status="Si ves este tuit es porque me he quedado sin memes para subir y el bot ha entrado en pánico y se ha suicidado")
                sys.exit()
        
        except FileNotFoundError:##si el fichero no exisita, lo crea
            print("LOG NO ENCONTRADO, CREANDO.")
            flog = open(file=favlog,mode="a+",encoding="utf-8")     

        print("aaaa "+tuit)
        flog.write(tuit)##escribe el joseo en el log
        flog.close()##cierra fd
        f.close()##cierra fd
        
        if "twimg.com" in tuit:#si tiene imagen:
            print("FAV CON IMAGEN")
            tuit = tuit.split("_PIC_")#splitea por la flag PIC
            reference = tuit[1]#reference mantiene el nombre del archivo
            stat = tuit[0]#status se queda la caption
            reference = reference.split("/");reference = reference[len(reference)-1]#saca el nombre del archivo local
            reference = reference.split("\n");reference = reference[0]
            if "?tag=12" in reference:
                reference = reference.replace("?tag=12","")

            path = str(joseo_favs_dir+reference)#saca la ruta de la imagen
            print(stat)
            print(path)
            subir = api.media_upload(path) #sube la foto a twitter
            tuitear = api.update_status(status=stat, media_ids=[subir.media_id])##devuelve la id de la foto y la tuitea    
        else:
            print("FAV SIN IMAGEN")
            tuitear = api.update_status(status=tuit)#sube el tuit
        print("RESULTADOS: ",tuit)
        

    #carpeta joseos
    ##============================================================================================================
    else:
        print("CARPETA JOSEOS")
        folder = joseo_manual_dir
        vector_joseos = glob.glob(folder + "*") ##Genera la ruta de todos los ficheros
        media = vector_joseos[random.randint(0,len(vector_joseos))-1] #selecciona un fichero random
        try:
            f = open(log,"r+")##Abre el log en read write
            lines = f.readlines()##lee las linas        
            i = 0
            if len(vector_joseos) != len(lines):
                while i < len(lines):##recorre las lineas buscando el joseo
                    if lines[i] == (media+"\n"):  
                        print("REPETIDO. BUSCAR NUEVO JOSEO ->(",media,")")
                        media = vector_joseos[random.randint(0,len(vector_joseos))-1] #selecciona un fichero random
                        i = 0
                    else: 
                        i = i+1
            else:
                print("YA NO HAY MEMES EN LA CARPETA")
                picRandomizer()
                sys.exit()                
        
        except FileNotFoundError:##si el fichero no exisita, lo crea
            print("LOG NO ENCONTRADO, CREANDO.")
            f = open(log,"a+")
    
        f.write(media+"\n")##escribe el joseo en el log
        f.close()##cierra fd

        josear = media.split("\\")#splitea la ruta y se queda con el filename
        josear = josear[1].split("_")#splitea el filename y nos queda el formato: [0] = CAP [1] = status [2..] = garbage
        
        #CAP detecta si el archivo media tendrá caption o no.
        #FORMATO:

        #CAP_caption_.png
        #TXT_status_.png

        if josear[0].lower() == "cap":
            print("JOSEO CON CAPTION")
            subir = api.media_upload(media) #sube la foto a twitter
            tuitear = api.update_status(status=josear[1], media_ids=[subir.media_id])##devuelve la id de la foto y la tuitea        
        elif josear[0].lower() == "txt":
            print("JOSEO SOLO TEXTO")
            tuitear = api.update_status(status=josear[1])##devuelve la id de la foto y la tuitea                
        else:
            print("JOSEO SIN CAPTION")
            subir = api.media_upload(media) #sube la foto a twitter
            tuitear = api.update_status(status="", media_ids=[subir.media_id])##devuelve la id de la foto y la tuitea                
        print("RESULTADOS: ",media)


def favs(max):
    f = open(file=joseo_favs_txt,mode="a+",encoding="utf-8")
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
print("FreemanJoseoBot v1.0 - EJECUTADO")
print("----------------------------------")


opt = input("Extraer favs? [s/n]: ")
opt = opt.lower()
if opt == "s":
   try:
       max = int(input("Cantitad de items?: "))
   except ValueError:
       max = 20

   favs(max)

print("horario")
#DEBUG
picRandomizer()

##HORARIOS
schedule.every().day.at("10:30").do(picRandomizer)
print("Programado mañana")
schedule.every().day.at("16:00").do(picRandomizer)
print("Programado mediodia")
schedule.every().day.at("19:00").do(picRandomizer)
print("Programado Tarde-noche")
while True:
   schedule.run_pending()
   time.sleep(1)   
    

