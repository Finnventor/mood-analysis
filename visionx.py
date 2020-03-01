import io
import os
import glob
#import sys
#sys.path.append('/Users/samuelchu/Library/Python/3.7/')
from google.cloud import vision
from google.cloud.vision import types

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'apikey.json'

client = vision.ImageAnnotatorClient()
'''
file_name = os.path.join(
    os.path.dirname(__file__),
    'sick4.jpg')
with io.open(file_name,'rb') as image_file:
    content = image_file.read()

image = types.Image(content = content)

response = client.label_detection(image = image)

labels = response.label_annotations

print("Labels:")

for label in labels:
    print(label.description)
'''

def detect_faces(content):
    """Detects faces in an image."""
    image = vision.types.Image(content=content)

    response = client.face_detection(image=image)
    faces = response.face_annotations

    # Names of likelihood from google.cloud.vision.enums
    likelihood_name = ('UNKNOWN', 'VERY_UNLIKELY', 'UNLIKELY', 'POSSIBLE',
                       'LIKELY', 'VERY_LIKELY')
    print('Faces:')

    coords = []

    for face in faces:
#        print(dir(face))

        print('anger: {}'.format(likelihood_name[face.anger_likelihood]))
        print('joy: {}'.format(likelihood_name[face.joy_likelihood]))
        print('surprise: {}'.format(likelihood_name[face.surprise_likelihood]))
        print('sorrow: {}'.format(likelihood_name[face.sorrow_likelihood]))

        vertices = ([(vertex.x, vertex.y)
                    for vertex in face.bounding_poly.vertices])
        coords.append(vertices)

        print('face bounds: {}'.format((vertices)))

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))
    return faces, coords



def localize_objects(image):
    """Localize objects in the image on Google Cloud Storage

    Args:
    uri: The path to the file in Google Cloud Storage (gs://...)
    """
    from google.cloud import vision
    client = vision.ImageAnnotatorClient()

    objects = client.object_localization(
        image=image).localized_object_annotations

    print('Number of objects found: {}'.format(len(objects)))
    for object_ in objects:
        print('\n{} (confidence: {})'.format(object_.name, object_.score))
        print('Normalized bounding polygon vertices: ')
        for vertex in object_.bounding_poly.normalized_vertices:
            print(' - ({}, {})'.format(vertex.x, vertex.y))
import os
def clear_directory(path):
    for file in glob.glob(f"{path}/*.jpg"):
        os.remove(file)

file_names = input("Enter file names > ").split()

from PIL import Image, ImageDraw
image_number = 0

clear_directory("joyful")
clear_directory("angry")
clear_directory("sorrow")
clear_directory("other")

'''
for file_name in file_names:#glob.glob("photos/*.jpg"):
    print(f"Analyzing {file_name}")
    with io.open(file_name,'rb') as image_file:
        content = image_file.read()

    image = Image.open(file_name)

    objects = client.object_localization(image=types.Image(content = content)).localized_object_annotations

    print('Number of objects found: {}'.format(len(objects)))
    
    for obj in objects:
        if obj.name == "Person":
            x = []
            y = []
            for vertex in obj.bounding_poly.normalized_vertices:

                x.append(vertex.x)
                y.append(vertex.y)
            coords = (min(x)*image.width, min(y)*image.height, max(x)*image.width, max(y)*image.height)
            coords = [int(c) for c in coords]
            print(coords)
            i = image.copy().crop(coords).save(f"faces/person_{image_number}.jpg")
            #images.append(image.copy().crop(coords).tobytes())
            image_number += 1
'''
anger = joy = sorrow = other = total = 0
width = 2

for file_name in file_names:#glob.glob("faces/*.jpg"):
    with io.open(file_name,'rb') as image_file:
        content = image_file.read()

    image = Image.open(file_name)
    output = image.copy()
    draw = ImageDraw.Draw(output)

    faces, coords = detect_faces(content)
    for face, coord in zip(faces, coords):
        
        #print(coords)
        #x = [i[0] for i in coord]
        #y = [i[1] for i in coord]
        coord = coord[0] + coord[2]
        #coords = (min(x)*image.width, min(y)*image.height, max(x)*image.width, max(y)*image.height)
        #coords = [int(c) for c in coords]
        img = image.copy().crop(coord)

        if face.anger_likelihood > 2:
            anger += 1
            img.save(f"angry/{anger}.jpg")
            draw.rectangle(coord, outline="#ff0000", width=width)
        elif face.joy_likelihood > 2:
            joy += 1
            img.save(f"joyful/{joy}.jpg")
            draw.rectangle(coord, outline="#00ff00", width=width)
        elif face.sorrow_likelihood > 2:
            sorrow += 1
            img.save(f"sorrow/{sorrow}.jpg")
            draw.rectangle(coord, outline="#0000ff", width=width)
        else:
            other += 1
            img.save(f"other/{other}.jpg")
            draw.rectangle(coord, outline="#000000", width=width)
        total += 1

    output.save(f"{file_name}_analyzed.jpg")

print(f"Detected {joy} joyful people, {sorrow} sad people, and {anger} angry people, out of {total} people.")

#    detect_faces(file_name)
#    localize_objects(image)
#    response = client.label_detection(image = image)
