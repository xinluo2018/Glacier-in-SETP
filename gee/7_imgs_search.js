/////////////////////////////////////////////////////////////////
// Author: xin luo
// create: 2021.10.30; ; modify: 2022.8.7
// Des: check the landsat images of the study region
/////////////////////////////////////////////////////////////////

// var bands_sel = ['B2', 'B3', 'B4', 'B5', 'B6', 'B7'] // landsat 8
var bands_sel = ['B1', 'B2', 'B3', 'B4', 'B5', 'B7']    // landsat 5,7

var region_wkl = ee.FeatureCollection('users/xin_luo/Glacier-RGI1305/wkunlun').geometry();
var region_kara = ee.FeatureCollection('users/xin_luo/Glacier-RGI1305/karakoram').geometry();
var region = region_wkl.union({'right': region_kara, 'maxError': 1});
var region_tile = ee.FeatureCollection(ee.Geometry.Rectangle(78, 36, 79, 37))
var region_rect = ee.FeatureCollection(ee.Geometry.Rectangle(72, 34, 84, 38))

var start_time = '2019-6-1';
var end_time = '2019-9-30';

print('scene area:', region.area())

//// Landsat 578 image
// var img_col = ee.ImageCollection('LANDSAT/LT05/C01/T1_SR')
// var img_col = ee.ImageCollection('LANDSAT/LE07/C01/T1_SR')
var img_col = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR')
  .filter(ee.Filter.lt('CLOUD_COVER_LAND', 10))
  .filterBounds(region)
  .filterDate(start_time, end_time )
  // .filter(ee.Filter.eq('WRS_PATH', 145))
  // .filter(ee.Filter.eq('WRS_ROW', 36))  //  35 & 36
  .sort('SENSING_TIME');

print('img_col:', img_col)

var img_mosaic = img_col.mosaic().clip(region).select(bands_sel)
print('img_mosaic:', img_mosaic)

//// JRC water map
var wkl_water_jrc = ee.Image('JRC/GSW1_3/GlobalSurfaceWater')
                        .select(['max_extent'])
                        .clip(region_rect);
var visual = {
    bands: ['max_extent'],
    min: 0, max: 1,
    palette: ['ffffff', 'ffbbbb', '0000ff']
};

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
// Map.centerObject(region, 6);
var empty = ee.Image().byte();
var outline_wkl = empty.paint({
    featureCollection: region_wkl, color: 1, width: 3});
var outline_kara = empty.paint({
    featureCollection: region_kara, color: 1, width: 3});
var outline_tile = empty.paint({
    featureCollection: region_tile, color: 1, width: 3});
  
      
Map.addLayer(img_col, {bands: ['B3', 'B2', 'B1'], min:0, max:4000}, 'Landsat 8');
// Map.addLayer(img_mosaic, {bands: ['B4', 'B3', 'B2'], min:0, max:5000}, 'Landsat 8');
// Map.addLayer(wkl_water_jrc.eq(1).selfMask(), visual, 'jrc_water');
Map.addLayer(outline_wkl, {palette: '#FFFF00'}, 'outline_wkl')
Map.addLayer(outline_kara, {palette: '#008000'}, 'outline_kara')
Map.addLayer(outline_tile, {palette: '#FF0000'}, 'outline_tile')


