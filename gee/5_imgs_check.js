// author: xin luo
// create: 2022.8.27
// des: check specific optical image of the study region


var region_wkl = ee.FeatureCollection('users/xin_luo/Glacier-RGI1305/wkunlun').geometry();
var region_kara = ee.FeatureCollection('users/xin_luo/Glacier-RGI1305/karakoram').geometry();
var region_tile = ee.FeatureCollection(ee.Geometry.Rectangle(78, 36, 79, 37))

var bands_l8 = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7'] // landsat 8
var bands_l57 = ['B1', 'B2', 'B3', 'B4', 'B5', 'B7']    // landsat 5,7

// --- 2009, landsat 5
var img_2009_1 = ee.Image('LANDSAT/LT05/C01/T1_SR/LT05_147034_20090813')
var img_2009_2 = ee.Image('LANDSAT/LT05/C01/T1_SR/LT05_147035_20090813')
var img_2009 = ee.ImageCollection([img_2009_1, img_2009_2]).mosaic().select(bands_l57)
// Map.addLayer(img_2009_1, {bands: ['B3', 'B2', 'B1'], min:0, max:4000}, 'img_2009_1');
// Map.addLayer(img_2009_2, {bands: ['B3', 'B2', 'B1'], min:0, max:4000}, 'img_2009_2');
Map.addLayer(img_2009, {bands: ['B3', 'B2', 'B1'], min:0, max:4000}, 'img_2009');

// --- 2019, landsat 8
var img_2019_1 = ee.Image('LANDSAT/LC08/C01/T1_SR/LC08_147034_20190926')
var img_2019_2 = ee.Image('LANDSAT/LC08/C01/T1_SR/LC08_147035_20190926')
var img_2019 = ee.ImageCollection([img_2019_1, img_2019_2]).mosaic().select(bands_l8)
// Map.addLayer(img_2019_1, {bands: ['B4', 'B3', 'B2'], min:0, max:4000}, 'img_2019_1');
// Map.addLayer(img_2019_2, {bands: ['B4', 'B3', 'B2'], min:0, max:4000}, 'img_2019_2');
Map.addLayer(img_2019, {bands: ['B4', 'B3', 'B2'], min:0, max:4000}, 'img_2019');


// // // Export to Google Drive
// Export.image.toDrive({
//     image: img_2019,
//     description: 'region_2019_36_78',
//     folder: 'tmp',
//     scale: 30,
//     fileFormat: 'GeoTIFF',
//     region: region_tile
//     });


//// outline visualization
// Map.centerObject(region, 6);
var empty = ee.Image().byte();
var outline_wkl = empty.paint({
    featureCollection: region_wkl, color: 1, width: 3});
var outline_kara = empty.paint({
    featureCollection: region_kara, color: 1, width: 3});
var outline_tile = empty.paint({
    featureCollection: region_tile, color: 1, width: 3});

Map.addLayer(outline_wkl, {palette: '#FFFF00'}, 'outline_wkl')
Map.addLayer(outline_kara, {palette: '#008000'}, 'outline_kara')
Map.addLayer(outline_tile, {palette: '#FF0000'}, 'outline_tile')





