#!/bin/env python3
import sys, os

assets = '/assets'
flairs_png = '/flairs.png'
template = '_template'

if len(sys.argv) < 4:
  print('Not enough args')
  exit
  sys.exit(1)

target = sys.argv[1]
try:
  dim = tuple(map(int, sys.argv[2:4]))
except ValueError:
  print('Last 2 args must be numeric (image size)')
  sys.exit(2)

if not os.path.isdir(target):
  print('target folder', target, 'does not exist')
  sys.exit(3)

if not os.path.isdir(target + assets):
  print('target does not have assets folder')
  sys.exit(4)


### flair image ###

pngs = list(filter(lambda f: f.endswith('.png'), os.listdir(target + assets)))
full_pngs = [target + assets + '/' + p for p in pngs]

from PIL import Image
images = list(map(Image.open, full_pngs))

h = dim[1] * len(images)
flairs_img = Image.new('RGB', (dim[0], h))

for y in range(len(images)):
  images[y].thumbnail(dim, Image.ANTIALIAS)
  flairs_img.paste(images[y], (0, dim[1] * y))

flairs_img.save(target + flairs_png)


### ranks/masteries images ###

rank_img = Image.open('_ranks/all.png')
rank_img.thumbnail((dim[1], dim[1] * 8))
rank_img.save(target + '/ranks.png')

mast_img = Image.open('_masteries/all.png')
mast_img.thumbnail((dim[1], dim[1] * 7))
mast_img.save(target + '/masteries.png')


### template files ###

classes = [p[:p.index('.')].replace('_', '') for p in pngs]

import shutil
for f in ['compile.scss', 'reddit.scss']:
  shutil.copy2(template + '/' + f, target + '/' + f)

with open(template + '/styles.scss', 'r') as styles_file:
  scss = styles_file.read()
scss = scss.replace('$$SIZE$$', str(dim[1]))
scss = scss.replace('$$RATIO$$', str(dim[0] / dim[1]))
scss = scss.replace('$$FLAIRNAMES$$', ' '.join(classes))
with open(target + '/styles.scss', 'w') as styles_file:
  styles_file.write(scss)

with open(template + '/index.html', 'r') as html_file:
  html = html_file.read()
html = html.replace('$$FLAIRNAMES$$', '\n'.join(['  - ' + c for c in classes]))
with open(target + '/index.html', 'w') as html_file:
  html_file.write(html)

  

