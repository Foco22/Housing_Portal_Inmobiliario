import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import urllib.request  # we are going to need to generate a Request object
from bs4 import BeautifulSoup as soup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date
import requests
import urllib.parse
import Regiones as region
from google.cloud import storage
import os
from datetime import timedelta, datetime
import pytz
################ Web - Scraping ########################

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:63.0) Gecko/20100101 Firefox/63.0'}
today = datetime.now(pytz.timezone('Chile/Continental'))
d1 = today


############### FUNCION ###############################

def precio_casas_venta():

    
    rango_paginas = list(range(51,1001,50))

    
    df_pagina_dpto_pagina = pd.DataFrame()

    for x in rango_paginas:
        url = 'https://www.portalinmobiliario.com/venta/departamento/_Desde_{}_NoIndex_True'.format(str(x))

        req = urllib.request.Request(url=url, headers=headers)
        with urllib.request.urlopen(req) as response:
            page_html = response.read()
        
        response = BeautifulSoup(page_html).find_all('div', class_ = 'ui-search-result__wrapper')

        df_pagina_dpto = pd.DataFrame()
        for j in range(len(response)):
            try:
                #### precio ####################
                response_precio = response[j].find_all("span", {"class": "price-tag ui-search-price__part shops__price-part price-tag-billing"})[0]
                response_precio = response_precio.find_all("span", {"class": "price-tag-text-sr-only"})[0]
                response_precio = response_precio.text.split(' ')
                precio = int(response_precio[0])


                #### metros ####################
                response_metros = response[j].find_all("li", {"class": "ui-search-card-attributes__attribute"})
                response_metros = response_metros[0].text.split('útiles')
                metros = response_metros[0]


                #### dormotiros ####################
                response_dormitorio = response[j].find_all("ul", {"class": "ui-search-card-attributes ui-search-item__group__element shops__items-group-details"})[0]
                response_dormitorio = response_dormitorio.find_all("li", {"class": "ui-search-card-attributes__attribute"})
                dormotorios = response_dormitorio[1].text


                #### dormotiros ####################
                response_dormitorio = response[j].find_all("ul", {"class": "ui-search-card-attributes ui-search-item__group__element shops__items-group-details"})[0]
                response_dormitorio = response_dormitorio.find_all("li", {"class": "ui-search-card-attributes__attribute"})
                baños = response_dormitorio[2].text

                #### direccion ####################
                response_dormitorio = response[j].find_all("p", {"class": "ui-search-item__group__element ui-search-item__location shops__items-group-details"})
                direccion = response_dormitorio[0].text


                ######### Link #########################
                response_link = response[j].find_all("div", {"class": "ui-search-result__content"})
                response_link = response_link[0].find_all("a", {"class": "ui-search-result__content-wrapper ui-search-link"})[0]
                #response_link = response_link.find_all("a", {"class": "ui-search-result__content-wrapper ui-search-link"})
                link = response_link['href']

                tupla = (x,precio,metros,dormotorios,baños,direccion,link, 'departamento','venta',d1)
                df_pagina_dpto_ite = pd.DataFrame([tupla])
                df_pagina_dpto = pd.concat([df_pagina_dpto,df_pagina_dpto_ite], axis = 0)

            except:
                print('Error en la extraccion del Dpto/Casa')

        df_pagina_dpto = df_pagina_dpto.rename(columns = {0:'pagina'})
        df_pagina_dpto = df_pagina_dpto.rename(columns = {1:'monto'})
        df_pagina_dpto = df_pagina_dpto.rename(columns = {2:'metros'})
        df_pagina_dpto = df_pagina_dpto.rename(columns = {3:'dormitorios'})
        df_pagina_dpto = df_pagina_dpto.rename(columns = {4:'baños'})
        df_pagina_dpto = df_pagina_dpto.rename(columns = {5:'direccion'})
        df_pagina_dpto = df_pagina_dpto.rename(columns = {6:'Link'})
        df_pagina_dpto = df_pagina_dpto.rename(columns = {7:'tipo_vivienda'})
        df_pagina_dpto = df_pagina_dpto.rename(columns = {8:'tipo'})
        df_pagina_dpto = df_pagina_dpto.rename(columns = {9:'fecha'})


        df_pagina_dpto_pagina = df_pagina_dpto_pagina.append(df_pagina_dpto)
    
    df_pagina_dpto_pagina = df_pagina_dpto_pagina.reset_index().drop(columns =['index'])
    return df_pagina_dpto_pagina


