"""
Main Docstring

TODO: Implement logging. Use a style consistent with stream.py.

"""


import httplib
import json
import os
import Queue
import socket
import threading
import urllib
import urlparse

import pymongo
import redis


# Define user name.
qactweet = os.getlogin()

# Import the stream parameters associated with this user account.
with open('/home/twitter-data/docs/parameters.json') as f:
    par = json.loads(f.read())[qactweet]

# Connect to MongoDB.
conn = pymongo.Connection(par['server_name'])
db = getattr(conn, par['database_name'])

# Connect to Redis.
r = redis.StrictRedis()


def unshorten(url):
    """Unshortens a URL, if possible.
    
    Sends a header request for a given URL, and returns the target location
    (if the URL is redirected) or the URL (if it is not redirected).
    
    Args:
        url: A string URL, including the scheme (usually http).
    
    Returns:
        If the URL is redirected, the target URL.
        If the URL is not redirected, the URL.
        In the case of an error, None.
    """ 
    try:
        parsed = urlparse.urlparse(url)
        h = httplib.HTTPConnection(parsed.netloc)
        h.request('HEAD', parsed.path)
        response = h.getresponse()
        if response.status / 100 == 3 and response.getheader('Location'):
            return response.getheader('Location')
        else:
            return url
    except httplib.HTTPException as e:
        return


class ThreadUrl(threading.Thread):
    """A threaded worker instance that parses URLs.
    
    Accepts dictionaries of the form {_id : ... , url : ...} from the populated
    queue. Expands each received URL, broadcasting to the ``youtube'' channel
    if the URL links to YouTube. Writes the Tweet ID and URLs to MongoDB.
    """
    
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
    
    def run(self):
        while True:
            # Get URL from queue.
            msg = self.queue.get()
            
            # Set up two lists: one for all URLs in the Tweet, and one for all
            # URLs in the Tweet that link to YouTube.
            urls = []
            youtube_urls = []
            
            # Parse URLs.
            for url in msg['urls']:
                # Unshorten URL and add it to the URLs list.
                try:
                    url = unshorten(url['expanded_url'])
                    urls.append(url)
                except (AttributeError, socket.error):
                    # AttributeError: unshorten() encountered HTTPException.
                    # socket.error: Connection refused.
                    continue
                # Parse the URL. If it links to YouTube, add it to the YouTube
                # URLs list. If it contains a link to a video (i.e., has the
                # 'v' URL query parameter), the video ID to Redis.
                try:
                    parsed = urlparse.urlparse(url)
                except AttributeError:
                    # URL parses to None.
                    continue
                if parsed.netloc == 'www.youtube.com':
                    youtube_urls.append(url)
                    try:
                        video_id = urlparse.parse_qs(parsed.query)['v'][0]
                        r.rpush('%s_video_ids' % par['database_name'], video_id)
                    except KeyError:
                        # Generic YouTube link without video ID.
                        continue
            
            # Insert the URL data into the database.
            try:
                doc = {'_id' : msg['_id'], 'urls' : urls}
                db.urls.insert(doc, safe=True)
            except pymongo.errors.DuplicateKeyError:
                # Document is already in the database.
                pass
            if youtube_urls:
                try:
                    doc = {'_id' : msg['_id'], 'urls' : youtube_urls}
                    db.youtube_urls.insert(doc, safe = True)
                except pymongo.errors.DuplicateKeyError:
                    # Document is already in the database.
                    pass

def main():
    
    # Define queue.
    queue = Queue.Queue()
    
    # Spawn a pool of threads, and pass a queue instance to each.
    for i in range(20):
        t = ThreadUrl(queue)
        t.setDaemon(True)
        t.start()
    
    while True:
        # This scales across multiple hosts because when they all block for
        # the same key, they are put in a FIFO queue.
        msg = eval(r.blpop('%s_urls' % par['database_name'])[1])
        queue.put(msg)
     
    # Shut down.
    queue.join()  # Blocks until all items in the queue have been processed.
    conn.disconnect()


if __name__ == '__main__':
    
    main()


