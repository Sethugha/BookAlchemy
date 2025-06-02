import requests
import wikipedia
import shutil
from flask import Flask,render_template, request, jsonify, redirect, url_for
from urllib.parse import quote

def retrieve_entity_via_wikipedia(search_term, imgpath):
    """
    Uses wikipedia to retrieve the wiki page of the <search_term>.
    extracts the summary and image urls. This imge-url is requested afterwards
    returning the first image ending with 'jpg'
    :param search_term: any search string, one or more words
    :param imgpath: relative path of the image file, adapted to the purpose of the search.
                    author portraits are saved as /static/images/portraits/{author.id}.jpg
                    books as /static/images/{book.isbn}.jpg
    :return: page summary, str
    """
    page = wikipedia.page(search_term)
    summary = page.summary
    image_url_list = page.images
    for img_url in image_url_list:
        if img_url.endswith('jpg'):
            img_response = requests.get(img_url)
            if img_response.status_code == 200:
                with open(imgpath, 'wb') as imgfile:
                    imgfile.write(img_response.content)
    return summary

def file_convert_csv_to_json(text):
    pass




def retrieve_entity_via_openlib(search_term):
    base_url = ("https://openlibrary.org/search/authors?q="
                + search_term.replace(' ', '+')
                + '&mode=everything')
    openLib = requests.get(base_url)
    if openLib.status_code == 200:
        return openLib.content


def backup_database(filepath):
    """function to create a copy of the database file
    using shutil
    return:
    """
    destination = filepath[:-2]+'sik'
    shutil.copyfile(filepath, destination)
    return destination


def main():
    pass

if __name__ == '__main__':
    main()
