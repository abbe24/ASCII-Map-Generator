import numpy as np
import rasterio

#old main: 41°44'27.0"N 111°48'52.0"W

np.set_printoptions(threshold=np.inf, linewidth=200)
#######################################################################3
# For demonstration, create a dummy 40x40 array
elevation_tiles_kft_rounded = np.random.randint(4, 7, (40, 40))

# --- DEM bounds (from your crop) ---
lat_max = 41.816   # North
lat_min = 41.671   # South
lon_min = -111.906 # West
lon_max = -111.712 # East

# --- Old Main coordinates ---
old_main_lat = 41 + 44/60 + 27/3600       # 41°44'27.0"N → 41.740833
old_main_lon = -(111 + 48/60 + 52/3600)   # 111°48'52.0"W → -111.814444

# --- Step 1: Normalize Old Main position in DEM ---
norm_row = (lat_max - old_main_lat) / (lat_max - lat_min)
norm_col = (old_main_lon - lon_min) / (lon_max - lon_min)

# --- Step 2: Map to 40x40 tile ---
tile_row = int(norm_row * 40)
tile_col = int(norm_col * 40)

print(f"Old Main is at tile row {tile_row}, column {tile_col} in the 40x40 array.")
#####################################################################################

# Load the cropped DEM
with rasterio.open("usu_crop.tif") as src:
    data = src.read(1)  # 2D elevation array

    rows, cols = data.shape
    print(f"Cropped DEM size: {rows} x {cols}")

    # We want 40 x 40 tiles
    target_size = 40

    # Compute block size
    block_y = rows // target_size
    block_x = cols // target_size
    print(f"Block size: {block_y} rows x {block_x} cols per tile")

    # Trim to multiple of block size
    trimmed = data[:block_y * target_size, :block_x * target_size]

    # Reshape and average to downsample
    reduced = trimmed.reshape(target_size, block_y, target_size, block_x).mean(axis=(1, 3))

    # Convert to integers
    elevation_tiles = reduced.astype(int)

# Convert meters → feet
elevation_tiles_ft = (elevation_tiles * 3.28084).astype(int)

# Elevation in thousands of feet (one decimal place)
elevation_tiles_kft = (elevation_tiles_ft / 1000.0).round(1)

#print("Elevation in thousands of feet (40x40):")
#print(elevation_tiles_kft)

# Elevation rounded to nearest 1000 ft
elevation_tiles_kft_rounded = np.rint(elevation_tiles_ft / 1000.0).astype(int)

# --- Step 3: Convert elevation array to string and place '@' ---
elevation_str_array = elevation_tiles_kft_rounded.astype(str)
elevation_str_array[tile_row, tile_col] = "@"
elevation_str = "\n".join(" ".join(row) for row in elevation_str_array)

#print("Elevation rounded to nearest 1000 ft (40x40):")
#print(elevation_tiles_kft_rounded)

#####################################################################################################
# --- Step 0: We already have ---
# trimmed = data[:block_y * target_size, :block_x * target_size]  # original DEM in meters
# block_y, block_x = 13, 17  # example from your print
# target_size = 40

# --- Step 1: Convert trimmed DEM to feet ---
trimmed_ft = trimmed * 3.28084  # float array in feet

# --- Step 2: Reshape into 40x40 tiles ---
reshaped = trimmed_ft.reshape(target_size, block_y, target_size, block_x)

# --- Step 3: Compute elevation range per tile (max - min) ---
elevation_range_ft = (reshaped.max(axis=(1,3)) - reshaped.min(axis=(1,3))).astype(int)

# --- Step 4: Convert to string array and place '@' for Old Main ---
elevation_range_str = elevation_range_ft.astype(str)
elevation_range_str[tile_row, tile_col] = "@"

# --- Step 1: Convert range to “hundreds of feet” rounded down ---
elevation_gain_digit = (elevation_range_ft // 100).astype(int)

# --- Step 2: Convert to string array and place '@' for Old Main ---
elevation_gain_str = elevation_gain_digit.astype(str)
elevation_gain_str[tile_row, tile_col] = "@"

# --- Step 1: Convert range to hundreds of feet and cap at 9 ---
elevation_gain_digit = (elevation_range_ft // 100).astype(int)
elevation_gain_digit = np.minimum(elevation_gain_digit, 9)  # cap at 9

# --- Step 2: Convert to string array and place '@' for Old Main ---
elevation_gain_digit_str = elevation_gain_digit.astype(str)
elevation_gain_digit_str[tile_row, tile_col] = "@"







# --- Step 1: Initialize empty ASCII array ---
ascii_map = np.empty_like(elevation_range_ft, dtype=str)

# --- Step 2: Apply rules ---
for i in range(elevation_range_ft.shape[0]):
    for j in range(elevation_range_ft.shape[1]):
        elev_gain = elevation_range_ft[i, j]
        if elev_gain < 25:
            c = "."
        elif elev_gain < 50:
            c = ","
        elif elev_gain < 125:
            c = "~"
        elif elev_gain < 350:
            c = "^"
        elif elev_gain < 750:
            c = "A"
        elif elev_gain < 1250:
            c = "M"
        else:
            c = "#"
        ascii_map[i, j] = c
print()
print()

# --- Step 3: Place "@" at Old Main ---
ascii_map[tile_row, tile_col] = "@"

ascii_map_str = "\n".join(" ".join(row) for row in ascii_map)







####################################################################################################

for row in elevation_str_array:
    print(" ".join(row))
print()
print()
for row in elevation_range_str:
    print(" ".join(row))
print()
print()
print("\nElevation gain per tile (hundreds of feet, 40x40):")
for row in elevation_gain_str:
    print(" ".join(row))
print()
print()
# --- Step 3: Print ASCII map ---
print("\nElevation gain per tile (0-9, 40x40):")
for row in elevation_gain_digit_str:
    print(" ".join(row))
print()
print()
for row in ascii_map:
    print(" ".join(row))


#print("Final elevation tile array (feet, 40x40):")
#print(elevation_tiles_ft)

# Save to a text file
with open("ascii_map.txt", "w") as f:
    f.write(ascii_map_str)

# Save to a text file
with open("ascii_elevation.txt", "w") as f:
    f.write(elevation_str)
