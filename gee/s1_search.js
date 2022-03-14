/////////////////////////////////////////////////////////////////
// Author: xin luo
// Create: 2021.10.27
/////////////////////////////////////////////////////////////////


var region = ee.Geometry.Rectangle(76.376, 34.415, 83.273, 37.280) // kunlun mountain
var bands_sel= ['VV','VH','VV']

var img_col = ee.ImageCollection('COPERNICUS/S1_GRD')
      .filter(ee.Filter.eq('instrumentMode', 'IW'))
      .filterBounds(region)
      .filterDate('2020-07-01', '2020-08-09');
print(img_col)


Map.centerObject(region, 6);
var empty = ee.Image().byte();
var scene_outline = empty.paint({
    featureCollection: region, color: 1, width: 3});


Map.addLayer(img_col, {bands: bands_sel, min:-30, max:0}, 'sen-1 image');
// Map.addLayer(sen3_img, {bands: bands_sel, min:0, max:100}, 'Sentinel 3');
Map.addLayer(scene_outline, {palette: '#FFFF00'}, 'scene_outline')


// Export.image.toDrive({
//   image: sen2_img,
//   description: 'S3A_20191225T045036_20191225T045336',
//   // folder: 'landsat578_water',
//   scale: 300,
//   fileFormat: 'GeoTIFF',
//   region: region
//   });

