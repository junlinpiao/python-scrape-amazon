import bs4
import os
import xlsxwriter
from time import sleep
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def download_image(image_url, img_path):
    resource = urlopen(image_url)
    output = open(img_path, 'wb')
    output.write(resource.read())
    output.close()

def get_img_dir():
    base_dir = ".//images"
    if not os.path.isdir(base_dir):
        os.mkdir(base_dir)
    dir_num = 1
    img_dir = base_dir + "//{}".format(dir_num)
    while os.path.isdir(img_dir):
        dir_num += 1
        img_dir = base_dir + "//{}".format(dir_num)
    os.mkdir(img_dir)
    return img_dir

def get_res_filename():
    file_num = 1
    filename = "result{}.xlsx".format(file_num)
    while os.path.isfile(filename):
        file_num += 1
        filename = "result{}.xlsx".format(file_num)
    return filename

def scrape_amazon(browser, worksheet, url):
    base_url = "https://www.amazon.com"
    browser.get(url)

    soup = bs4.BeautifulSoup(browser.page_source, "html.parser")
    # get page count
    page_count = 1
    page_num_lis = soup.select("ul.a-pagination li")
    if len(page_num_lis) > 1:
        page_count = page_num_lis[-2].get_text().strip()
        page_count = int(page_count)
    print ("{} Pages Found.".format(page_count))

    row = 0
    image_dir = get_img_dir()
    for i in range(page_count):
        cur_page_url = "{}&page={}".format(url, i+1)
        print ("Loading Page {} ...".format(i+1))
        browser.get(cur_page_url)
        soup = bs4.BeautifulSoup(browser.page_source, "html.parser")
        products = soup.select("div.s-result-list>div.s-result-item")
        print ("Extracting products from Page {} ...".format(i+1))
        for product in products:
            product_name = ""
            product_price = ""
            product_img_url = ""
            product_img_filename = ""
            product_name_div = product.select("div.sg-col-inner h2 a")
            if len(product_name_div) == 0:
                continue
            product_name = product_name_div[0].get_text().strip()
            product_img_tag = product.select("img")
            if len(product_img_tag) > 0:
                product_img_url = product_img_tag[0]['src'].strip()
                product_img_filename = product_img_url.split('/')[-1]
            product_price_whole = product.select("span.a-price-whole")
            if len(product_price_whole)>0:
                product_price_symbol = product.select("span.a-price-symbol")
                product_price_symbol = product_price_symbol[0].get_text().strip()
                product_price_fraction = product.select("span.a-price-fraction")
                product_price_fraction = product_price_fraction[0].get_text().strip()
                product_price_whole = product_price_whole[0].get_text().strip()
                product_price = "{}{}{}".format(product_price_symbol, product_price_whole, product_price_fraction)
            worksheet.write(row, 0, product_name)
            worksheet.write(row, 1, product_price)
            worksheet.write(row, 2, product_img_url)
            worksheet.write(row, 3, image_dir+"//"+product_img_filename)
            row += 1
            if product_img_filename != "":
                image_path = image_dir+"//"+product_img_filename
                download_image(product_img_url, image_path)
            print ("Extracted: {}".format(product_name))

def scrape_walmart(browser, worksheet, url):
    base_url = "https://www.walmart.com"
    # url = "https://www.walmart.com/browse/all-apple-ipad/0/0/?_refineresult=true&amp%3B_be_shelf_id=7780&amp%3Bfacet=shelf_id%3A7780&amp%3BredirectQuery=ipad&amp%3Bsearch_redirect=true&amp%3Bsearch_sort=100&page=3"
    browser.get(url)

    soup = bs4.BeautifulSoup(browser.page_source, "html.parser")
    # get page count
    page_count = 1
    page_num_lis = soup.select("ul.paginator-list li")
    if len(page_num_lis) > 1:
        page_count = page_num_lis[-1].get_text().strip()
        page_count = int(page_count)
    print ("{} Pages Found.".format(page_count))

    row = 0
    image_dir = get_img_dir()
    for i in range(page_count):
        cur_page_url = "{}&page={}".format(url, i+1)
        print ("Loading Page {} ...".format(i+1))
        browser.get(cur_page_url)
        soup = bs4.BeautifulSoup(browser.page_source, "html.parser")
        products = soup.select("div.search-product-result>ul>li")
        print ("Extracting products from Page {} ...".format(i+1))
        for product in products:
            product_name = ""
            product_price = ""
            product_img_url = ""
            product_img_filename = ""
            product_name_div = product.select(".product-title-link span")
            if len(product_name_div) == 0:
                continue
            product_name = product_name_div[0].get_text().strip()
            product_img_tag = product.select("img")
            if len(product_img_tag) > 0:
                product_img_url = product_img_tag[0]['src'].strip()
                product_img_filename = product_img_url.split('/')[-1].split('?')[0]
            product_price_whole = product.select("span.price-group")
            if len(product_price_whole)>0:
                product_price = product_price_whole[0].get_text().strip()
                
            worksheet.write(row, 0, product_name)
            worksheet.write(row, 1, product_price)
            worksheet.write(row, 2, product_img_url)
            worksheet.write(row, 3, image_dir+"//"+product_img_filename)
            row += 1
            if product_img_filename != "":
                image_path = image_dir+"//"+product_img_filename
                download_image(product_img_url, image_path)
            print ("Extracted: {}".format(product_name))

def main():
    browser = None
    try:
        # url = "https://www.amazon.com/s?k=face+shield&ref=nb_sb_noss_1"
        url=input("Enter Searched Products Url: ")
        if not "amazon.com" in url and not "walmart.com" in url:
            print ("Amazon and Walmart are only supported.")
            return
        tmplist1 = url.split("?")
        tmplist = []
        if len(tmplist1) > 1:
            tmplist = tmplist1[1].split("&")
        for tmp in tmplist:
            if "page=" in tmp:
                if "&{}".format(tmp) in url:
                    url = url.replace("&{}".format(tmp), "")
                elif "{}&".format(tmp) in url:
                    url = url.replace("{}&".format(tmp), "")
                else:
                    url = url.replace(tmp, "")
                break

        # open chrome driver
        print ("Opening Selenium Chrome driver...")
        driver_path = os.path.join(os.getcwd(), 'chromedriver')
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--no-sandbox')
        # browser = webdriver.Chrome(driver_path)
        browser = webdriver.Chrome(driver_path, options=chrome_options)
        print ("Loading...")

        # open xlsx file
        result_filename = get_res_filename()
        workbook = xlsxwriter.Workbook(result_filename)
        worksheet = workbook.add_worksheet()
        worksheet.write(0, 0, "Product Name")
        worksheet.write(0, 1, "Price")
        worksheet.write(0, 2, "Image URL")
        worksheet.write(0, 3, "Image file name")

        if "amazon.com" in url:
            scrape_amazon(browser, worksheet, url)
        elif "walmart.com" in url:
            scrape_walmart(browser, worksheet, url)
        
        workbook.close()
        browser.close()
        print ("Extracting Finished Successfully!")
    except:
        if browser:
            browser.close()
        print ("Error!")

if __name__ == "__main__":
    main()