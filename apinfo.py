#!/usr/bin/env python
#-*- coding: utf-8 -*-
from __future__ import print_function

from bs4 import BeautifulSoup
import argparse
import requests


from joblib import Parallel, delayed
import multiprocessing

num_cores = multiprocessing.cpu_count()

parser = argparse.ArgumentParser(description='Submit realm data to artifactpower.info')
parser.add_argument('--realm', required=True, help='Realm name')
parser.add_argument('--region', required=True, help='Region (EU/US)')
parser.add_argument('--verbose', '-v', action='store_true', default=False)

args = parser.parse_args()

if args.verbose:
   verbose=True
else:
   verbose=False

realm=args.realm
region=args.region

chars = []

def doPages():
  pages = range(0,435)
  for page in pages:
    html = grabPage(page)
    extractNames(html)

def grabPage(page):
  headers = {
    'Origin': 'http://www.wowprogress.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2859.0 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Cache-Control': 'no-cache',
    'X-Requested-With': 'XML HttpRequest',
    'Referer': 'http://www.wowprogress.com/gearscore/' + region + '/' + realm,
  }

  data = 'ajax=1'
  if verbose:
    print('Grabbing page ' + str(page+1) + ' from ' + region + '/' + realm)
  r = requests.post('http://www.wowprogress.com/gearscore/' + region.lower() + '/' + realm + '/char_rating/next/' + str(page-1), headers=headers, data=data)
  #todo - check if request succeeded
  return r.text

def extractNames(html):
  soup = BeautifulSoup(html)
  tags = soup.find_all('a', {"class" : "character"})
  if verbose:
    print('Extracted: ', end="")
  for elements in tags:
    name = elements.text
    if verbose:
      print(name + ", ", end="")
    chars.append(name.encode('utf-8'));
  if verbose:
    print('')

def submitToServer( char ):
  headers = {
    'Origin': 'http://artifactpower.info',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2859.0 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Cache-Control': 'no-cache',
    'Referer': 'http://artifactpower.info/',
  }

  data = 'char=' + char + '&region=' + region.upper() + '&server=' + realm + '&exec='
  
  if verbose:
     print('Submitting ' + region + '/' + realm + '/' + char)
  #todo - check if request succeeded
  r = requests.post('http://artifactpower.info/', headers=headers, data=data)

# scraping pages
# todo - this should be also parallised, but I failed badly
doPages()

# submit the data to the website
Parallel(n_jobs=num_cores)(delayed(submitToServer)(each) for each in chars)

# vim: set sw=2 :