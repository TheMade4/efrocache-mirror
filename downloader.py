import os
import hashlib
import subprocess
import asyncio

import requests


def background(f):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, **kwargs)
    return wrapped



efrocachemap_url = 'https://raw.githubusercontent.com/efroemling/ballistica/master/.efrocachemap'

cache_map = requests.get(efrocachemap_url).json()
cache_map_hashes = list(cache_map.values())

base_url = 'https://files.ballistica.net/cache/ba1'
base_path = os.path.join(os.getcwd(), 'ba1')


def get_hash(data):
	return hashlib.md5(data).hexdigest()


def get_prefix(_hash):
	_hash = f'{_hash[:2]}/{_hash[2:4]}'
	return _hash


def get_prefixed_hash(_hash):
	_hash = f'{get_prefix(_hash)}/{_hash[4:]}'
	return _hash


def get_download_path(_hash):
	return os.path.join(base_path, get_prefixed_hash(_hash))


def get_download_dir(_hash):
	return os.path.join(base_path, get_prefix(_hash))


@background
def download(url, path, i, n):
	print('start downloading', url, path)
	subprocess.run([
		'curl',
		'-f',
		'-s',
		url,
		'-o',
		path
	])
	print(f'downloaded {i} in {n}')



download_list = []
for _hash in cache_map_hashes:
	p_hash = get_prefixed_hash(_hash)
	download_url = f'{base_url}/{p_hash}'
	download_path_prefix = get_download_dir(_hash)
	download_list.append((download_url, download_path_prefix, _hash[4:]))

n = len(download_list)
for i, (url, path, file_name) in enumerate(download_list):
	print(f'{i} in {n}')
	full_path = os.path.join(path, file_name)
	if not os.path.exists(path):
		print('create dir', path)
		os.makedirs(path)
	if not os.path.exists(full_path):
		download(url, full_path, i, n)
		continue
	print('is exists', full_path)


