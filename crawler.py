import logging
import os
import re
from lxml import etree
from urllib.parse import urlparse, urljoin, parse_qs
from corpus import Corpus
import queue
from collections import defaultdict

logger = logging.getLogger(__name__)


class Crawler:
    """
    This class is responsible for scraping urls from the next available link in frontier and adding the scraped links to
    the frontier
    """

    def __init__(self, frontier):
        self.frontier = frontier
        self.corpus = Corpus()
        self.all_urls = set()

        self.url_queue = queue.Queue(maxsize=150)
        self.url_dict = dict()

        self.url_traps = []

    def make_analytics(self):
        file = open("analytics.txt", "w+")

        ## Analytics #1
        ## Keep track of the subdomains that it visited, and count how many different URLs it has processed from each of those subdomains

        ## Citation: https://stackoverflow.com/questions/6925825/get-subdomain-from-url-using-python
        ## This was helpful in extracting the subdomains

        subdomain_dict = defaultdict(int)
        for url in self.url_dict.keys():

            url_to = urlparse(url)
            subdomain = url_to.hostname.split('.')[0]
            subdomain_dict[subdomain] += 1

        file.write("Analytics #1 - Subdomains visted and how many different urls processed from these subdomains: "
                   "\n ")
        for sub,count in subdomain_dict.items():
            file.write(str(sub) +":\t" + str(count) + "\n")

        file.write("\n \n")

        ## Analytics #2
        ## Find the page with the most valid out links (of all pages given to your crawler). Out Links are the number of links that are present on a particular webpage.
        max_key = max(self.url_dict, key=self.url_dict.get)
        max_value = self.url_dict[max_key]
        file.write("Analytics #2 - The page with the most valid out links: \t " + max_key + " with " + str(
            max_value) + " out links \n\n")

        ## Analytics #3
        ## List of downloaded URLs and identified traps.

        file.write("Analytics #3 - List of downloaded URLs and identified traps \n\n")

        file.write("LIST OF DOWNLOADED URLs \n")
        file.write("======================================= \n")

        for valid_url in self.url_dict:
            file.write(valid_url + "\n")

        ## print(len(self.url_dict))
        file.write("\nLIST OF IDENTIFIED TRAPS \n")
        file.write("======================================= \n")

        for trap in self.url_traps:
            file.write(trap + "\n")

        file.close()

    def start_crawling(self):
        """
        This method starts the crawling process which is scraping urls from the next available link in frontier and adding
        the scraped links to the frontier
        """
        perform = False
        while self.frontier.has_next_url():
            perform = True
            url = self.frontier.get_next_url()
            logger.info("Fetching URL %s ... Fetched: %s, Queue size: %s", url, self.frontier.fetched,
                        len(self.frontier))
            url_data = self.fetch_url(url)

            ##print(url_data)
            count = 0
            for next_link in self.extract_next_links(url_data):
                if self.corpus.get_file_name(next_link) is not None:
                    if self.is_valid(next_link):
                        count += 1  ## This line can be used to gather most # of valid outlinks for Analytics #2
                        self.frontier.add_url(next_link)

            if url in self.url_dict:
                self.url_dict[url] += count
            else:
                self.url_dict[url] = count

        if perform:
            self.make_analytics()


    def fetch_url(self, url):
        """
        This method, using the given url, should find the corresponding file in the corpus and return a dictionary
        containing the url, content of the file in binary format and the content size in bytes
        :param url: the url to be fetched
        :return: a dictionary containing the url, content and the size of the content. If the url does not
        exist in the corpus, a dictionary with content set to None and size set to 0 can be returned.
        """

        file_name = self.corpus.get_file_name(url)  # looks up file name of url

        # create a dict which will have url info
        url_data = {'url': url, 'content': None, 'size': 0}
        try:

            with open(file_name,
                      'rb') as fobj:  # read and open file. if file can be opened, add in url, contents, and size of the file.
                xml = fobj.read()

            url_data['url'] = url
            url_data['content'] = xml
            url_data['size'] = os.path.getsize(file_name)

        except:  # if file can't be opened, print error
            print("file error")

        return url_data  # return dict of info

    def extract_next_links(self, url_data):
        """
         The url_data coming from the fetch_url method will be given as a parameter to this method. url_data contains the
         fetched url, the url content in binary format, and the size of the content in bytes. This method should return a
         list of urls in their absolute form (some links in the content are relative and needs to be converted to the
         absolute form). Validation of links is done later via is_valid method. It is not required to remove duplicates
         that have already been fetched. The frontier takes care of that.

         Suggested library: lxml
         """
        outputLinks = []
        root = etree.HTML(url_data['content'])  # creates an html object of the contents of the given url dict
        links = root.xpath(
            "//@href")  # extract all links with type "href" into a list of links. every url link will be preceded with 'href'

        for link in links:
            new_url = urljoin(url_data['url'],
                              link)  # constructs an absolute url by combining the original url info with scraped url links.
            ##print(new_url)
            if new_url not in self.frontier.urls_set:  # if this absolute url is new, then add it to the list, otherwise just continue.
                outputLinks.append(new_url)
                ## print(new_url)
            else:
                continue
                # return final list of all absolute links.
        return outputLinks

    def is_valid(self, url):
        """
        Function returns True or False based on whether the url has to be fetched or not. This is a great place to
        filter out crawler traps. Duplicated urls will be taken care of by frontier. You don't need to check for duplication
        in this method

        Helpful sources: https://www.contentkingapp.com/academy/crawler-traps/,
        https://www.portent.com/blog/seo/field-guide-to-spider-traps-an-seo-companion.htm,
        https://support.archive-it.org/hc/en-us/articles/208332943-Identify-and-avoid-crawler-traps-
        """
        parsed = urlparse(url)

        ## Look out for: long messy strings, repeating/extra directories,
        ## long line of urls that are similar/go to same page, same links but diff w/ http and https

        if parsed.scheme not in set(["http", "https"]):
            return False
        try:

            #### Handle URL Length ####
            if len(url) > 150:
                self.url_traps.append(url)
                return False

            #### Handle Repeating Dictionaries ####
            directory_dict = dict()
            for directory in parsed.path.split("/"):
                if directory in directory_dict:
                    directory_dict[directory] += 1

                    if directory_dict[directory] > 4:
                        self.url_traps.append(url)
                        return False
                else:
                    directory_dict[directory] = 0

            #### Handling URLs that are generated seemingly indefinitely ####

            url_without_params = parsed.netloc + parsed.path
            if len(parsed.query) == 0:
                url_without_params = url_without_params + "NO?"

            if (self.url_queue.full()):
                self.url_queue.get()

            self.url_queue.put(url_without_params)

            queue_list = list(self.url_queue.queue)     ## we place the recent 150 links in a queue and check if there 
            queue_list1 = queue_list[-60:]              ## are similar links, or links that may go to the same page

            count = 0

            for i in queue_list1:
                if i == url_without_params:
                    count += 1

            if count > 35:
                self.url_traps.append(url)
                return False

            #### Handle HTTP/HTTPS links ####
            modified_url = ""
            if parsed.scheme == "http":
                modified_url = url[4:]
            if parsed.scheme == "https":
                modified_url = url[5:]

            if modified_url in self.all_urls:
                return False
            else:
                self.all_urls.add(modified_url)

            return ".ics.uci.edu" in parsed.hostname \
                   and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4" \
                                    + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
                                    + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
                                    + "|thmx|mso|arff|rtf|jar|csv" \
                                    + "|rm|smil|wmv|swf|wma|zip|rar|gz|pdf)$", parsed.path.lower())

        except TypeError:
            print("TypeError for ", parsed)
            return False

