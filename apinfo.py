#!/usr/bin/env python
#-*- coding: utf-8 -*-
from __future__ import print_function

from bs4 import BeautifulSoup
import argparse
import requests
import time

from joblib import Parallel, delayed
import multiprocessing

parser = argparse.ArgumentParser(description='Submit realm data to artifactpower.info')
parser.add_argument('--realm', required=True, help='Realm name')
parser.add_argument('--region', required=True, help='Region (EU/US)')
parser.add_argument('--verbose', '-v', action='store_true', default=False)
parser.add_argument('--debug', '-d', action='store_true', default=False)
parser.add_argument('--threads', '-t', type=int, default=multiprocessing.cpu_count(), help='Amount of threads to use. Defaults to core count.')
parser.add_argument('--delay', type=int, default=0, help='Delay submits by amount of seconds. Defaults to 0')
parser.add_argument('--start', type=int, default=0, help='Start from page number. Defaults to 0.')
parser.add_argument('--end', type=int, default=435, help='End at page number. Defaults to 435')

args = parser.parse_args()

realm=args.realm
region=args.region

chars = []

def doPages():
  pages = range(args.start,args.end)
  for page in pages:
    html = grabPage(page)

    if args.debug:
      print('Debug: ' + html)

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
  print('Grabbing page ' + str(page+1) + ' from ' + region + '/' + realm)
  r = requests.post('http://www.wowprogress.com/gearscore/' + region.lower() + '/' + realm + '/char_rating/next/' + str(page-1), headers=headers, data=data)
  #todo - check if request succeeded
  return r.text

def extractNames(html):
  soup = BeautifulSoup(html, "html.parser")
  tags = soup.find_all('a', {"class" : "character"})
  if args.verbose:
    print('Extracted: ', end="")

  for elements in tags:
    name = elements.text

    if args.verbose:
      print(name + ", ", end="")

    chars.append(name.encode('utf-8'));

  if args.verbose:
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
  
  print('Submitting ' + region + '/' + realm + '/' + char)
  #todo - check if request succeeded
  r = requests.post('http://artifactpower.info/', headers=headers, data=data)
  time.sleep(args.delay)
  if args.debug:
    print('Debug: ' + r.text)

# scraping pages
# todo - this should be also parallised, but I failed badly
doPages()

# submit the data to the website
Parallel(n_jobs=args.threads)(delayed(submitToServer)(each) for each in chars)

# vim: set sw=2 :
