#This program will scrape Craiglist to get all currently listed cars and trucks in the US and their attributes such as odometer, price, year etc.

from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from pandas import ExcelWriter
import pandas as pd
import re

pages = set()

#Get the US states links
state_links = []
try:    
    html = urlopen('https://redding.craigslist.org/')
except HTTPError as e:
    print(e)
except URLError:
    print('The server could not be found!')
try:
    bs = BeautifulSoup(html.read(),'html.parser').find_all('a',href = re.compile(r'geo.craigslist.org/iso/us/..$'))
    for link in bs:
        state_links.append(link.attrs)
    for a in range(0,len(state_links)):
        state_links[a]['href'] = f"https:{state_links[a]['href']}"
except AttributeError as e:
    print(e)
    print('doesnt have tag') 
    
#state_links = state_links[:32] --- de-comment this line if you want to reduce/select the number of US states from which you want to scrape trucks and cars for sale data


#Get the US counties/cities links    
county_list = []
for a in range(0,len(state_links)):
    try:    
        html = urlopen(state_links[a]['href'])
    except HTTPError as e:
        print(e)
    except URLError:
        print('The server could not be found!')
    try:
        bs_county = BeautifulSoup(html.read(),'html.parser').find_all('a',href = re.compile(r'https://((?!www)[a-z]+).craigslist.org$'))
        for link in bs_county:
            county_list.append(link.attrs)
            #print(link.attrs) --- de-comment this line if you want to reduce/select the number of US states from which you want to scrape trucks and cars for sale data
    except AttributeError as e:
        print(e)
        print('doesnt have tag')
      
county_list = county_list[:50]

        
for b in range(0,len(county_list)):
    county_list[b]['href'] = f"{county_list[b]['href']}/d/cars-trucks/search/cta"
    

#Sets up the main dataframe used for the final excel file in which all car listings and their corresponding attributes will be stored
ExcelFile = pd.DataFrame({'ID':['Null'],'link':['Null'],'odometer':[0],'paint color':['test'],
                              'VIN':['test'],'fuel':['test'],'type':['test'],
                              'drive':['test'],'title status':['test'],
                              'price':[0],'brand':['test'],'model':['Null'],
                              'transmission':['test'],'cylinders':['test'],
                              'year make':[0],'date posted':[datetime.today()]})

#Lists of car brands and models to loop through so that each car listing can have 'brand' and 'model' attributes
car_brands = ['jeep','subaru','bmw','mercedes','audi','ford','honda'
                              ,'toyota','acura','lexus','gmc','dodge','cadillac','chevy',
                              'chevrolet','porsche','tesla','chrysler','nissan','volkswagen',
                              'volvo','jaguar','buick','hyundai','lincoln','mazda','ram',
                              'kia','infiniti','mitsubishi','fiat','mini','alfa','suzuki',
                              'land ']
car_models = [' a3',' a4',' a5',' a6',' a7',' a8',' q5',' q7','mdx','rdx','ilx','tlx','2 series'
              ,'3 series','4 series','5 series','7 series','8 series',' x1',' x2'
              ,' x3',' x4',' x5',' x6',' x7','encore','encore gx','envision','envision avenir'
              ,'enclave','enclave avenir','escalade',' xt4',' xt5',' xt6',' ct4',' ct5'
              ,'colorado','silverado','trailblazer','trax','equinox','blazer'
              ,'spark','malibu','camaro','corvette',' 300','voyager','pacifica'
              ,'charger','challenger','durango','journey','caravan','spider'
              ,'ecosport','escape','bronco','edge','explorer','mustang','tahoe'
              ,'expedition','maverick','ranger','f150','f-150','super duty',' f250',' f-250',' f 250'
              ,'fusion','sierra 1500','canyon','sierra heavy duty','terrain',' f350',' f 350',' f-350'
              ,'acadia','yukon','cr-v','cr v',' crv','hr-v','hr v','pilot','passport',' sierra'
              ,'civic sedan','accord','insight','clarity','civic','odyssey', ' mkx'
              ,'ridgeline','vanue','kona','tucson','santa cruz','santa fe'
              ,'palisade','q50','q60','qx50','qx55','qx60','qx80','f pace'
              ,'f-pace','f-type','f type',' xf','grand cherokee','cherokee'
              ,'compass','renegade','gladiator','wrangler','soul','sportage'
              ,'seltos','niro','sorento','telluride','carnival','rio','forte'
              ,'k5','stinger',' is ',' is',' es ',' es',' ls ',' ls',' ux ',' ux', ' ats'
              ,' nx ',' rx ',' gx ',' nx',' rx',' gx',' lx',' rc',' lc','suburban'
              ,' lx ',' rc ',' lc ','navigator','aviator','nautilus','corsair'
              ,'cx-3','cx 3','cx3','cx-30','cx 30','cx30','cx-5','cx 5',' cx5'
              ,'cx-9',' cx9','cx 9','mazda 3','mazda3','mazda 6','mazda6'
              ,'mx-5','mx5','mx 5',' glc ',' glc',' glb', 'glb ',' glc','dart'
              ,' glc ',' gle ',' gle',' gls',' gls ','a-class','a class','sonata'
              ,'c-class','c class','e-class','e class','s-class','s class', 'elantra'
              ,'hardtop','countryman','clubman','outlander','mirage','pathfinder','fiesta'
              ,'armada','murano','kicks','rogue','versa','sentra','altima','maxima'
              ,'leaf','frontier','titan','evoque','velar','cruze','optima','impala'
              ,'discovery','defender','range rover','impreza','legacy','crosstrek'
              ,'forester','outback','accent','brz','wrx','prius','corolla','camry','traverse'
              ,'avalon','mirai',' 86 ',' 86','supra','sienna','tacoma','tundra'
              ,'venza','c-hr','c hr','rav4','highlander','4runner','4-runner','mkz',' fit', ' land cruiser'
              ,'sequoia','jetta','taos','passat','arteon','golf','tiguan'
              ,'atlas','xc90','xc60','xc40','s90','s60','v90','v60'
              ,' 1500',' 2500',' 3500',' 500',' 370z', ' ct6']

