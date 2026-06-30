
import rasterio as rio
from rasterio.warp import reproject, calculate_default_transform,Resampling

def reproj_img(path_in, path_out, dst_crs = 'EPSG:4326'):

    src = rio.open(path_in)
    transform, width, height = calculate_default_transform(
        src.crs, dst_crs, src.width, src.height, *src.bounds)
    kwargs = src.meta.copy()
    kwargs.update({
        'crs': dst_crs,
        'transform': transform,
        'width': width,
        'height': height})

    dst = rio.open(path_out, 'w', **kwargs)
    for i in range(1, src.count + 1):
        reproject(
            source=rio.band(src, i),
            destination=rio.band(dst, i),
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=transform,
            dst_crs=dst_crs,
            resampling=Resampling.nearest)

