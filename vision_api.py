import os
import io
from google.cloud import vision
from PIL import Image


def detect_crop_hints(path):
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    crop_hints_params = vision.CropHintsParams(aspect_ratios=[1])
    image_context = vision.ImageContext(crop_hints_params=crop_hints_params)

    response = client.crop_hints(image=image, image_context=image_context)
    hints = response.crop_hints_annotation.crop_hints

    vertices = []
    for vertex in hints[0].bounding_poly.vertices:
        vertices.append({'x': vertex.x, 'y': vertex.y})

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

    return vertices


def crop_file(path, bounds):
    im = Image.open(path)
    im_crop = im.crop((bounds[3]['x'], bounds[1]['y'], bounds[1]['x'], bounds[3]['y']))
    im_crop.save(os.path.join('resources/trim', os.path.basename(path)), quality=95)


def upload_file(file, filename, directory):
    file.save(os.path.join(directory, filename))
