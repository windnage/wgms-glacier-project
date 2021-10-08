# This is from
# https://stackoverflow.com/questions/47038407/dissolve-overlapping-polygons-with-gdal-ogr-while-keeping-non-connected-result
import fiona
from shapely.ops import cascaded_union
from shapely.geometry import shape, mapping

src = '/tmp/polys/glims_region_7_cleaned.shp'

with fiona.open(src, 'r') as ds_in:
    crs = ds_in.crs
    drv = ds_in.driver

    geoms = []
    for x in ds_in:
        geom = shape(x["geometry"])
        if not geom.is_valid:
            geom = geom.buffer(0)

        geoms.append(geom)

    dissolved = cascaded_union(geoms)

schema = {
    "geometry": "Polygon",
    "properties": {"id": "int"}
}

dst = '/tmp/polys/soutput.shp'

with fiona.open(dst, 'w', driver=drv, schema=schema, crs=crs) as ds_dst:
    for i, g in enumerate(dissolved):
        ds_dst.write({"geometry": mapping(g), "properties": {"id": i}})
