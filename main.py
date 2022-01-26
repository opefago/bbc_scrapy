import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service

from bs4 import BeautifulSoup

import time

import xlsxwriter

chrome_options = Options()
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")

url = 'https://www.bbc.com/'


def scroll_to_end(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        # Scroll down to the bottom.
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load the page
        time.sleep(2)
        # Calculate new scroll height and compare with last height.
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def get_links(driver, main_url, xpath):
    driver.get(main_url)
    driver.implicitly_wait(2)
    scroll_to_end(driver)
    elements = driver.find_elements(By.XPATH, xpath)
    list_url = [(el.get_attribute('href'), el.text) for el in elements]
    return list_url


def scrape(driver, link_url, link_text):
    driver.get(link_url)
    driver.implicitly_wait(2)
    heading = fetch_header(driver, link_text)
    print(heading)
    print(fetch_body(driver))


def fetch_body(driver):
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')
    top = soup.find('article')
    if top is not None:
        paragraphs = top.find_all('p', class_='ssrcss-1q0x1qg-Paragraph eq5iqo00')
        if len(paragraphs) == 0:
            paragraphs = soup.find_all('p', class_='24eqi4to3bw.0.0.0.1.$paragraph-5.0')
        if len(paragraphs) == 0:
            paragraphs = soup.find_all("span", {'data-reactid': re.compile(r'paragraph')})
        if len(paragraphs) == 0:
            paragraphs = soup.find_all("div", class_='body-text-card__text')
    else:
        paragraphs = soup.find_all('p', class_='24eqi4to3bw.0.0.0.1.$paragraph-5.0')
        if len(paragraphs) == 0:
            paragraphs = soup.find_all("span", {'data-reactid': re.compile(r'paragraph')})
        if len(paragraphs) == 0:
            paragraphs = soup.find_all("div", class_='body-text-card__text')
    return [p.text for p in paragraphs]


def fetch_header(driver, link_text):
    heading = link_text
    try:
        heading = driver.find_element(By.XPATH, "//h1[@id='main-heading']").text
    except NoSuchElementException:
        try:
            heading = driver.find_element(By.XPATH, "//div[contains(@class, 'article-headline__text')]").text
        except NoSuchElementException:
            pass
    return heading


def save_to_file(links):
    row = 0
    column = 0
    workbook = xlsxwriter.Workbook('BBC_Frontpage_links.xlsx')
    worksheet = workbook.add_worksheet()
    for link in links:
        worksheet.write(row, column, link[0])
        row += 1
    workbook.close()


if __name__ == '__main__':
    ser = Service("./chromedriver")
    driver = webdriver.Chrome(options=chrome_options, service=ser)

    links = get_links(driver, url, "//a[@class='block-link__overlay-link']")
    save_to_file(links)

    for link in links:
        scrape(driver, *link)
    driver.close()


