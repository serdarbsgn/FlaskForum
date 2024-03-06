import os
project_dir = os.path.dirname(os.path.abspath(__file__))
profile_photos_dir = "/photos/users/"

def listify(map):
    templist = []
    for row in map:
        dicx = {}
        for key,val in row.items():
            dicx[key] = val
        templist.append(dicx)
    return templist

def redirect(link):
    return '<script>window.location.href = "'+link+'";</script>'

def open_window(link):
    return '<script>window.open("'+link+'", "newwindow", "height=300,width=500");</script>'