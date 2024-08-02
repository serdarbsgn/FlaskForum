import os
project_dir = os.path.dirname(os.path.abspath(__file__))
profile_photos_dir = "/photos/users/"
product_photos_dir = "/photos/products/"

def listify(map):
    templist = []
    for row in map:
        dicx = {}
        for key,val in row.items():
            dicx[key] = val
        templist.append(dicx)
    return templist

