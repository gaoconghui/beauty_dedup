#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import print_function

import ctypes
import errno
import os
import pickle
import random
import sys
import time

import requests

from db import Image

DEFAULT_PHASH = "00000000000000000000"


class pHash(object):
    def __init__(self):
        self._lib = ctypes.CDLL('/opt/local/lib/libpHash.dylib', use_errno=True)

    def dct_imagehash_async(self, path):
        r, w = os.pipe()
        pid = os.fork()
        if not pid:
            with os.fdopen(w, 'wb') as dst:
                pickle.dump(self.dct_imagehash(path), dst)
            os._exit(0)  # so "finally" clauses won't get triggered
        else:
            os.close(w)
            return r, pid

    def dct_imagehash(self, path):
        phash = ctypes.c_uint64()
        if self._lib.ph_dct_imagehash(path, ctypes.pointer(phash)):
            errno_ = ctypes.get_errno()
            err, err_msg = (errno.errorcode[errno_], os.strerror(errno_)) \
                if errno_ else ('none', 'errno was set to 0')
            print(('Failed to get image hash'
                   ' ({!r}): [{}] {}').format(path, err, err_msg), file=sys.stderr)
            return None
        return phash.value

    def hamming_distance(self, hash1, hash2):
        return self._lib.ph_hamming_distance(
            *map(ctypes.c_uint64, [hash1, hash2]))


class ImageManager(object):
    def __init__(self):
        self.phash = pHash()
        self.phash_cache = {}

    def get_phash(self, key):
        if key not in self.phash_cache:

            try:
                self.phash_cache[key] = int(Image.select().where(Image.key == key).get().phash)
            except:
                print(key + " not exist , need download")
                file_path = self._download(key)
                try:
                    key_hash = self.phash.dct_imagehash(file_path)
                except:
                    key_hash = DEFAULT_PHASH
                # self._delete_file(file_path)
                image = Image()
                image.key = key
                image.phash = key_hash
                image.gallery_id = key.split("/")[1]
                image.save()
                self.phash_cache[key] = key_hash
        return self.phash_cache[key]

    # def has_same(self, key):
    #     same = False
    #     p1 = self.phash(key)
    #     for k, v in self.phash_map.iteritems():
    #         if k == key:
    #             continue
    #         p2 = v
    #         distance = hammingDist(p1, p2)
    #         if distance < 16:
    #             same = True
    #             print
    #             "{k1}  ,  {k2}  maybe same distance:{d}".format(k1=key, k2=k, d=distance)
    #     return same

    def distance(self, key1, key2):
        # s1 = bin(self.get_phash(key1))[2:].rjust(8,'0')
        # s2 = bin(self.get_phash(key2))[2:].rjust(8,'0')
        # return sum([ch1 != ch2 for ch1, ch2 in zip(s1, s2)])
        return self.phash.hamming_distance(self.get_phash(key1), self.get_phash(key2))

    def _download(self, key):
        print("download  " + key)
        url = "http://static.meizibar.com/{key}!dedup1".format(key=key)
        r = requests.get(url)
        file_path = "/tmp/images/dedup/" + str(random.random() * time.time())
        open(file_path, 'wb').write(r.content)
        return file_path

    def _delete_file(self, path):
        print("delete " + path)
        if os.path.exists(path):
            os.remove(path)


if __name__ == '__main__':
    manager = ImageManager()


    # f = open("/tmp/tmp01.log","r")
    # datas = [d.replace("\n","") for d in f.readlines()]
    # print(datas)
    # for index,key in enumerate(datas):
    #     print (key)
    #     print (index)
    #     print(manager.get_phash(key))
    def hammingDist(s1, s2):
        assert len(s1) == len(s2)
        # s1 = "".join([str(bin(int(s,16)))[2:].rjust(8,'0') for s in s1])
        # s2 = "".join([str(bin(int(s,16)))[2:].rjust(8,'0') for s in s2])
        return sum([ch1 != ch2 for ch1, ch2 in zip(s1, s2)])


    h1 = manager.get_phash("images/3UGUuUhrf/dmvbm40sl")
    h2 = manager.get_phash("images/EZmA7436J/DOpIgiILX")
    print(manager.distance("images/3UGUuUhrf/dmvbm40sl", "images/EZmA7436J/DOpIgiILX"))
    print(bin(h1)[2:])
    print(bin(h2)[2:].rjust(64, '0'))
