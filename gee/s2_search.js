/////////////////////////////////////////////////////////////////
// Author: xin luo
// Create: 2021.10.27; modify: 2022.8.7
/////////////////////////////////////////////////////////////////


var Bands_S2 = ['B2', 'B3', 'B4', 'B8', 'B11', 'B12']

var region_wkl = ee.FeatureCollection('users/xin_luo/Glacier-RGI1305/wkunlun').geometry();
var region_kara = ee.FeatureCollection('users/xin_luo/Glacier-RGI1305/karakoram').geometry();
var region = region_wkl.union({'right': region_kara, 'maxError': 1});
print('scene area:', region.area())

/// Sentinel-2 image
var img_col = ee.ImageCollection('COPERNICUS/S2_SR')  // from 2017-03-28
// var img_col = ee.ImageCollection('COPERNICUS/S2')
                  .filterBounds(region)
                  // .filterDate('2019-11-30', '2020-02-01')
                  .filterDate('2020-05-01', '2020-09-01')
                  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20));
print('img_col:', img_col)

var img_mosaic = img_col.mosaic().clip(region).select(Bands_S2)
print('img_mosaic:', img_mosaic)

var empty = ee.Image().byte();
var outline_wkl = empty.paint({
    featureCollection: region_wkl, color: 1, width: 3});
var outline_kara = empty.paint({
    featureCollection: region_kara, color: 1, width: 3});

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
Map.addLayer(img_mosaic, {bands: ['B4', 'B3', 'B2'], min: 0, max: 7000}, 'sen2 image');
Map.addLayer(outline_wkl, {palette: '#FFFF00'}, 'outline_wkl')
Map.addLayer(outline_kara, {palette: '#008000'}, 'outline_kara')

