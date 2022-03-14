/////////////////////////////////////////////////////////////////
// Author: xin luo
// Create: 2021.10.27
/////////////////////////////////////////////////////////////////


var Bands_S2 = ['B2', 'B3', 'B4', 'B8', 'B11', 'B12']

var region = ee.FeatureCollection('users/xin_luo/tmp/kunlun_region');
var region = region.geometry();
print('scene area:', region.area())

/// Sentinel-2 image
var img_col = ee.ImageCollection('COPERNICUS/S2_SR')  // from 2017-03-28
// var img_col = ee.ImageCollection('COPERNICUS/S2')
                  .filterBounds(region)
                  .filterDate('2020-06-30', '2020-07-01')
                  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30));
print('img_col:', img_col)

var img_mosaic = img_col.mosaic().clip(region).select(Bands_S2)
print('img_mosaic:', img_mosaic)

var empty = ee.Image().byte();
var region_outline = empty.paint({
    featureCollection: region, color: 1, width: 3});

// // Export to Google Drive
// Export.image.toDrive({
//     image: img_mosaic,
//     description: 's2_kunlun_20200630',
//     folder: 'tmp',
//     scale: 20,
//     fileFormat: 'GeoTIFF',
//     region: region,
//     });


Map.centerObject(region, 6);
Map.addLayer(img_mosaic, {bands: ['B4', 'B3', 'B2'], min: 0, max: 10000}, 'sen2 image');
Map.addLayer(region_outline, {palette: '#FFFF00'}, 'scene_outline')

