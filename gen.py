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
scaling = 1
try:
  dim = tuple(map(int, sys.argv[2:4]))
  if len(sys.argv) > 4:
    scaling = float(sys.argv[4])
except ValueError:
  print('Last three args must be numeric (image size)')
  sys.exit(2)

if not os.path.isdir(target):
  print('target folder', target, 'does not exist')
  sys.exit(3)

if not os.path.isdir(target + assets):
  print('target does not have assets folder')
  sys.exit(4)

original_dim = dim
dim = tuple([ int(scaling * x) for x in dim ])

### flair image ###

pngs = list(filter(lambda f: f.endswith('.png') or f.endswith('.jpg') or f.endswith('.jpeg'), os.listdir(target + assets)))
pngs = sorted(pngs, key=str.lower)

full_pngs = [target + assets + '/' + p for p in pngs]

from PIL import Image, ImageFilter
images = list(map(Image.open, full_pngs))

h = dim[1] * len(images)
flairs_img = Image.new('RGBA', (dim[0], h))

for y in range(len(images)):
  img = images[y].convert('RGBA')
  if img.size[0] / img.size[1] > dim[0] / dim[1]:
    width = int(img.size[0] * dim[1] / img.size[1])
    img = img.resize((width, dim[1]), resample=Image.BILINEAR)
    offset = int((width - dim[0]) / 2) # extra width / 2
    img = img.crop((offset, 0, offset + dim[0], dim[1]))
  else:
    img = img.resize(dim, resample=Image.BILINEAR)

  loc = [0, dim[1] * y]
  loc[0] += (dim[0] - img.size[0]) // 2
  loc[1] += (dim[1] - img.size[1]) // 2
  #TODO
  left = img.crop((0, 0, 1, img.size[1]))
  right = img.crop((img.size[0] - 1, 0, img.size[0], img.size[1]))
  left = left.resize((dim[0] // 2, dim[1]), resample=Image.NEAREST)
  right = right.resize((dim[0] // 2, dim[1]), resample=Image.NEAREST)
  #left.putalpha(127)
  #right.putalpha(127)
  flairs_img.paste(left, (0, dim[1] * y))
  flairs_img.paste(right, (dim[0] // 2, dim[1] * y))
  flairs_img.paste(img, tuple(loc))

flairs_img.save(target + flairs_png)


### ranks/masteries images ###

rank_img = Image.open('_ranks/all.png')
rank_img.thumbnail((dim[1], dim[1] * 8))
rank_img.save(target + '/ranks.png')

mast_img = Image.open('_masteries/all.png')
mast_img.thumbnail((dim[1], dim[1] * 7))
mast_img.save(target + '/masteries.png')


### template files ###

classes = [p[:p.index('.')].replace('_', '').replace(' ', '-') for p in pngs]

import shutil
for f in ['compile.scss', 'reddit.scss']:
  shutil.copy2(template + '/' + f, target + '/' + f)

with open(template + '/styles.scss', 'r') as styles_file:
  scss = styles_file.read()
scss = scss.replace('$$SIZE$$', str(original_dim[1]))
scss = scss.replace('$$WIDTH$$', str(original_dim[0]))
scss = scss.replace('$$RATIO$$', str(dim[0] / dim[1]))
scss = scss.replace('$$FLAIRNAMES$$', ' '.join(classes))
with open(target + '/styles.scss', 'w') as styles_file:
  styles_file.write(scss)

with open(template + '/index.html', 'r') as html_file:
  html = html_file.read()
html = html.replace('$$FLAIRNAMES$$', '\n'.join(['  - ' + c for c in classes]))
with open(target + '/index.html', 'w') as html_file:
  html_file.write(html)
