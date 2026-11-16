from pathlib import Path
import rasterio

DATA_DIR = Path("data/raw")

files = list(DATA_DIR.rglob("*.tif")) + list(DATA_DIR.rglob("*.tiff"))

if not files:
    print("No GeoTIFF datasets found.")
else:
    for file in files:
        print(f"\nTesting: {file}")

        try:
            with rasterio.open(file) as dataset:
                print("Width:", dataset.width)
                print("Height:", dataset.height)
                print("Bands:", dataset.count)
                print("CRS:", dataset.crs)
                print("Bounds:", dataset.bounds)
                print("Resolution:", dataset.res)
                print("Data type:", dataset.dtypes)

                sample = dataset.read(1, masked=True)

                print("Valid pixels:", sample.count())
                print("Dataset readable: YES")

        except Exception as error:
            print("Dataset readable: NO")
            print("Error:", error)