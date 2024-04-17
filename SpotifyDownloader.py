import os, time, shutil
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from colorama import init as colorama_init
from colorama import Fore
from colorama import Style
colorama_init()

os.system('cls')

def initMenu():
    userName = os.getlogin()
    mainMusicsPath = os.path.join(r'C:\Users', userName+r'\Music')
    musicData = {
        'url': '',
        'name': '',
        'album': '',
        'authorName': '',
        'musicType': '',
        'zipDirectory': '',
        'musicDirectory': ''
    }

    # Iniciando o Chrome e configurando
    def initChromeDriver():
        chromeBrowser = webdriver.ChromeOptions()
        prefs = {"download.default_directory" : mainMusicsPath}
        chromeBrowser.add_argument('--headless=new')  
        chromeBrowser.add_experimental_option("prefs", prefs)
        chromeBrowser = webdriver.Chrome(options=chromeBrowser)
        chromeBrowser.get('https://spotifydown.com/pt')
        return chromeBrowser
    chromeBrowser = initChromeDriver()
    wait = WebDriverWait(chromeBrowser, 25)

    # Esperando input do usuário e dar o musicType
    def inputMenu():
        print('-----Spotify-Automated-downloader-----')
        musicData['url'] = input('Insert URL: ')
        if musicData['url'].find('album') == -1:
           musicData['musicType'] = 'track'
        else:
            musicData['musicType'] = 'album'
    inputMenu()

    def doActionsInSite():
        for tentativasPassos in range(0, 3):
            try:
                # Pegando e escrevendo a url no elemento
                time.sleep(2)
                element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div/div[1]/input')))
                element.send_keys(musicData['url'])

                # Apertando button de procurar
                element = chromeBrowser.find_element(By.XPATH, '//*[@id="__next"]/div/button')
                element.click() 

                musicData['name'] = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div/div[2]/p[1]'))).text
                musicData['authorName'] = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div/div[2]/p[2]'))).text
                if musicData['musicType'] == 'album':
                    musicData['album'] = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div/div[2]/p[1]'))).text
                else:
                    musicData['album'] = '-'
                print(f'Name: {Fore.GREEN}{musicData["name"]}{Style.RESET_ALL}, Author: {Fore.GREEN}{musicData['authorName']}{Style.RESET_ALL}, Album: {Fore.GREEN}{musicData['album']}{Style.RESET_ALL}')

                if musicData['musicType'] == 'track':
                    downloadZipButton = chromeBrowser.find_element(By.XPATH, '//*[@id="__next"]/div/div[2]/div[2]/div/div[2]/button')
                    downloadZipButton.click()

                    element = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="__next"]/div/div[2]/div[1]/a[1]')))
                    element.click()
                    
                    # Check if has downloaded
                    musicData['musicDirectory'] = os.path.join(mainMusicsPath, r'spotifydown.com - ' + musicData['name']+ r'.mp3')
                    dotCount = 1
                    while True:
                        if not os.path.isfile(musicData['musicDirectory']):
                            print(f'{Fore.MAGENTA}Downloading{"." * dotCount}{Style.RESET_ALL}', end='\r')
                            print(end='\x1b[2K' )
                            time.sleep(1)
                            dotCount = 1 if dotCount > 2 else dotCount + 1
                        else:
                            print(f'{Fore.GREEN}Downloaded{Style.RESET_ALL}')
                            chromeBrowser.quit()
                            break
                else:
                    # Apertando botão de zip
                    downloadZipButton = chromeBrowser.find_element(By.XPATH, '/html/body/div[1]/div/div[2]/div[1]/button')
                    downloadZipButton.click()
                    time.sleep(1)
            
                    # Apertando botão de confirmar
                    downloadZipButton = chromeBrowser.find_element(By.XPATH, '//*[@id="__next"]/div/div[2]/div[2]/div/div/button[1]')
                    downloadZipButton.click()
                    time.sleep(1)   

                    # Pegado informações dos downloads das músicas
                    downloadStatusName = chromeBrowser.find_elements(By.XPATH, '//*[@id="__next"]/div/div[2]/div[2]/div/div/div[1]')
                    for track in downloadStatusName:
                        print(f'{Fore.MAGENTA}Downloading - {Fore.GREEN}{track.text}{Style.RESET_ALL}')

                    # Check if has downloaded
                    musicData['zipDirectory'] = os.path.join(mainMusicsPath, musicData['album'] + r'_SpotifyDown_com.zip')
                    dotCount = 1
                    while True:
                        if not os.path.isfile(musicData['zipDirectory']):
                            print(f'{Fore.MAGENTA}Downloading{"." * dotCount}{Style.RESET_ALL}', end='\r')
                            print(end='\x1b[2K' )
                            time.sleep(1)
                            dotCount = 1 if dotCount > 2 else dotCount + 1
                        else:
                            print(f'{Fore.GREEN}Downloaded{Style.RESET_ALL}')
                            chromeBrowser.quit()
                            break
                break
            except:
                if tentativasPassos == 2:
                    print('An error is occurring.')
                else:
                    print("trying again", tentativasPassos)
                    chromeBrowser.refresh()
                    time.sleep(5)
    doActionsInSite()

    def createDirectoryOfMusic():
        # Checando se tem a pasta do autor já
        musicAuthorPath = os.path.join(mainMusicsPath, musicData['authorName'])
        if os.path.isdir(musicAuthorPath):
            print('Author exist')
        else:
            print(f"Don't exist... Creating paste called {musicData['authorName']}")
            os.mkdir(musicAuthorPath)
        
        # Checando se tem o album da música já
        albumNamePath = os.path.join(musicAuthorPath, musicData['album'])
        if os.path.isdir(albumNamePath):
            print('Album exist')
        else:
            print(f"Don't exist... Creating paste called {musicData['album']}")
            os.mkdir(albumNamePath)

        if musicData['musicType'] == 'album':
            # Movendo e descompactando as músicas na pasta do album
            try:
                shutil.move(musicData['zipDirectory'], albumNamePath)
                musicData['zipDirectory'] = os.path.join(albumNamePath, musicData['album'] + r'_SpotifyDown_com.zip')  
                shutil.unpack_archive(musicData['zipDirectory'], albumNamePath)
                os.remove(musicData['zipDirectory'])
                print(f"{Fore.YELLOW}Done!")
            except:
                print('erro ao mover')  
                os.remove(musicData['zipDirectory'])
        else:
            try:
                uga = os.path.join(albumNamePath, musicData['name']+r'.mp3')
                shutil.move(musicData['musicDirectory'], uga)
                print(f"{Fore.YELLOW}Done!")
            except:
                print('erro ao mover')  
                os.remove(musicData['musicDirectory'])
    createDirectoryOfMusic()
initMenu()    