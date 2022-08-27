/////////////////////////////////////////////////////////////////
// Author: xin luo
// Create: 2021.10.27
/////////////////////////////////////////////////////////////////

// --------- region --------
var region = ee.Geometry.Rectangle(76.376, 34.415, 83.273, 37.280) // kunlun mountain

// --------- visualization bands -------
// var bands_sel = ['Oa11_radiance', 'Oa05_radiance', 'Oa03_radiance']
var bands_sel = ['Oa08_radiance', 'Oa06_radiance', 'Oa04_radiance']

// --------- data search --------
var img_col = ee.ImageCollection('COPERNICUS/S3/OLCI')
                  .filterDate('2018-07-07', '2018-08-08')
                  .filterBounds(region);
// print(img_col)

// --- Ensure the s3 image fully contain the given region.---
var condition = function(image){
    var footprint = ee.Geometry(image.get('system:footprint'))
    var condition = ee.Geometry.Polygon(footprint.coordinates()).contains(region)
    return ee.Algorithms.If(condition, 
                            image.set('data', 'true'), 
                            ee.Image([]).set('data', 'false'))};

var img_col = img_col.map(condition).filterMetadata('data', 'equals','true')
print(img_col)

// ---- specific image selection ----
var img = ee.Image('COPERNICUS/S3/OLCI/S3A_20180707T044644_20180707T044944')
                    .clip(region).select(bands_sel)

var empty = ee.Image().byte();
var outline = empty.paint({
        featureCollection: region, color: 1, width: 3});

Map.centerObject(region, 5);
// Map.addLayer(img_col, {bands: bands_sel, min: 0, max: 250}, 'sentinel-3');
Map.addLayer(img, {bands: bands_sel, min: 0, max: 150}, 'sentinel-3');
Map.addLayer(outline, {palette: 'FFFF00'}, 'outline')

// // --- export ---
// Export.image.toDrive({
//   image: img,
//   description: 'S3A_20180207T115228_20180207T115528',
//   // folder: 'landsat578_water',
//   scale: 300,
//   fileFormat: 'GeoTIFF',
//   region: region
//   });
