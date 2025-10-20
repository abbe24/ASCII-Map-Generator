import elevation
import rasterio
import numpy as np

#Bounding Box for 10x10 miles41°45'00.0"N 111°48'47.9"W
#10 miles = 16.1 km
#1 deg latitude = 69 mi -> 10 mi ~ 0.145 deg

#Latitude: 41.7400° N
#Longitude: -111.8133° 

#41°45'00.0"N 111°48'47.9"W

#west_lon = -111.906
#east_lon = -111.712
#south_lat = 41.671
#north_lat = 41.816

# NE(41.816, -111.712) 
# SE(41.671, -111.712) 
# SW(41.671, -111.906) 
# NW(41.816, -111.906)

# Download SRTM data clipped to 10x10 miles around USU
bounds = (-111.906, 41.671, -111.712, 41.816)
elevation.clip(bounds=bounds, output="usu.tif")

# Read DEM
with rasterio.open("usu.tif") as src:
    dem = src.read(1)
    transform = src.transform

# Convert DEM to 0.25 mi tiles (~402 m)
tile_size_meters = 402
pixel_size = transform.a  # resolution in meters
block = int(tile_size_meters / pixel_size)

ascii_map = []
for i in range(0, dem.shape[0], block):
    row = []
    for j in range(0, dem.shape[1], block):
        patch = dem[i:i+block, j:j+block]
        if patch.size == 0: continue
        elev_gain = patch.max() - patch.min()

        # Your ASCII terrain system
        if elev_gain < 25:
            c = "."
        elif elev_gain < 50:
            c = ","
        elif elev_gain < 125:
            c = "~"
        elif elev_gain < 250:
            c = "^"
        elif elev_gain < 750:
            c = "A"
        elif elev_gain < 1250:
            c = "M"
        else:
            c = "#"
        row.append(c)
    ascii_map.append("".join(row))

# Display ASCII map
for line in ascii_map:
    print(line)




#map2DStrArray = [
#    ["f", "f", ".", "."],
#    [".", "f", "M", "f"],
#    [".", ".", "f", "."],
#    ["f", "f", "s", "s"]
#]

#mapStr = "\n".join(["".join(r) for r in map2DStrArray])
#print(mapStr)