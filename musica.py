# -*- coding: utf-8 -*-
#downloader para music.163.com
#Patricio Reinoso M.
#2015-04-12

import md5
import base64
import urllib2
import urllib
import json
import random
import os
import sys
import wget


def busqueda(nombre, tipo):
    if tipo=='artista':
        idTipo=100
    elif tipo=='disco':
        idTipo=10
    elif tipo=='cancion':
        idTipo=1
    search_url = 'http://music.163.com/api/search/get'
    params = {
            's': nombre,
            'type': idTipo,
            'offset': 0,
            'sub': 'false',
            'limit': 100
    }
    params = urllib.urlencode(params)
    resp = urllib2.urlopen(search_url, params)
    datos = json.loads(resp.read())
    if datos['code'] == 200:
        return datos["result"]
    else:
        return None
    
def buscaAlbumsPorArtista(artista_id):
    albums = []
    offset = 0
    while True:
        url = 'http://music.163.com/api/artist/albums/%s?offset=%d&limit=50' % (artista_id, offset)
        resp = urllib2.urlopen(url)
        tmp_albums = json.loads(resp.read())
        albums.extend(tmp_albums['hotAlbums'])
        if tmp_albums['more'] == True:
            offset += 50
        else:
            break
    return albums

def buscaCancionesDisco(album_id):
    url = 'http://music.163.com/api/album/%s/' % album_id
    resp = urllib2.urlopen(url)
    songs = json.loads(resp.read())
    return songs['album']['songs']

def buscaCancion(cancion_id):
    url = 'http://music.163.com/api/song/detail?ids=[%s]' % cancion_id
    resp = urllib2.urlopen(url)
    songs = json.loads(resp.read())
    return songs['songs'][0]


def descargaDisco(disco_id):
    datosJson=buscaCancionesDisco(disco_id)
    
    for track in datosJson:
        #trackName=remueveCaracteresEspeciales(track["bMusic"]["name"])
        trackPos=remueveCaracteresEspeciales(track["position"])
        trackName=str(trackPos).zfill(2)+" - "+remueveCaracteresEspeciales(track["name"])
        albumName=remueveCaracteresEspeciales(track["album"]["name"])
        artistName=remueveCaracteresEspeciales(track["artists"][0]["name"])
        print (artistName+" - "+albumName)
        print (trackName+".mp3")
        try:
            archivo=wget.download(track["mp3Url"])
            carpeta=artistName+"/"+albumName+"/"
            if not os.path.exists(carpeta):
                os.makedirs(carpeta)
            os.rename(archivo, "./"+carpeta+trackName+".mp3")
        except:
            print "Error al descargar "+track["mp3Url"]
        #print json.dumps(track)
        print "*****************************************"
    print "Descarga del album "+albumName+" completa!"
    return True

def descargaCancion(cancion_id):
    track=buscaCancion(cancion_id)
    print json.dumps(track)
    trackPos=remueveCaracteresEspeciales(track["position"])
    trackName=str(trackPos).zfill(2)+" - "+remueveCaracteresEspeciales(track["name"])
    albumName=remueveCaracteresEspeciales(track["album"]["name"])
    artistName=remueveCaracteresEspeciales(track["artists"][0]["name"])
    print (artistName+" - "+albumName)
    print (trackName+".mp3")
    try:
        archivo=wget.download(track["mp3Url"])
        carpeta=artistName+"/"+albumName+"/"
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)
        os.rename(archivo, "./"+carpeta+trackName+".mp3")
    except:
        print "Error al descargar "+track["mp3Url"]
    #print json.dumps(track)
    print "*****************************************"
    print "Descarga de la canción "+albumName+" completa!"
    return True

def remueveCaracteresEspeciales(texto):
    texto=str(texto)
    texto=texto.replace("\\", "-")
    texto=texto.replace('/', "-")
    texto=texto.replace(':', "-")
    texto=texto.replace("'", "")
    texto=texto.replace('$', "")
    texto=texto.replace('%', "")
    texto=texto.replace('#', "")
    texto=texto.replace('@', "")
    texto=texto.replace('?', "")
    texto=texto.replace('¿', "")
    texto=texto.replace('!', "")
    texto=texto.replace('Ç', "")
    return texto

    
    
#configuramos la cookie para el sitio web
cookie_opener = urllib2.build_opener()
cookie_opener.addheaders.append(('Cookie', 'appver=2.0.2'))
cookie_opener.addheaders.append(('Referer', 'http://music.163.com'))
urllib2.install_opener(cookie_opener)


print "Descargas de música usando el API de http://music.163.com"
print "1) Búsqueda por artista"
print "2) Búsqueda por nombre de album"
print "3) Búsqueda por nombre de canción"
print ""
opcion = int(raw_input('Seleccione una opción: '))
if (opcion==1):
    #busqueda por cancion
    print ""
    query=raw_input('Ingrese el nombre del grupo: ')
    jsonArtista=busqueda(query, 'artista')
    if (jsonArtista["artistCount"]>0):
        i=1
        dictArtistas={}
        for a in jsonArtista['artists']:
            print '[%2d] Id: %d\tNombre: %s' % (i, a['id'], a['name'])
            dictArtistas.update({str(i):a['id']})
            i=i+1
        print ""
        numArtista=raw_input('Ingrese el numero del artista encontrado: ')
        idArtista=dictArtistas[str(numArtista)]
        print ""
        print "Albumes encontrados para el artista seleccionado:"
        jsonDiscos=buscaAlbumsPorArtista(idArtista)
        i=1
        dictDiscos={}
        for a in jsonDiscos:
            print '[%3d] Id: %d\tNombre: %s' % (i, a['id'], a['name'])
            dictDiscos.update({str(i):a['id']})
            i=i+1
        numDisco=str(raw_input('Ingrese el numero del disco a descargar, o 0 para descargar todos: '))
        if (numDisco=="0"):
            print "Descargando discografía completa"
            idDiscos=dictDiscos.values()
            print idDiscos
            for disco in idDiscos:
                descargaDisco(disco)
        else:
            descargaDisco(dictDiscos[str(numDisco)])
        
    else:
        print "No existen resultados para la búsqueda de: "+query
elif (opcion==2):
    #busqueda por disco
    query=raw_input('Ingrese el nombre del disco: ')
    jsonDisco=busqueda(query, 'disco')
    #print json.dumps(jsonDisco)
    if (jsonDisco["albumCount"]>0):
        i=1
        dictDiscos={}
        for a in jsonDisco["albums"]:
            print '[%3d] Id: %d\tNombre: %s - %s' % (i, a['id'], a['name'], a['artist']['name'])
            dictDiscos.update({str(i):a['id']})
            i=i+1
        numDisco=str(raw_input('Ingrese el numero del disco a descargar: '))
        descargaDisco(dictDiscos[str(numDisco)])
elif (opcion==3):
    #busqueda por cancion
    query=raw_input('Ingrese el nombre de la cancion: ')
    jsonCancion=busqueda(query, 'cancion')
    if (jsonCancion["songCount"]>0):
        print "Encontradas "+str(jsonCancion["songCount"])+" canciones"
        i=1
        dictCanciones={}
        for a in jsonCancion['songs']:
            print '[%3d] Id: %d\tNombre: %s' % (i, a['id'], a['name']+" - "+a['album']['name']+" ["+a['artists'][0]['name']+"]")
            dictCanciones.update({str(i):a['id']})
            i=i+1
    numCancion=str(raw_input('Ingrese el numero de la cancion a descargar: '))   
    descargaCancion(dictCanciones[str(numCancion)])
