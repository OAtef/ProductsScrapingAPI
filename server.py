from flask import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import re

app = Flask(__name__)

@app.route("/scrape", methods=['POST'])
def scrape():
    requestedData = []
    if (request.data):
        userData = request.get_json()
        print(userData)
        link = userData["Links"][0]
        nameInput = userData["Keyword"]
        nameInput = nameInput.rstrip()
        depth = userData["Depth"]

        options = Options()
        options.add_argument('headless')

        driver = webdriver.Chrome(chrome_options=options)

        nextPageExists = True
        parentDivClassName = None

        while nextPageExists:
            driver.get(link)
            time.sleep(1)
            if parentDivClassName is None:
                itemTag = driver.find_elements_by_xpath("//*[contains(text(),'" + nameInput + "')]")
                for item in itemTag:
                    if item.tag_name != "script" and item.tag_name != "noscript":
                        parentDiv = item.find_elements_by_xpath(".//ancestor::div")
                        # if len(parentDiv) < 1 no data to be extracted
                        # if class value = None find id value / if nothing found = no data can be extracted
                        if depth is "1":
                            parentDivClassName = parentDiv[0].get_attribute("class")
                            print(parentDivClassName)
                        elif depth is "2":
                            half = len(parentDiv)//2
                            parentDivClassName = parentDiv[half].get_attribute("class")
                        elif depth is "3":
                            parentDivClassName = parentDiv[-1].get_attribute("class")

            allDivs = driver.find_elements_by_xpath("//div[@class='" + parentDivClassName + "']")

            tempText = ""
            for div in allDivs:
                childItems = div.find_elements_by_xpath(".//*")
                for child in childItems:
                    text = child.text
                    # add validation on child.text to not be in unwantedstrings list
                    if len(child.text) > 1 and text != tempText:
                        tempText = text
                        # if text contains $ loop on each char if integer create new string append it else append text
                        if "$" in text:
                            price = re.search(r"(?:[\£\$\€]{1}[,\d]+.?\d*)", text)
                            requestedData.append({'ExtractedData': price.group()})
                        else:
                            requestedData.append({'ExtractedData': text})

            try:
                nextPage = driver.find_element_by_xpath(
                    "//div[contains(@class,'pagination') or contains(@id,'pagination')]//a[contains(@class,'ext') or contains(text(),'ext')]")
                nextPageExists = True
                link = nextPage.get_attribute("href")
            except:
                nextPageExists = False

        driver.quit()
        # return jsonify({'ExtractedData': requestedData})
        return jsonify(tuple(requestedData))


if __name__ == "__main__":
    app.run(debug=True)