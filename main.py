import requests
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import config
import chromedriver_autoinstaller

def setup_selenium():
    chromedriver_autoinstaller.install()  # Автоинсталлер для установки правильной версии chromedriver
    options = Options()
    options.headless = True  # Вот тут Запуск в режиме headless
    service = Service()
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def get_image_urls_from_yandex_folder(folder_url, driver):
    driver.get(folder_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    img_urls = []
    for img_tag in soup.find_all('img'):
        img_url = img_tag.get('src')
        if img_url and img_url.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            img_urls.append(img_url)
    return img_urls

def collect_images_from_urls(base_urls):
    driver = setup_selenium()
    images = []
    for base_url in base_urls:
        img_urls = get_image_urls_from_yandex_folder(base_url, driver)
        for img_url in img_urls:
            img_response = requests.get(img_url)
            if img_response.status_code == 200:
                img = Image.open(BytesIO(img_response.content)).convert("RGB")
                images.append(img)
    driver.quit()
    return images

def save_as_tiff(images, output_path):
    if images:
        images[0].save(output_path, save_all=True, append_images=images[1:], compression="tiff_deflate")

def main(output_file):
    images = collect_images_from_urls(config.URLS)
    save_as_tiff(images, output_file)
    print(f"Saved {len(images)} images to {output_file}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python main.py Result.tif")
        sys.exit(1)

    output_file = sys.argv[1]
    main(output_file)