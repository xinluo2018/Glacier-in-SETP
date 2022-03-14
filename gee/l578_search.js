/////////////////////////////////////////////////////////////////
// Author: xin luo
// Date: 2021.10.30
// Description: select the landsat images
/////////////////////////////////////////////////////////////////

var bands_sel = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7'] // landsat 8
// var bands_sel = ['B1', 'B2', 'B3', 'B4', 'B5', 'B7']    // landsat 5,7


var region = ee.FeatureCollection('users/xin_luo/tmp/kunlun_region');
var region = region.geometry();

print('scene area:', region.area())

//// Landsat 578 image
// var image_collection = ee.ImageCollection('LANDSAT/LT05/C01/T1_SR')
// var image_collection = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR')
var img_col = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR')
  .filter(ee.Filter.lt('CLOUD_COVER_LAND', 20))
  .filterBounds(region)
  .filterDate('2020-09-10', '2020-09-21')
  .filter(ee.Filter.eq('WRS_PATH', 145))
  .sort('SENSING_TIME');

print('img_col:', img_col)

var img_mosaic = img_col.mosaic().clip(region).select(bands_sel)
print('img_mosaic:', img_mosaic)


// // Export to Google Drive
// Export.image.toDrive({
//     image: img_mosaic,
//     description: 'l8_kunlun_20200914',
//     folder: 'tmp',
//     scale: 30,
//     fileFormat: 'GeoTIFF',
//     region: region
//     });

//// visualization
Map.centerObject(region, 6);
var empty = ee.Image().byte();
var scene_outline = empty.paint({
    featureCollection: region, color: 1, width: 3});

// Map.addLayer(img, {bands: ['B5', 'B4', 'B3'], min:0, max:4000}, 'Landsat 8');
Map.addLayer(img_mosaic, {bands: ['B5', 'B4', 'B3'], min:0, max:9000}, 'Landsat 8');
Map.addLayer(scene_outline, {palette: '#FFFF00'}, 'scene_outline')



