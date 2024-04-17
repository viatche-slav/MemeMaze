from src.constants import BAD_LINK
from bs4 import BeautifulSoup as bs
from requests import get


def parse(url):
    """
    Converts a URL to the website with images to the list of those images.

    :param url: link to the website
    :return: list with images
    """

    image_links = list()
    for element in bs(get(url).text, "html.parser").find_all("img"):
        link = element.get("src")
        if link[-4:] == ".png":
            if link == BAD_LINK:
                break
            image_links.append(link)
    return image_links
