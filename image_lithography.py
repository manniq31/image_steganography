from PIL import Image
from simplecrypt import encrypt, decrypt
import random

keys = []
yes = ["Yes", "Y", "y", "yes", ""]

def generateKeys():
    keys.clear()
    path = input("store keys as: ")
    for i in range(0, 6):
        x = randomColor()
        if x not in keys:
            keys.append(x)
    print("keys: ", keys)
    with open(path, "w") as file:
        file.write(str(keys))
        print("keys stored successfully")


def importKeys():
    keys.clear()
    path = input("load keys from: ")
    with open(path, "r") as file:
        for key in (eval(file.readline())):
            if type(key) == int:
                keys.append((key,) * 3)  # generate RGB tuple from 1 channel image
            else:
                keys.append(key)
    print("keys: ", keys)


def decode():
    if not keys:
        print("you have to import keys first")
        input("press enter to continue ")
        importKeys()
    counter = 0
    text = ""
    img = Image.open(input("input image path: "))
    pix = img.load()
    for y in range(0, img.size[1]):
        for x in range(0, img.size[0]):
            if pix[x, y] in keys:
                text += chr(counter)
                counter = 0
            counter += 1
    print("text: ", text)


def encode():
    if not keys:
        while True:
            print("you have to generate(1) or import(2) keys first")
            selection = input("enter your selection (1 or 2): ")
            if selection == "1":
                generateKeys()
                break
            elif selection == "2":
                importKeys()
                break
            else:
                print("invalid input")
    text = input("enter a String to encode: ")
    path = input("store image as: ") + ".png"
    pixels = 1  # the pixel-0 at the beginning
    for c in text: pixels += ord(c)
    width = 0
    height = 0
    # generate an approximately 16:9 image
    while width * height < pixels:
        width += 1
        if height / width < 0.53: height += 1
    image = []
    i = 0
    counter = 0
    for pixel in range(0,height*width):
        if i < len(text):
            if counter == ord(text[i]):
                pixel = random.choice(keys)
                counter = 0
                i += 1
            else:
                while True:
                    color = randomColor()
                    if color not in keys:
                        break
                pixel = color
        else:
            while True:
                color = randomColor()
                if color not in keys: break
            pixel = color
        counter += 1
        image.append(pixel)
    Image.frombytes("R,G,B",(width,height), bytes(image))
    print("image was stored successfully")
    print("pixels needed: ", pixels, "\npixels used: ", width * height)


def randomColor():
    color = []
    for i in range(0, 3):
        color.append(random.randint(0, 255))
    return tuple(color)


def generatePassword():
    password_location = input("store the password as: ")
    min_char = 80
    max_char = 120
    byte_list = []
    for i in range(random.randint(min_char, max_char)):
        byte_list.append(random.getrandbits(8))
    password = bytes(byte_list)
    with open(password_location, "wb") as file:
        file.write(password)
        print("password stored successfully")
    return password


def hideString():
    while True:
        path = input("choose a png image to hide string in: ")
        text = input("enter the String you want to hide: ")
        img = Image.open(path)
        pixels = 0
        if input("encrypt the string? [Y/n]: ") in yes:
            password = generatePassword()
            secret = encrypt(password, text)
        else:
            secret = bytes(text.encode('utf-8'))
        for b in secret:
            pixels += b + 1
        if pixels < img.width * img.height: break
        print("the image is to small to contain that string\nchoose another one with more pixels")
    hide(secret, path)


def hideFile():
    while True:
        file_path = input("file you want to hide: ")
        image_path = input("image you want to hide the file in: ")
        img = Image.open(image_path)
        file = open(file_path, "rb").read()
        if input("encrypt the file? [Y/n]: ") in yes:
            password = generatePassword()
            secret = encrypt(password, file)
        else:
            secret = file
        pixels = 0
        for b in secret: pixels += b + 1
        if pixels < img.width * img.height: break
        print("the image is to small to contain that string\nchoose another one with more pixels")
    hide(secret, image_path)


def hide(secret, path):
    # use the last bit of every color for every pixel to store if its relevant for the string
    counter = 0
    with Image.open(path) as img:
        data = img.getdata()
        mode = img.mode
        size = img.size
    color = []
    new_image= []
    n = 0
    for pixel in data:
        for i in range(0, 3):
            color.append(pixel[i])
            if n < len(secret):
                if counter == secret[n]:
                    color[i] = color[i] | 1
                    counter = 0
                    n += 1
                else:
                    color[i] = color[i] & 254
                    counter += 1
            else:
                color[i] = color[i] & 254
                counter += 1
        new_image.append(tuple(color))
        color = []
    Image.frombytes(mode, size, new_image).save(path)
    print("immage saved succesfully")



def discover():
    image_path = input("choose an image to extract data from: ")
    secret = discoverSecret(image_path)
    if input("is the data encrypted? [Y/n]: ") in yes:
        password_location = input("load password from (leave empty for manual input): ")
        if not password_location:
            password = input("password: ")
        else:
            with open(password_location, "rb") as file:
                password = file.read()
        data = decrypt(password, secret)
    else: data = secret
    try:
        text = data.decode('utf-8')
        if input("the data is text\ndo you want to display it? [Y/n]: ") in yes:
            print("text:\n", text)
        file_path = input("store as (empty for not storing):") is not ""
    except UnicodeDecodeError:
        file_path = input("the data can't be shown as text\nstore discovered file as: ")
    if file_path is not "":
        with open(file_path, "wb") as file:
            file.write(secret)
        print("file stored succesfully")

def discoverSecret(image_path):
    with Image.open(image_path) as img:
        data = img.getdata()
    counter = 0
    secret = []
    for pixel in data:
            for i in range(0, 3):
                if pixel[i] & 1:
                    secret.append(counter)
                    counter = 0
                else:
                    counter += 1
    return bytes(secret)


while True:
    task = input(
        "1) encode\n2) decode\n3) generate Keys\n4) import Keys\n5) hide string in existing image\n"
        "6) hide file in image\n7) discover file/string\ninput: ")
    if task == "1":
        encode()
    elif task == "2":
        decode()
    elif task == "3":
        generateKeys()
    elif task == "4":
        importKeys()
    elif task == "5":
        hideString()
    elif task == "6":
        hideFile()
    elif task == "7":
        discover()
    elif task == "exit":
        exit()
    else:
        print("invalid input")
    input("press enter to continue ")