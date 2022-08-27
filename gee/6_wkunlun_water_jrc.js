// author: xin luo
// create: 2021.11.26
// des: check jrc water of the study region.

// Study area
var region_wkl = ee.FeatureCollection('users/xin_luo/Glacier-RGI1305/wkunlun').geometry();
var region_kara = ee.FeatureCollection('users/xin_luo/Glacier-RGI1305/karakoram').geometry();
var region = region_wkl.union({'right': region_kara, 'maxError': 1});
var region_tile = ee.FeatureCollection(ee.Geometry.Rectangle(78, 36, 79, 37) )


var wkl_water_jrc = ee.Image('JRC/GSW1_3/GlobalSurfaceWater')
                        .select(['occurrence', 'max_extent'])
                        .clip(region);

var visual = {
    bands: ['occurrence'],
    min: 50.0, max: 100.0,
    palette: ['ffffff', 'ffbbbb', '0000ff']
};

var visual_ = {
    bands: ['max_extent'],
    min: 0.1, max: 1,
    palette: ['ffffff', 'ffbbbb', '0000ff']
};


var empty = ee.Image().byte();
//// outline visualization of the study area.
var outline_wkl = empty.paint({
    featureCollection: region_kara, color: 1, width: 3});
var outline_kara = empty.paint({
    featureCollection: region_wkl, color: 1, width: 3});
var outline_tile = empty.paint({
    featureCollection: region_tile, color: 1, width: 3});
    
Map.setCenter(81.0, 35.4, 7);
Map.addLayer(wkl_water_jrc, visual, 'Occurrence');
Map.addLayer(wkl_water_jrc.eq(1).selfMask(), visual_, 'max_extent water');
Map.addLayer(outline_wkl, {palette: '#FFFF00'}, 'outline_wkl')
Map.addLayer(outline_kara, {palette: '#008000'}, 'outline_kara')
Map.addLayer(outline_tile, {palette: '#FF0000'}, 'outline_tile')



// // export jcr water image
// Export.image.toDrive({
//     image: wkl_water_jrc,
//     description: 'wkl_water_jrc',
//     folder: 'tmp',
//     scale: 30, 
//     maxPixels: 1e10,
//     fileFormat: 'GeoTIFF',
//     region: region,
//     });
