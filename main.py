from webCrawler import WebCrawler
import sys

if __name__ == "__main__":
    webCrawler = WebCrawler()
    webCrawler.read_from_main_dir(sys.argv[1])