from bs4 import BeautifulSoup
import requests
import time
import jsonlines
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from dotenv import dotenv_values


env_variables = dotenv_values('.env')
proxy = env_variables['PROXY']
base_url = ['INPUT_URL']
file_name = ['OUTPUT_FILE']

page_number = 1
tags_list = []
author_list = []
sentence_list = []

def selenium_driver_constructor():
    options = Options()
    options.add_experimental_option("detach", True)
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def get_quote_elements(soup):
    quotes_container = soup.find("div",id="quotesPlaceholder")
    return quotes_container.find_all('div', class_='quote')

def get_sentence(quote_element):
    sentence = quote_element.find('span', class_='text')
    return sentence.text

def get_author(quote_element):
    author = quote_element.find('small', class_='author')
    return author.text

def get_tags(quote_element):
    tags_div = quote_element.find('div', class_='tags')
    if tags_div:
        tag_elements = tags_div.find_all('a', class_='tag')
        return [tag.text for tag in tag_elements]
    return None


while True:

    driver = selenium_driver_constructor()
    driver.get(f'{base_url}page/{page_number}/')
    wait_quote_element = WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.CLASS_NAME, 'quote')))
    page_source = driver.page_source
    driver.close()

    soup = BeautifulSoup(page_source, 'html.parser')
    for quote_element in get_quote_elements(soup):
        sentence_list.append(get_sentence(quote_element))
        author_list.append(get_author(quote_element))
        tags_list.append(get_tags(quote_element))

    page_number += 1
    next_element = soup.find('li', class_='next')
    if next_element is None:
        break

with jsonlines.open(f'{file_name}', mode='w') as writer:
        for sentence,author,tags in zip(sentence_list,author_list,tags_list):
            data = {
                "text": sentence,
                "by": author,
                "tags": tags
            }
            writer.write(data)





