## Author: xin luo
## create: 2023.6.22;
## des: images mosaic and subsetting to specific extent. 
## usage: python imgs2tiles.py


import os
os.chdir('/home/xin/Developer-luo/Glacier-in-SETP')
from glob import glob
from utils.imgs_in_extent import imgs_in_extent

def imgs2tile(path_imgs_in, path_tile_out, extent_tile):
    '''
    args:
      path_imgs_in: list, paths of candidate images for subseting.
      path_tile_out: str, path for the tile saved.
      extent_tile: list, [left, right, bottom, up]
    '''
    left, right, bottom, up = extent_tile
    path_imgs_sel = imgs_in_extent(paths_img=path_imgs_in, extent=extent_tile)
    path_imgs_sel_str = ' '.join(path_imgs_sel)
    command_merge = 'gdal_merge.py -n -999 -a_nodata -999 -co COMPRESS=LZW -o imgs_mosaic.tif ' + path_imgs_sel_str
    print(os.popen(command_merge).read())
    extent_subs = ' '.join([str(left), str(up), str(right), str(bottom)])
    command_subs = 'gdal_translate -projwin ' + extent_subs + ' -co COMPRESS=LZW imgs_mosaic.tif ' + path_tile_out  ## subseting
    print(os.popen(command_subs).read())
    os.remove('imgs_mosaic.tif')


def imgs2tiles(path_imgs_in, dir_tile_out, tile_corners, res_tile=1):
  '''
  args:
    path_imgs_in: list, paths of candidate images for subseting.
    dir_tile_out: str, the directory that that croppted tiles to be saved.
    tile_corners: list of [left_tiles, bottom_tiles], the tiles to be subset.
    res_tile: resolution of the tile, optional 1 and 0.5      
  '''
  left_tiles, bottom_tiles = tile_corners
  if not os.path.exists(dir_tile_out): os.makedirs(dir_tile_out)
  for i_tile, left_tile in enumerate(left_tiles):
    print('i_tile: %s' % (i_tile))
    if res_tile == 1:
      extent = [left_tile, left_tile+1, bottom_tiles[i_tile], bottom_tiles[i_tile]+1]
      path_out = dir_tile_out + '/tile_%s_%s.tif' % (str(bottom_tiles[i_tile]), str(left_tile)) 
      imgs2tile(path_imgs_in=path_imgs, path_tile_out=path_out, extent_tile=extent)
    else:
      lefts_tile_sub = [left_tile, left_tile + res_tile]
      bottoms_tile_sub =[bottom_tiles[i_tile], bottom_tiles[i_tile] + res_tile]
      extents_sub = [[left_tile_sub, left_tile_sub+res_tile, bottom_tile_sub, bottom_tile_sub+0.5] \
                                  for left_tile_sub in lefts_tile_sub for bottom_tile_sub in bottoms_tile_sub ]
      for extent_sub in extents_sub:
        print('extent: %s %s %s %s' % (extent_sub[0], extent_sub[1], extent_sub[2], extent_sub[3]))
        left_sub, right_sub, bottom_sub, up_sub = extent_sub
        path_out = dir_tile_out + '/tile_%s_%s.tif' % (str(int(bottom_sub*10)), str(int(left_sub*10))) 
        imgs2tile(path_imgs_in=path_imgs_in, path_tile_out=path_out, extent_tile=extent_sub)



### Subseting tiles to sub-tiles of the difference map.
left_tiles =   [91, 92, 93, 94, 95, 91, 92, 93, 94, 95, 96, 97, 91, 92, 93, 94, 95, 96, 97, 98, 94, 95, 96, 97, 98, 96, 97, 98]
bottom_tiles = [31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 30, 30, 29, 29, 29, 29, 29, 29, 29, 29, 28, 28, 28, 28, 28, 27, 27, 27]

if __name__ == '__main__':

  # -- 1. dems difference tile
  res_tile_sub = 1
  dir_imgs_in = 'data/aster-stereo/tiles-dif-map'
  dir_tile_out = 'data/aster-stereo/tiles-sub-dif-map'
  path_imgs = glob(dir_imgs_in + '/tile_??_??.tif')
  imgs2tiles(path_imgs_in=path_imgs, dir_tile_out=dir_tile_out, \
                       tile_corners=[left_tiles, bottom_tiles], res_tile=res_tile_sub)


  # ## -- 2. JRC water tile
  # res_tile_sub = 0.5
  # path_img_in = 'data/land-cover/water/water-jrc/mask_mosaic_subs.tif'
  # dir_tile_out = 'data/land-cover/water/water-jrc/tiles-'
  # path_imgs = [path_img_in]
  # imgs2tiles(path_imgs_in=path_imgs, dir_tile_out=dir_tile_out, \
  #                                   tile_corners=[left_tiles, bottom_tiles], res_tile=res_tile_sub)


  # ### -- 3. Globeland30 stable land cover tiles
  # res_tile_sub = 0.5
  # dir_imgs_in = 'data/land-cover/stable-cover/tiles-2010'
  # dir_tile_out = 'data/land-cover/stable-cover/tiles-sub-2010'
  # path_imgs = glob(dir_imgs_in + '/tile_??_??.tif')
  # imgs2tiles(path_imgs_in=path_imgs, dir_tile_out=dir_tile_out, \
  #                             tile_corners=[left_tiles, bottom_tiles], res_tile=res_tile_sub)


  # ### -- 4.  srtm dem tiles
  # res_tile_sub = 0.5
  # dir_imgs_in = 'data/dem-data/srtm-c/tiles'
  # dir_tile_out = 'data/dem-data/srtm-c/tiles-sub'
  # path_imgs = glob(dir_imgs_in + '/tile_??_??.tif')
  # imgs2tiles(path_imgs_in=path_imgs, dir_tile_out=dir_tile_out, \
  #                             tile_corners=[left_tiles, bottom_tiles], res_tile=res_tile_sub)


  # ### -- 5. rgi60 glacier to tiles
  # res_tile_sub = 0.5
  # path_img_in = 'data/land-cover/rgi60/rgi60_setp_mask.tif'
  # dir_tile_out = 'data/land-cover/rgi60/tiles-sub'
  # path_imgs = [path_img_in]
  # imgs2tiles(path_imgs_in=path_imgs, dir_tile_out=dir_tile_out, \
  #                             tile_corners=[left_tiles, bottom_tiles], res_tile=res_tile_sub)



