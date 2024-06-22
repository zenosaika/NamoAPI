import ee

ee.Authenticate(auth_mode='notebook')
ee.Initialize(project='ee-owlmen2546')

def get_map(input_x, input_y):

    x = ee.Number(input_x)
    y = ee.Number(input_y)
    distance = ee.Number(0.001)

    lowerLeft = ee.Geometry.Point([x.subtract(distance), y.subtract(distance)])
    lowerRight = ee.Geometry.Point([x.add(distance), y.subtract(distance)])
    upperLeft = ee.Geometry.Point([x.subtract(distance), y.add(distance)])
    upperRight = ee.Geometry.Point([x.add(distance), y.add(distance)])
    geometry = ee.Geometry.Polygon([lowerLeft, lowerRight, upperRight, upperLeft, lowerLeft])

    dataset = (
        ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
        .filterDate('2024-05-22', '2024-06-22')
        # Pre-filter to get less cloudy granules.
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))
        .filterBounds(geometry) # Filter data to your AOI
    )

    img = dataset.mosaic().clip(geometry)

    visualization = {
        'min': 0,
        'max': 3000,
        'bands': ['B4', 'B3', 'B2'],
    }

    download_url = img.visualize(**visualization).getDownloadURL({
    'scale': 1,
    'format': 'png'
    })

    return download_url