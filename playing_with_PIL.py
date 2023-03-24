from PIL import Image

filename = "C:/Users/sebbur0910/OneDrive - Highgate School/School/Year 12/paging.jpeg"

with Image.open(filename) as img:
    img.load()
    img.save("paging.jpeg")
 #   img.show()

with open(filename, 'rb') as file:
    blobData = file.read()
print(blobData)

