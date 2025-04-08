import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor

# Lista de URLs adicionais para acessar
urls_adicionais = [
    "porto-bello-iv",
    "viva-residence-alecrim",
    "viva-residence-bela-vista-2-etapa",
    "viva-residence-cidade-jardim",
    "viva-club-da-ilha",
    "viva-mais-barra",
    
]

# Função para fazer download da imagem
def download_image(img_url, img_path):
    response = requests.get(img_url)
    if response.status_code == 200:
        with open(img_path, 'wb') as file:
            file.write(response.content)
        print(f"Imagem {os.path.basename(img_path)} baixada com sucesso em {img_path}")
    else:
        print(f"Erro ao baixar a imagem {os.path.basename(img_path)}")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)


url_base = "https://vivaconstrucoes.com.br/empreendimentos/pronto-para-morar/"

for url_adicional in urls_adicionais:
    full_url = url_base + url_adicional
    driver.get(full_url)
    
    # Esperar a página carregar
    time.sleep(5)
    
    select_element = Select(driver.find_element(By.ID, "mesAno"))
    
    options = [option for option in select_element.options if option.get_attribute('value') and option.get_attribute('value') != "Selecione o mês e o ano"]
    
    main_directory = os.path.join("imagens", url_adicional)
    os.makedirs(main_directory, exist_ok=True)
    
    for option in options:
        month_year = option.text.strip()
        option_value = option.get_attribute('value')
        
        print(f"Selecionando a opção: {option_value} - {month_year}")
        
        select_element.select_by_value(option_value)
        
        time.sleep(5)
        
        images = driver.find_elements(By.CSS_SELECTOR, ".estagio-obra a.item")
        
        directory = os.path.join(main_directory, month_year.replace(" ", "_"))
        os.makedirs(directory, exist_ok=True)
        
        download_tasks = []
        for img in images:
            img_url = img.get_attribute('href')
            img_name = os.path.basename(img_url)
            img_path = os.path.join(directory, img_name)
            download_tasks.append((img_url, img_path))
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(lambda p: download_image(*p), download_tasks)
        
        select_element = Select(driver.find_element(By.ID, "mesAno"))


driver.quit()