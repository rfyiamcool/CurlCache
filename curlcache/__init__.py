#coding:utf-8

import os
import json
import logging
import glob
import base64
import urllib2

from datetime import datetime, timedelta

class QueryCache(object):

    def __init__(self, hours=0, days=0, minutes=10, seconds=0):
        self.alt_chars = '-_'
        self.cache_dir = ".cache"

        self.cache_length = timedelta(hours=hours, days=days, minutes=minutes,
                                      seconds=seconds)
        self.auto_invalidate_period = timedelta(minutes = 10)
        self.last_invalidation_time = None
        if self.cache_length < self.auto_invalidate_period:
            self.auto_invalidate_period = self.cache_length

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
        self.cache_meta = {}
        self.read_cache()
        self.auto_invalidate()

    def read_cache(self):
        for file in glob.glob(os.path.join(self.cache_dir, '*')):
            self._load_file_from_cache(file)

    def invalidate_old(self):
        now = datetime.now()
        self.last_invalidation_time = now
        updated_cache_meta ={}
        for item in self.cache_meta:
            then = self.cache_meta[item]['changed']
            logging.info("%s %s %s"% (now, then, self.cache_length))
            if (now - then) > self.cache_length:
                # Remove File
                os.remove(self.cache_meta[item]['location'])
            else:
                # Copy to new cache
                updated_cache_meta[item] = self.cache_meta[item]
        self.cache_meta = updated_cache_meta

    def auto_invalidate(self):
        now = datetime.now()
        if self.last_invalidation_time is None or \
                (now - self.last_invalidation_time) > self.auto_invalidate_period:
            self.invalidate_old()

    def json_query(self, url):
        if url not in self.cache_meta:
            self._query(url)
        return self._load_json(self.cache_meta[url])

    def _load_json(self, file):
        with open(file['location'], 'rb') as cached_file:
            return json.load(cached_file)

    def _query(self, url):
        b64 = base64.b64encode(url, self.alt_chars)
        output_location = os.path.join(self.cache_dir, b64)
        with open(output_location, 'wb') as fh:
            req = urllib2.Request(url)
            f = urllib2.urlopen(req)
            fh.write(f.read())
            f.close()

            self._load_file_from_cache(output_location)

    def _load_file_from_cache(self, file):
        url = base64.b64decode(os.path.split(file)[1], self.alt_chars)
        self.cache_meta[url] = {
            'location': file,
            'modified': datetime.fromtimestamp(os.path.getmtime(file)),
            'changed': datetime.fromtimestamp(os.path.getctime(file)),
        }

if __name__ == "__main__":
    pass
