import os
import os.path as osp
from multiprocessing import Pool
import argparse
from collect_links import CollectLinks
import imghdr
import random
import json


class Sites:
    GOOGLE = 1
    GOOGLE_FULL = 3

    @staticmethod
    def get_text(code):
        if code == Sites.GOOGLE:
            return 'google'
        elif code == Sites.GOOGLE_FULL:
            return 'google'

    @staticmethod
    def get_face_url(code):
        if code == Sites.GOOGLE or Sites.GOOGLE_FULL:
            return "&tbs=itp:face"


class AutoCrawler:
    def __init__(self, skip_already_exist=True, n_threads=4, do_google=True, download_path='collected_links',
                 face=False, no_gui=False, limit=0, proxy_list=None, print_url=False):
        """
        :param skip_already_exist: Skips keyword already downloaded before. This is needed when re-downloading.
        :param n_threads: Number of threads to download.
        :param do_google: Download from google.com (boolean)
        :param download_path: Download folder path
        :param face: Face search mode
        :param no_gui: No GUI mode. Acceleration for full_resolution mode.
        :param limit: Maximum count of images to download. (0: infinite)
        :param proxy_list: The proxy list. Every thread will randomly choose one from the list.
        """

        self.skip = skip_already_exist
        self.n_threads = n_threads
        self.do_google = do_google
        self.download_path = download_path
        self.full_resolution = True
        self.face = face
        self.no_gui = no_gui
        self.limit = limit
        self.proxy_list = proxy_list if proxy_list and len(proxy_list) > 0 else None
        self.print_url = print_url

        os.makedirs('./{}'.format(self.download_path), exist_ok=True)

    @staticmethod
    def all_dirs(path):
        paths = []
        for dir in os.listdir(path):
            if os.path.isdir(path + '/' + dir):
                paths.append(path + '/' + dir)

        return paths

    @staticmethod
    def all_files(path):
        paths = []
        for root, dirs, files in os.walk(path):
            for file in files:
                if os.path.isfile(path + '/' + file):
                    paths.append(path + '/' + file)

        return paths

    @staticmethod
    def get_extension_from_link(link, default='jpg'):
        splits = str(link).split('.')
        if len(splits) == 0:
            return default
        ext = splits[-1].lower()
        if ext == 'jpg' or ext == 'jpeg':
            return 'jpg'
        elif ext == 'gif':
            return 'gif'
        elif ext == 'png':
            return 'png'
        else:
            return default

    @staticmethod
    def validate_image(path):
        ext = imghdr.what(path)
        if ext == 'jpeg':
            ext = 'jpg'
        return ext  # returns None if not valid

    @staticmethod
    def make_dir(dirname):
        current_path = os.getcwd()
        path = os.path.join(current_path, dirname)
        if not os.path.exists(path):
            os.makedirs(path)

    @staticmethod
    def get_keywords(keywords_file='keywords_collect/name_meta.json'):
        with open(keywords_file, 'r', encoding='utf-8-sig') as f:
            name_meta = json.load(f)
        
        keywords = []
        for k, v in name_meta.items():
            name_t = v["name"]
            if osp.exists(osp.join("./collected_links", name_t+".txt")):
                continue
            keywords.append(name_t)

        print('{} keywords found: {}'.format(len(keywords), keywords))

        # re-save sorted keywords

        return keywords

    def download_from_site(self, keyword, site_code):
        site_name = Sites.get_text(site_code)
        add_url = Sites.get_face_url(site_code) if self.face else ""

        try:
            proxy = None
            if self.proxy_list:
                proxy = random.choice(self.proxy_list)
            collect = CollectLinks(no_gui=self.no_gui, proxy=proxy, print_url=self.print_url)  # initialize chrome driver
        except Exception as e:
            print('Error occurred while initializing chromedriver - {}'.format(e))
            return

        try:
            print('Collecting links... {} from {}'.format(keyword, site_name))

            if site_code == Sites.GOOGLE_FULL:
                links = collect.google_full(keyword, add_url)
            else:
                print('Invalid Site Code')
                links = []

            print('Downloading images from collected links... {} from {}'.format(keyword, site_name))

            print('Done {} : {}'.format(site_name, keyword))

        except Exception as e:
            print('Exception {}:{} - {}'.format(site_name, keyword, e))

    def download(self, args):
        self.download_from_site(keyword=args[0], site_code=args[1])

    def do_crawling(self):
        keywords = self.get_keywords()

        tasks = []

        for keyword in keywords:
            dir_name = '{}/{}'.format(self.download_path, keyword)
            google_done = os.path.exists(os.path.join(os.getcwd(), dir_name, 'google_done'))
            if google_done and self.skip:
                print('Skipping done task {}'.format(dir_name))
                continue

            if self.do_google and not google_done:
                if self.full_resolution:
                    tasks.append([keyword, Sites.GOOGLE_FULL])
                else:
                    tasks.append([keyword, Sites.GOOGLE])

        pool = Pool(self.n_threads)
        pool.map_async(self.download, tasks)
        pool.close()
        pool.join()
        print('Task ended. Pool join.')

        print('End Program')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--skip', type=str, default='true',
                        help='Skips keyword already downloaded before. This is needed when re-downloading.')
    parser.add_argument('--threads', type=int, default=4, help='Number of threads to download.')
    parser.add_argument('--face', type=str, default='false', help='Face search mode')
    parser.add_argument('--no_gui', type=str, default='auto',
                        help='No GUI mode. Acceleration for full_resolution mode. '
                             'But unstable on thumbnail mode. '
                             'Default: "auto" - false if full=false, true if full=true')
    parser.add_argument('--limit', type=int, default=0,
                        help='Maximum count of images to download per site. (0: infinite)')
    parser.add_argument('--proxy-list', type=str, default='',
                        help='The comma separated proxy list like: "socks://127.0.0.1:1080,http://127.0.0.1:1081". '
                             'Every thread will randomly choose one from the list.')
    parser.add_argument('--print_url', action='store_true')
    args = parser.parse_args()

    _skip = False if str(args.skip).lower() == 'false' else True
    _threads = args.threads
    _face = False if str(args.face).lower() == 'false' else True
    _limit = int(args.limit)
    _proxy_list = args.proxy_list.split(',')
    _print_url = args.print_url

    no_gui_input = str(args.no_gui).lower()
    if no_gui_input in ['auto' or 'true']:
        _no_gui = True
    else:
        _no_gui = False

    print(
        'Options - skip:{}, threads:{}, face:{}, no_gui:{}, limit:{}, _proxy_list:{}'
            .format(_skip, _threads, _face, _no_gui, _limit, _proxy_list))

    crawler = AutoCrawler(skip_already_exist=_skip, n_threads=_threads,
                          face=_face, no_gui=_no_gui, limit=_limit, proxy_list=_proxy_list, print_url=_print_url)
    crawler.do_crawling()
