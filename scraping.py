#!/usr/bin/env python
# coding: utf-8
# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

def scrape_all():
    # Initiate headless driver for deployment
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)
    img_urls_titles = scrap_mars_Hemispheres_images_title(browser)
    featured_images = featured_image(browser)
    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_images,
        "facts": mars_facts(),
        'hemispheres' : img_urls_titles,
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data

# ### Visit the NASA Mars News Site
def mars_news(browser):
    url = 'https://redplanetscience.com/'
    browser.visit(url)

    browser.is_element_present_by_css('div.list_text', wait_time=1)

    html = browser.html
    news_soup = soup(html, 'html.parser')

    try:
        slide_elem = news_soup.select_one('div.list_text')
        news_title = slide_elem.find('div', class_='content_title').get_text()
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    browser.back()
    return news_title, news_p

# ### JPL Space Images Featured Image
def featured_image(browser):
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    except AttributeError:
        return None 

    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html()

# # D1: Scrape High-Resolution Mars’ Hemisphere Images and Titles
# ### Hemispheres
def scrap_mars_Hemispheres_images_title(browser):
    url = 'https://marshemispheres.com/'
    browser.visit(url)
    html = browser.html
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.
    for i in range(4):
        browser.links.find_by_partial_text('Hemisphere Enhanced')[i].click()
        html2 = browser.html
        soup2 = soup(html2,'html.parser')
        title = soup2.find('h2', class_='title').text
        img_url = soup2.find('li').a.get('href')
        images = {}
        images['img_url'] = f'https://marshemispheres.com/{img_url}'
        images['title'] = title
        hemisphere_image_urls.append(images)
        browser.back()

    browser.quit()
    return hemisphere_image_urls

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())

