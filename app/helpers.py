import os
project_dir = os.path.dirname(os.path.abspath(__file__))
flask_dir = os.path.abspath(os.path.join(project_dir, '..', '..', 'FlaskForum', 'app'))
profile_photos_dir = "photos/users"
product_photos_dir = "photos/products"

def listify(map):
    templist = []
    for row in map:
        dicx = {}
        for key,val in row.items():
            dicx[key] = val
        templist.append(dicx)
    return templist

def limit_line_breaks(content:str, max_line_breaks=255):
    lines = content.splitlines()
    new_content = ""
    for i,line in enumerate(lines):
        if i<max_line_breaks:
            new_content += f'{line}<br>'
        else:
            new_content += ' '.join(lines[i:])
            break
    return new_content.rstrip('<br>')
