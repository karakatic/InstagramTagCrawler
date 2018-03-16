import requests
import json
import pandas as pd
from io import StringIO
import sys
import time
import datetime


class Post(object):
    header = 'id,code,timestamp,owner_id,liked,commented,display_url,caption'

    @staticmethod
    def escape(string):
        return string.encode("unicode_escape").decode("utf-8")

    def __init__(self, node):
        n = node.get('node', None)
        self.id = n.get('id', None)
        self.timestamp = n.get('taken_at_timestamp', None)
        self.display_url = n.get('display_url', None)
        self.liked = n.get('edge_liked_by', None).get('count', 0)
        self.commented = n.get('edge_media_to_comment', None).get('count', 0)
        self.owner_id = n.get('owner', None).get('id', None)
        self.code = n.get('shortcode', None)

        caption_tmp = n.get('edge_media_to_caption', None).get('edges', None)
        self.caption = caption_tmp[0].get('node', None).get('text', '')

    def get_tags(self):
        return {self.caption.strip("#") for tag in self.caption.split() if tag.startswith("#")}

    def to_dict(self):
        return {'id': self.id,
                'code': self.code,
                'timestamp': self.timestamp,
                'owner_id': self.owner_id,
                'linked': self.liked,
                'commented': self.commented,
                'display_url': self.display_url,
                'caption': Post.escape(self.caption)
                }

    def to_pandas(self):
        return pd.read_csv(StringIO(Post.header + '\n' + str(self)), index_col=0)

    def to_csv(self):
        return ','.join((self.id,
                         self.code,
                         str(self.timestamp),
                         self.owner_id,
                         str(self.liked),
                         str(self.commented),
                         '\"' + self.display_url + '\"',
                         '\"' + Post.escape(self.caption) + '\"'))

    def __str__(self):
        return self.to_csv()


class InstagramTagCrawler(object):
    base_url = 'https://www.instagram.com/explore/tags/'

    @staticmethod
    def print_json(data_dict):
        print(json.dumps(data_dict, indent=4))

    @staticmethod
    def to_pandas(all_posts):
        df0 = None
        for p in all_posts:
            df1 = p.to_pandas()

            if df0 is None:
                df0 = df1
            else:
                df0 = pd.concat([df0, df1], axis=0)

        df0 = df0[~df0.index.duplicated(keep='last')]

        return df0

    def __init__(self, tag, pages=1, verbose=False):
        self.tag = tag
        self.verbose = verbose
        self.url = InstagramTagCrawler.base_url + self.tag + '/?__a=1'

    def get_ig_page(self, max_id=None):
        self.url = InstagramTagCrawler.base_url + self.tag + '/?__a=1'
        if max_id is not None:
            self.url = self.url + '&max_id=' + max_id

        if self.verbose:
            print('GET:', self.url, end='')

        session = requests.Session()
        r = session.get(self.url)

        if self.verbose:
            print(r.status_code, end='')

        if r.status_code == requests.codes.ok:
            return r
        else:
            return None

    def get_posts(self, pages=1):
        max_id = None
        resulting_posts = []

        for i in range(pages):
            try:
                ig_data_dict = self.get_ig_page(max_id)

                if self.verbose:
                    print(ig_data_dict)

                res = ig_data_dict.json()
                data = res.get('graphql', None).get('hashtag', None)

                l_posts = data.get('edge_hashtag_to_media', None).get('edges', None)  # .get('node', None)
                for post in l_posts:
                    resulting_posts.append(Post(post))

                page_info = data.get('edge_hashtag_to_media', None).get('page_info', None)
                max_id = page_info.get('end_cursor', None)
                if max_id is None:
                    return resulting_posts
            except:
                break

        return resulting_posts


if __name__ == "__main__":
    args = sys.argv
    tag = ''
    pages = 1
    repeat_sec = -1

    if len(args) < 2:
        print('Instagram Tag Crawler command line use instructions.\n'
              'Three arguments should be specified in the following order:\n'
              '1. tag to crawl\n'
              '2. number of pages to crawl (default=1)\n'
              '3. number of seconds between repeated crawls (for continuous crawl).\n'
              '    -1 (default) = do not repeat'
              '    any other integer = repeat crawls indefinitely every this amount of seconds\n\n'
              'Example uses:\n'
              'python instagramtagcrawler.py paris 3\n'
              'python instagramtagcrawler.py paris 1 3600\n')
    else:
        tag = args[1]
        if len(args) > 2:
            pages = int(args[2])
        if len(args) == 4:
            repeat_sec = int(args[3])

        print('Starting Instagram tag crawler for tag #%s on %d pages' % (tag, pages), end=' ')
        if repeat_sec == -1:
            print('without repeating.')
        else:
            print('repeating it every %d seconds. Break the crawler with CTRL+C.' % repeat_sec)

        print('Results are saved in the file ./tags/%s.csv' % tag)

        crawler = InstagramTagCrawler(tag)
        df = None

        while True:
            print('Crawling (', datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'), ')...',
                  end=' ')

            posts = crawler.get_posts(pages=pages)
            df1 = InstagramTagCrawler.to_pandas(posts)

            if df is None:
                df = df1
            else:
                df = pd.concat([df, df1], axis=0)
                df = df[~df.index.duplicated(keep='last')]

            df.to_csv('./tags/' + tag + '.csv')
            print('FINISHED')

            if repeat_sec != -1:
                time.sleep(repeat_sec)
            else:
                break
