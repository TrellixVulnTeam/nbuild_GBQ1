#!/usr/bin/env python3.6
# -*- coding: utf-8 -*-

import os
import hashlib
import requests
from urllib.parse import urlparse
import urllib.request
from nbuild.log import wlog, ilog, clog, flog
from nbuild.stdenv.package import get_package


def fetch_urls(
    downloads,
):
    for download in downloads:
        fetch_url(**download)


def fetch_url(
    url,
    md5=None,
    sha1=None,
    sha256=None,
):
    package = get_package()

    url_object = urlparse(url)
    path = os.path.join(
        package.download_dir,
        os.path.basename(url_object.path)
    )

    if not sha256:
        wlog(f"No sha256 to ensure the integrity of {url}")

    if not _check_file(path, md5, sha1, sha256):
        ilog(f"Fetching {url}")
        if url_object.scheme == 'http' or url_object.scheme == 'https':
            download_direct(url, path)
        elif url_object.scheme == ('ftp'):
            download_ftp(url, path)
        else:
            flog(f"Unknown protocol to download file from url {url}")
            exit(1)
        clog(f"Fetch done. Stored at {path}")
        if not _check_file(path, md5, sha1, sha256):
            flog(
                "Downloaded file's signature is invalid. "
                "Please verify the signature(s) in the build manifest "
                "and the authenticity of the given link."
            )
            exit(1)
    else:
        clog(f"Using cache at {path}")


def download_direct(url, path):
        req = requests.get(url, stream=True)
        with open(path, 'wb') as file:
            for chunk in req.iter_content(chunk_size=4096):
                file.write(chunk)


def download_ftp(url, path):
    with urllib.request.urlopen(url) as response, \
         open(path, 'wb') as out_file:
        data = response.read()
        out_file.write(data)


def _check_file(path, md5, sha1, sha256):
    if os.path.exists(path):
        out = True
        if md5 is not None:
            out &= _check_md5(path, md5)
        if sha1 is not None:
            out &= _check_sha1(path, sha1)
        if sha256 is not None:
            out &= _check_sha256(path, sha256)
        return out
    else:
        return False


def _check_md5(path, md5):
    hash_md5 = hashlib.md5()
    with open(path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest() == md5


def _check_sha1(path, sha1):
    hash_sha1 = hashlib.sha1()
    with open(path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b''):
            hash_sha1.update(chunk)
    return hash_sha1.hexdigest() == sha1


def _check_sha256(path, sha256):
    hash_sha256 = hashlib.sha256()
    with open(path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b''):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest() == sha256
