/////////////////////////////////////////////////////////////////
// Author: xin luo
// create: 2021.10.30; ; modify: 2022.8.7
// Description: select the landsat images
/////////////////////////////////////////////////////////////////

var bands_sel = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7'] // landsat 8
// var bands_sel = ['B1', 'B2', 'B3', 'B4', 'B5', 'B7']    // landsat 5,7

var region_wkl = ee.FeatureCollection('users/xin_luo/Glacier-RGI1305/wkunlun').geometry();
var region_kara = ee.FeatureCollection('users/xin_luo/Glacier-RGI1305/karakoram').geometry();
var region = region_wkl.union({'right': region_kara, 'maxError': 1});

var start_time = '2020-05-1';
var end_time = '2020-09-30';

print('scene area:', region.area())

//// Landsat 578 image
// var img_col = ee.ImageCollection('LANDSAT/LT05/C01/T1_SR')
// var img_col = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR')
var img_col = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR')
  .filter(ee.Filter.lt('CLOUD_COVER_LAND', 20))
  .filterBounds(region)
  .filterDate(start_time, end_time )
  // .filter(ee.Filter.eq('WRS_PATH', 145))
  // .filter(ee.Filter.eq('WRS_ROW', 36))  //  35 & 36
  .sort('SENSING_TIME');

print('img_col:', img_col)

var img_mosaic = img_col.mosaic().clip(region).select(bands_sel)
print('img_mosaic:', img_mosaic)


// // // Export to Google Drive
// Export.image.toDrive({
//     image: img_mosaic,
//     description: 'l8_kunlun_202012',
//     folder: 'tmp',
//     scale: 30,
//     fileFormat: 'GeoTIFF',
//     region: region
//     });

//// visualization
Map.centerObject(region, 6);
var empty = ee.Image().byte();
var outline_wkl = empty.paint({
    featureCollection: region_wkl, color: 1, width: 3});
var outline_kara = empty.paint({
    featureCollection: region_kara, color: 1, width: 3});
    
// Map.addLayer(img, {bands: ['B5', 'B4', 'B3'], min:0, max:4000}, 'Landsat 8');
Map.addLayer(img_mosaic, {bands: ['B4', 'B3', 'B2'], min:0, max:5000}, 'Landsat 8');
Map.addLayer(outline_wkl, {palette: '#FFFF00'}, 'outline_wkl')
Map.addLayer(outline_kara, {palette: '#008000'}, 'outline_kara')