total_count = 0
file_saving_count = 0

#Loops through all US counties/cities
for a in range(0,len(county_list)):
        print(f"starting a new loop, county being {county_list[a]['href']}")
        total_count_liste = []
        liste = []
            
        #Gets the count of total cars of each US county/city
        try:    
            html = urlopen(county_list[a]['href'])
        except HTTPError as e:
            print(e)
        except URLError:
            print('The server could not be found!')
        except ConnectionResetError as e:
            print(e)
        try:
            bs_test = BeautifulSoup(html.read(),'html.parser').find_all('span',{'class':'totalcount'})
            for the_count in bs_test:
                total_count_liste.append(re.sub('[^0-9]','',str(the_count)))
            total_count_liste = int(str(set(total_count_liste))[2:-2])
        except AttributeError as e:
            print(e) 
        
        
        #Retrieves the first 120 car listings links of each US county/city
        try:
            html = urlopen(county_list[a]['href'])
        except HTTPError as e:
            print(e)
        except URLError:
            print('The server could not be found!')
        try:
            bs = BeautifulSoup(html.read(),
                        'html.parser').find_all('a',
                        href = re.compile(r'craigslist.org/((?![^a-z]).)((?![^a-z]).)((?![^a-z]).)/'))
            for link in bs:
                if 'href' in str(link) and 'data-ids' not in str(link):
                    if 'data-id' in str(link):
                        liste.append(link.attrs)
        except AttributeError:
            print('doesnt have tag') 
            
            
            
            
        #Retrieves all car listings links of each US county/city
        while total_count_liste >= (len(liste)+120): 
            url = f"{county_list[a]['href']}?s={len(liste)}"
            try:
                html = urlopen(url)
            except HTTPError as e:
                print(e)
            except URLError:
                print('The server could not be found!')
            try:
                bs = BeautifulSoup(html.read(),
                    'html.parser').find_all('a',
                    href = re.compile(r'craigslist.org/((?![^a-z]).)((?![^a-z]).)((?![^a-z]).)/'))
                for link in bs:
                    if 'href' in str(link) and 'data-ids' not in str(link):
                        if 'data-id' in str(link):
                            liste.append(link.attrs)
            except AttributeError:
                print('doesnt have tag')
            
            
            

        #liste = liste[:10] --- de-comment this line if you want to limit the number of vehicles that will be scraped per US county/city (there should be around 400+ counties/city)
        


        #Loops through all car listings
        for b in range(0,len(liste)):
            model_validated = 0
            dictio = {'ID':'Null','link':'Null','odometer':0,'paint color':'Null',
                              'VIN':'Null','fuel':'Null','type':'Null',
                              'drive':'Null','title status':'Null',
                              'price':0,'brand':'Null','model':'Null'
                              ,'transmission':'Null','cylinders':'Null',
                              'year make':0,'date posted':datetime.today()}

            la_bonne_listasse = []
            module_b = []
            module_time = []
                
            #Retrieves the attributes for each car listing
            try:
                html = urlopen(liste[b]['href'])
            except HTTPError as e:
                print(e)
            except URLError:
                print('The server could not be found!')
            try:
                bs_2 = BeautifulSoup(html.read(),'html.parser')
            except AttributeError as e:
                print(e) 
            
            #Inserts each attribute, if found, into the dictionary that is going to be appended to the main dataframe 
            try:
                dictio['ID'] = liste[b]['data-id']
            except KeyError as e:
                print(e)
            dictio['link'] = liste[b]['href']
            data = bs_2.find_all('span')
            data2 = bs_2.find_all('b')
            data3 = bs_2.find_all('time',{'class':'date timeago'})
            for ligne in data:
                la_bonne_listasse.append(str(ligne))
            for ligne in data2:
                module_b.append(str(ligne))
            try:
                for t in range(0,len(car_models)):
                    if (car_models[t] in module_b[0].lower()) and (model_validated == 0):
                        dictio["model"] = car_models[t]
                        model_validated = 1
                for ligne in data3:
                    module_time.append(str(ligne))
                dictio["date posted"] = datetime.strptime(module_time[1][63:79], '%Y-%m-%d %H:%M')
                year_make = module_b[0]
                year_make = re.sub('[^0-9]',' ',year_make)
                year_make = re.sub('(([^0-9].)([^0-9].)([^0-9].)([^0-9].))','',year_make)
                year_make = re.sub(' ','',year_make)
            except IndexError as e:
                print(e)
            if len(year_make) > 0:
                if len(year_make) > 4:
                    year_make = year_make[:4]
                year_make = int(year_make)
                if year_make <= (int(datetime.today().strftime("%Y"))+1):
                    dictio["year make"] = year_make
            for i in range(0,len(la_bonne_listasse)):
                la_bonne_listasse[i] = re.sub('<b','',la_bonne_listasse[i])
                la_bonne_listasse[i] = re.sub('b>','',la_bonne_listasse[i])
                la_bonne_listasse[i] = re.sub('[^a-zA-Z0-9.]',' ',la_bonne_listasse[i])
                if 'price' in la_bonne_listasse[i] and 'postingtitletext' not in la_bonne_listasse[i]:
                    car_price = re.sub('price','',la_bonne_listasse[i])
                    car_price = re.sub('[^0-9.]',' ',car_price)
                    car_price = re.sub(' ','',car_price)
                    if  '.' in car_price:
                        car_price = car_price[:-3]
                    car_price = re.sub('[^0-9]',' ',car_price)
                    if len(car_price) >0:
                        car_price = int(car_price)
                        dictio["price"] = car_price
                la_bonne_listasse[i] = re.sub('[^a-zA-Z0-9]',' ',la_bonne_listasse[i])
                la_bonne_listasse[i] = re.sub('span','',la_bonne_listasse[i])
                la_bonne_listasse[i] = re.sub('class','',la_bonne_listasse[i])[2:]
                if 'odometer' in la_bonne_listasse[i]:
                    odometer = re.sub('odometer','',la_bonne_listasse[i])
                    odometer = re.sub('[^0-9]',' ',la_bonne_listasse[i])
                    odometer = re.sub(' ','',odometer)
                    if len(odometer) > 0:
                        odometer = int(odometer)
                        dictio["odometer"] = odometer
                if 'paint color' in la_bonne_listasse[i]:
                    paint_color = re.sub('paint color','',la_bonne_listasse[i])
                    paint_color = re.sub(' ','',paint_color)
                    dictio["paint color"] = paint_color
                if 'VIN' in la_bonne_listasse[i]:
                    Vehicle_Identification_Number = re.sub('VIN','',la_bonne_listasse[i])
                    Vehicle_Identification_Number = re.sub(' ','',Vehicle_Identification_Number)
                    dictio["VIN"] = Vehicle_Identification_Number
                if 'fuel' in la_bonne_listasse[i]:
                    fuel = re.sub('fuel','',la_bonne_listasse[i])
                    fuel = re.sub(' ','',fuel)
                    dictio["fuel"] = fuel
                if 'type' in la_bonne_listasse[i]:
                    car_type = re.sub('type','',la_bonne_listasse[i])
                    car_type = re.sub(' ','',car_type)
                    dictio["type"] = car_type
                if 'drive' in la_bonne_listasse[i]:
                    drive = re.sub('drive','',la_bonne_listasse[i])
                    drive = re.sub(' ','',drive)
                    dictio["drive"] = drive
                if 'title status' in la_bonne_listasse[i]:
                    title_status = re.sub('title status','',la_bonne_listasse[i])
                    title_status = re.sub(' ','',title_status)
                    dictio["title status"] = title_status
                for y in range(0,len(car_brands)):
                    if car_brands[y] in la_bonne_listasse[i].lower():
                        brand = car_brands[y]
                        dictio["brand"] = brand
                if 'transmission' in la_bonne_listasse[i]:
                    transmission = re.sub('transmission','',la_bonne_listasse[i])
                    transmission = re.sub(' ','',transmission)
                    dictio["transmission"] = transmission
                if 'cylinders' in la_bonne_listasse[i]:
                    cylinders = re.sub('cylinders','',la_bonne_listasse[i])
                    cylinders = re.sub('[^0-9]',' ',la_bonne_listasse[i])
                    cylinders = re.sub(' ','',cylinders)
                    if len(cylinders) > 0:
                        cylinders = int(cylinders)
                        dictio["cylinders"] = cylinders
            total_count = total_count +1
            file_saving_count = file_saving_count + 1
            print(f'{b}/{len(liste)}, total scraped: {total_count}') #---- you can comment out this line if you find getting this data printed on your while the scraper is running annoying
            ExcelFile = ExcelFile.append(dictio,ignore_index=True,sort=False)
            
            #saving the excel file every batch of 100 scraped cars, in case if the connection crashes you still has the data saved (you can change the directory location as you please)
            if file_saving_count == 100:
                writer = ExcelWriter(r'C:\Users\dimit\Downloads\current_tickets.xlsx')
                ExcelFile.to_excel(writer,'cars', index = False)
                writer.save()
                writer.close()
                file_saving_count = 0
                