def precio_casas_arriendo():

    
    rango_paginas = list(range(51,1001,50))

    
    df_pagina_dpto_pagina = pd.DataFrame()

    for x in rango_paginas:
        url = 'https://www.portalinmobiliario.com/arriendo/departamento/_Desde_{}_NoIndex_True'.format(str(x))

        req = urllib.request.Request(url=url, headers=headers)
        with urllib.request.urlopen(req) as response:
            page_html = response.read()
        
        response = BeautifulSoup(page_html).find_all('div', class_ = 'ui-search-result__wrapper')
        df_pagina_dpto = pd.DataFrame()
        for j in range(len(response)):
            try:
                #### precio ####################
                response_precio = response[j].find_all("span", {"class": "price-tag ui-search-price__part shops__price-part price-tag-billing"})[0]
                response_precio = response_precio.find_all("span", {"class": "price-tag-text-sr-only"})[0]
                response_precio = response_precio.text.split(' ')
                precio = int(response_precio[0])


                #### metros ####################
                response_metros = response[j].find_all("li", {"class": "ui-search-card-attributes__attribute"})
                response_metros = response_metros[0].text.split('útiles')
                metros = response_metros[0]


                #### dormotiros ####################
                response_dormitorio = response[j].find_all("ul", {"class": "ui-search-card-attributes ui-search-item__group__element shops__items-group-details"})[0]
                response_dormitorio = response_dormitorio.find_all("li", {"class": "ui-search-card-attributes__attribute"})
                dormotorios = response_dormitorio[1].text

                #### direccion ####################
                response_dormitorio = response[j].find_all("p", {"class": "ui-search-item__group__element ui-search-item__location shops__items-group-details"})
                direccion = response_dormitorio[0].text

                ######### Link #########################
                response_link = response[j].find_all("div", {"class": "ui-search-result__content"})
                response_link = response_link[0].find_all("a", {"class": "ui-search-result__content-wrapper ui-search-link"})[0]
                #response_link = response_link.find_all("a", {"class": "ui-search-result__content-wrapper ui-search-link"})
                link = response_link['href']
                
                tupla = (x,precio,metros,dormotorios, 0, direccion,link, 'departamento','arriendos',d1)
                df_pagina_dpto_ite = pd.DataFrame([tupla])
                df_pagina_dpto = pd.concat([df_pagina_dpto,df_pagina_dpto_ite], axis = 0)

            except:
                print('Error en la extraccion del Dpto/Casa')

        df_pagina_dpto = df_pagina_dpto.rename(columns = {0:'pagina'})
        df_pagina_dpto = df_pagina_dpto.rename(columns = {1:'monto'})
        df_pagina_dpto = df_pagina_dpto.rename(columns = {2:'metros'})
        df_pagina_dpto = df_pagina_dpto.rename(columns = {3:'dormitorios'})
        df_pagina_dpto = df_pagina_dpto.rename(columns = {4:'baños'})
        df_pagina_dpto = df_pagina_dpto.rename(columns = {5:'direccion'})
        df_pagina_dpto = df_pagina_dpto.rename(columns = {6:'Link'})
        df_pagina_dpto = df_pagina_dpto.rename(columns = {7:'tipo_vivienda'})
        df_pagina_dpto = df_pagina_dpto.rename(columns = {8:'tipo'})
        df_pagina_dpto = df_pagina_dpto.rename(columns = {9:'fecha'})


        df_pagina_dpto_pagina = df_pagina_dpto_pagina.append(df_pagina_dpto)
    
    df_pagina_dpto_pagina = df_pagina_dpto_pagina.reset_index().drop(columns =['index'])
    return df_pagina_dpto_pagina



def servicio_lat_lon(x):

    x = x.split(',')[0] + ',' + x.split(',')[-1] +  ', ' + 'CHILE'
    print(x)
    try:
        url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(x) +'?format=json'
        #print(requests.get(url))
        response = requests.get(url).json()
        #print(response[0]["lat"],response[0]["lon"])
        # Do the request and get the response data
        lat = response[0]["lat"]
        lon= response[0]["lon"]
        return (lat,lon)
    except:
        print('Error')
        return (0,0)


