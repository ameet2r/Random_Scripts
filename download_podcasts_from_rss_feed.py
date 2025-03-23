import xml.etree.ElementTree as ET
import requests
from tqdm import tqdm
import sys
import os
import time


def remove_special_chars(filename):
    new_filename = ""
    for char in filename:
        if char.isalnum() or char.isspace():
            new_filename += char

    return new_filename


def download_podcast(url, filename):
    response = requests.get(url, stream=True)

    if response.status_code == 200:
        total_size = int(response.headers.get("content-length", 0)) # Get file size
        block_size = 1024 # Download in 1KB chuncks
        with open(filename, "wb") as file, tqdm(
            desc=filename,
            total=total_size,
            unit="B",
            unit_scale=True,
            unit_divisor=block_size
        ) as bar:
            for chunk in response.iter_content(block_size):
                file.write(chunk)
                bar.update(len(chunk))
        print(f"{filename} downloaded successfully")
    else:
        print(f"{filename} failed to download. Status code: {response.status_code}")


def main(): 
    args = sys.argv[1:] 
    if len(args) == 0:
        print("Error no args given. Required arguments: download_location (where to download the podcast), xml_file (name of the rss feed for the podcast saved as a .xml file)")
        print("Example: python download_podcasts_from_rss_feed.py './anma_podcast' './anma.xml'")
        return

    download_location = args[0]
    xml_file = args[1]
    tree = ET.parse(xml_file)
    root = tree.getroot()
    channel = root.find("channel")

    if channel is not None:
        items = channel.findall("item")
        for item in items:
            title = item.find("title")
            pubDate = item.find("pubDate")
            url = item.find("enclosure")
            if (title is not None) and (pubDate is not None) and (url is not None):
                filename = f"{download_location}/{remove_special_chars(title.text)}.{remove_special_chars(pubDate.text)}.mp3"
                if os.path.exists(filename):
                    print(f"{filename} already exists, skipping download")
                else:
                    try:
                        time.sleep(1) # wait 1 second between calls, just in case
                        download_podcast(url.attrib["url"], filename)
                    except Exception as error:
                        print(f"Error downloading {filename}: {error}")
            

if __name__ == "__main__":
    main()
