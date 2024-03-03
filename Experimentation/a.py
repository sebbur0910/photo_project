import binascii
import PIL.Image
import io

file_path = "C:\\Users\\sebbur0910\\OneDrive - Highgate School\\School\\Year 12\\photo_project\\Experimentation\\Capture.png"
with PIL.Image.open(file_path) as img:
#Converts the image to 1s and 0s
    img.load()
    bytestream = io.BytesIO()
    img.save(bytestream, format="PNG")
    hex_data = bytestream.getvalue()
    data = binascii.hexlify(hex_data)
    img = bin(int(data, 16))
    img = img[2:].zfill(32)

   # print(img)

def convertToBinaryData(filename):
    # Convert digital data to binary format
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData

print(convertToBinaryData(file_path))