def limpiza_datos():
    
    
    ##### Arriendo ##############
    df_arriendo = precio_casas_arriendo()
    df_arriendo['metros'] =df_arriendo['metros'].apply(lambda x : 1 if ('m' in str(x[:3])) or (',' in str(x[:3])) else int(x[:3]))
    df_arriendo['dormitorios'] =df_arriendo['dormitorios'].apply(lambda x : int(x[:2]))
    df_arriendo['mes'] = df_arriendo['fecha'].apply(lambda x: str(x)[5:7])
    df_arriendo['año'] = df_arriendo['fecha'].apply(lambda x: str(x)[:4])
    df_arriendo['mes'] = df_arriendo['mes'].apply(lambda x : '0' + str(x) if len(str(x)) < 1  else str(x))
    df_arriendo['periodo'] = df_arriendo.apply(lambda row: str(row['año'])+ str(row['mes']), axis =1)
    df_arriendo['comuna'] = df_arriendo['direccion'].apply(lambda x : x.split(',')[-1][1:])   
    df_arriendo['lat'] = df_arriendo['direccion'].apply(lambda x : servicio_lat_lon(x)[0])
    df_arriendo['lng'] = df_arriendo['direccion'].apply(lambda x : servicio_lat_lon(x)[1])

    df_regiones = region.base_regiones()
    df_regiones = df_regiones[['nombre_comuna','nombre_provincia','nombre_region','Letra']]
    df_regiones = df_regiones.rename(columns = {'nombre_comuna':'comuna'})
    df_arriendo = pd.merge(df_arriendo,df_regiones, on =['comuna'], how = 'left' )
    df_arriendo = df_arriendo.loc[df_arriendo['lat'] !=0 ]
    df_arriendo = df_arriendo[~df_arriendo['Letra'].isna()]
    df_arriendo = df_arriendo.loc[df_arriendo['metros'] != 1]
    
    df_arriendo = df_arriendo.reset_index().drop(columns =['index'])

    
    
    ##### Venta ##############
    df_venta = precio_casas_venta()
    df_venta['metros'] =df_venta['metros'].apply(lambda x : int(x[:3]))
    df_venta['baños'] =df_venta['baños'].apply(lambda x : int(x[:2]))
    df_venta['dormitorios'] =df_venta['dormitorios'].apply(lambda x : int(x[:2]))
    df_venta['mes'] = df_venta['fecha'].apply(lambda x: str(x)[5:7])
    df_venta['año'] = df_venta['fecha'].apply(lambda x: str(x)[:4])
    df_venta['mes'] = df_venta['mes'].apply(lambda x : '0' + str(x) if len(str(x)) < 1  else str(x))
    df_venta['periodo'] = df_venta.apply(lambda row: str(row['año'])+ str(row['mes']), axis =1)
    df_venta['comuna'] = df_venta['direccion'].apply(lambda x : x.split(',')[-1][1:])   
    df_venta['lat'] = df_venta['direccion'].apply(lambda x : servicio_lat_lon(x)[0])
    df_venta['lng'] = df_venta['direccion'].apply(lambda x : servicio_lat_lon(x)[1])

    df_regiones = region.base_regiones()
    df_regiones = df_regiones[['nombre_comuna','nombre_provincia','nombre_region','Letra']]
    df_regiones = df_regiones.rename(columns = {'nombre_comuna':'comuna'})
    df_venta = pd.merge(df_venta,df_regiones, on =['comuna'], how = 'left' )
    df_venta = df_venta.loc[df_venta['lat'] !=0 ]
    df_venta = df_venta[~df_venta['Letra'].isna()]
    
    df_venta = df_venta.reset_index().drop(columns =['index'])
    
    df_total = pd.concat([df_venta,df_arriendo],axis = 0)

    df_total = df_total.reset_index().drop(columns =['index'])
    return df_total

def base_datos_google():


    df = limpiza_datos()
    storage_client = storage.Client.from_service_account_json("ferrous-pact-273022-63f668492a23.json")
    bucket = storage_client.get_bucket('portal_inmobiliario_proyecto')
    df.to_csv('Base_Arriendo_Venta_{}.csv'.format(str(d1)),sep =';')
    blob = bucket.blob('Base_Arriendo_Venta_{}.csv'.format(str(d1)))
    blob.upload_from_filename('Base_Arriendo_Venta_{}.csv'.format(str(d1)))

    #os.remove('Base_Arriendo_Venta_{}.csv'.format(str(d1)))

    return True

base_datos_google()
