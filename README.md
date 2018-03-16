# InstagramTagClawler

## Get Instagram posts by Tag with no authentication or login required.

A non API way (no authentication required) to get Instagram posts by Tag in dict, json or pandas DataFrame. Crawler and example included.

### Get the code
```
git clone https://github.com/karakatic/InstagramTagCrawler.git
```

### Commandline use
```
python instagramtagcrawler.py tag pages_to_crawl repeat_every_n_seconds
```

`pages_to_crawl` (default=1)
Indicates how many pages should be crawled. There are approximately 30 posts per page.

`repeat_every_n_seconds` (default=-1)
If you want to repeat crawling (for newer posts) every X seconds, use `repeat_every_n_seconds` argument.
- **-1** crawls only one time
- **any other integer** repeat crawls indefinitely every this amount of seconds

In every repeated crawl, the crawler will crawl `pages_to_crawl` pages. The posts will not repeat in the resulting file.

**Example use:**

Crawl for all posts with tag **#paris** for three most recent pages, and do not repeat this process.
```
python instagramtagcrawler.py paris 3
```

The information about tags will be saved in CSV format in the `{tag}.csv` file.

### Python library use

1. Import the library
```python
from instagramtagcrlawler import Post, InstagramTagCrawler
```

2. Initialize the tag crawler
```python
crawler = InstagramTagCrawler(tag='paris')
```

3. Get the list of all posts
```python
posts = crawler.get_posts()
```

We can specify number of pages that crawler crawls (default=1)
```python
posts = crawler.get_posts(pages=3)
```

4. Use the list of posts
```python
for post in posts:
    caption = post.caption
    print(post)

    dict_post = post.to_dict() # Get the dictionary of this post
    tags_in_post = post.get_tags() # Get the list of all tags in this post
```

Or get the pandas DataFrame of all crawled posts
```python
from instagramtagcrlawler import InstagramTagCrawler

crawler = InstagramTagCrawler(tag='pandas')
posts = crawler.get_posts()

df = crawler.to_pandas(posts)
```