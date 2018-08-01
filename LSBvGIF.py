"""
    modified LSB (least significant bit) algorithm for steganography (text hidden in an image)
    this method stores each bit of the secrect text into the image using a key as a pattern
    0110000111000110011000101101011011001011 =  419940193995      (this is an example) where
                    (pattern)                =       key
    the pixel's LSB bit is changed if the pattern bit is 0 otherwise it's the one before it that's changed 
    changed pixels are chosen in a clockwise spiral order
    this file is specific for GIFs
"""

from PIL import Image
from pathlib import Path
import docx
import LSB
import pyglet
from win32api import GetSystemMetrics


def conv_inc(i,j,row,col,count):
    """given the picture dimentions and the current pixel position and border
    this method determines the next position """
    if j==count:
        if i!=row-count-1:
            i+=1
        else:
            j+=1
    elif i==row-count-1:
        if j==col-count-1:
            i-=1
        else:
            j+=1
    elif j==col-count-1:
        if i==count:
            j-=1
        else:
            i-=1
    else:
        j-=1
    if i==j==count:
        count+=1
        i=count
        j=count
    return(i,j,count)

def plot(x, y, ressources):
    '''This function plots side by side the encoded image and the original one 
    it also labels both of them no matter what the size of the image is.
    Expected input:
        x first gif file name
        y second gif file name
        ressources  the ressources directory
    Expected output:
        Two windows side by side displaying the encoded and original GIF'''

    pyglet.resource.path = [ressources]
    pyglet.resource.reindex()
    # picking the gif
    org_gif = x[x.rfind('/')+1:]
    animation = pyglet.resource.animation(org_gif)
    sprite = pyglet.sprite.Sprite(animation)
    
    enc_gif=y[y.rfind('/')+1:]
    animation2 = pyglet.resource.animation(enc_gif)
    sprite2 = pyglet.sprite.Sprite(animation2)
    
    # create a window and set it to the gif size
    win = pyglet.window.Window(width=sprite.width, height=sprite.height, caption="Original GIF")
    win2= pyglet.window.Window(width=sprite2.width, height=sprite2.height, caption="Encoded GIF")
    
    # setting display locations and icon
    
    ws=GetSystemMetrics(0)
    hs=GetSystemMetrics(1)
    
    x1=(ws//2)-sprite.width
    y1=(hs//2)-sprite.height
    win.set_location(x1, y1)
    
    x2=x1+sprite.width+3
    win2.set_location(x2, y1)
    
    #icon=pyglet.image.load(display.ico)
    #win.set_icon(icon)
    #win2.set_icon(icon)
    
    # drawing windows
    @win.event
    def on_draw():
        win.clear()    
        sprite.draw()       
        
    @win2.event
    def on_draw():
        win2.clear() 
        sprite2.draw()
    # running the applet   
    pyglet.app.run()


def codeGIF(img_dir, text):
    """this function encodes the text inside a gif and generates a key corresponding to the encoding
    
    Expected input:
        img_dir path for the gif to encode
        text the message to encode
        
     Expected output:
         Tuple containing the encoding key and the encoded gif path
         """
    
    #read the gif , generate the key and initialise the variables :
    imgf=Image.open(img_dir)
    img=imgf.load() #read the pixel palete indices
    row = col = pati=count=  0  # row = row iterator / col = column iterator / pati = pattern iterator / count=border iterator
    tup = LSB.generate_key(len(text) * 8, imgf.size[0],imgf.size[1])  # generate our key
    key=tup[3]
    bin_key = bin(key)
    pat = (42 - len(bin_key)) * "0" + bin_key[2:]
    
    #write every character into the picture :
    for char in text:
        x = LSB.binaryUTF(char)  # writing an integer in the form of a binary string (ex: '0101011')
        for char2 in x:
            y = "0" + bin(img[row,col])[2:]  # creating a binary string representation of the pixel in postion (row,col) with at least 2 bits
            pat_i = int(pat[pati])
            if char2 != y[-1 - pat_i]:  # in case of difference of bits we change it
                y = y[:-1 - pat_i] + char2 + pat_i * y[-1]  # if the pattern bit is 0 y=y[:-1]+char2 otherwise y=y[:-2]+char2+y[-1]
            img[row,col] = int(y, 2)  # new pixel color value
            if count<(imgf.size[0]-count-1) and count<(imgf.size[1]-count-1):
                row,col,count=conv_inc(row,col,imgf.size[0],imgf.size[1],count)
            else:
                imgf.close()
                return ((-1, "ERROR : text file too big!!"))
            pati += 1
            if pati == len(pat):  # if the end if  the pattern is reached we restart at the beginning
                pati = 0
    
    #same process is done for '#' as for every other character
    a = ord('#')  # the character '#' represents here the end of file and it is used to know when the eof is reached while decoding
    x = (10 - len(bin(a))) * "0" + bin(a)[2:]
    for char2 in x:
        y = '0' + bin(img[row,col])[2:]  # binary string representation of an integer (in the form of "0b0101")
        if char2 != y[-1 - int(pat[pati])]:
            y = y[:-1 - int(pat[pati])] + char2 + int(pat[pati]) * y[-1]
        img[row,col]= int(y, 2)
        if count<(imgf.size[0]-count-1) and count<(imgf.size[1]-count-1):
            row,col,count=conv_inc(row,col,imgf.size[0],imgf.size[1],count)
        else:
            imgf.close()
            return ((-1, "ERROR : text file too big!!"))
        pati += 1
        if pati == len(pat):  # if the end if  the pattern is reached we restart at the beginning
            pati = 0
    
    #save the new gif in the new path :
    new_dir = img_dir[:img_dir.rfind('.')] + "_new" + img_dir[img_dir.rfind('.'):]
    imgf.save(new_dir,save_all=True,duration=imgf.info["duration"],loop=imgf.info["loop"])
    imgf.close()
    return ((tup[3], new_dir))  # returns the key


def decodeGIF(img_dir, msg_dir, key):
    """this method basically reads the image, extracts the bits and it generates the corresponding character using the key
    as a guideline and then adds it to the text and finally it saves it in  .txt/docx file
    
    Expected input:
        img_dir path of the gif to decode
        msg_dir path of the file
        key the key for decoding
        
    Expected output:
        file path of the decoded text
        """
    #read the steganography gif, decode the key and initialise the variables :
    imgf2 = Image.open(img_dir)
    img2=imgf2.load()
    bin_key = bin(key)
    pat = (42 - len(bin_key)) * "0" + bin_key[2:]
    row = col = pati = count = 0  # row = row iterator / col = column iterator / pati = pattern iterator / counter=border iterator
    text2 = ""  # variable that will contain the hidden message
    c = ''
    Aslash=False # true if the most recent character extracted was '\'
    
    #analyse picture until a '#' was detected
    while (c != '#') or Aslash==True:
        if c=="#":
            text2=text2[:-1]+c #ignores '\' if there was a '\#' written
        else:
            text2 += c        
        x = ""  # variable representing the binary string of the character
        p = "1"
        j = 0
        
        #read bits until a '0' is reached
        while p != "0":
            y = "0" + bin(img2[row,col])[2:]  # binary string representation of an integer (in this case we need at least 2 bits)
            p = y[-1 - int(pat[ pati])]  # the hidden bit is added to the binary string (last bit or the one before depending on the pattern bit)
            x += p
            j += 1
            if count<(imgf2.size[0]-count-1) and count<(imgf2.size[1]-count-1):
                row,col,count=conv_inc(row,col,imgf2.size[0],imgf2.size[1],count)
            else:
                imgf2.close()
                return ("ERROR : wrong key")
            pati += 1
            if pati == len(pat):
                pati = 0

        #calculate number of bytes depending on the number of '1' read previously
        if j == 1:
            j = 7
        else:
            j = 8 - j + (j - 2) * 8
        for s in range(j):
            y = "0" + bin(img2[row,col])[2:]  # binary string representation of an integer (in this case we need at least 2 bits)
            x += y[-1 - int(pat[pati])]  # the hidden bit is added to the binary string (last bit or the one before depending on the pattern bit)
            if count<(imgf2.size[0]-count-1) and count<(imgf2.size[1]-count-1):
                row,col,count=conv_inc(row,col,imgf2.size[0],imgf2.size[1],count)
            else:
                imgf2.close()
                return ("ERROR : wrong key")
            pati += 1
            if pati == len(pat):
                pati = 0
        try:    
            c = LSB.charUTF(x)
        except ValueError : #if this error is detected , this means the binary string found doesn't correspond to any utf-8 character
            imgf2.close() #which means either the picture doesn't have the text or teh wrong key was provided
            return("ERROR : wrong key")
        if c=='\\' :
            Aslash=True
        elif c!='#':
            Aslash=False
    
    #check if the message file exists and choose the new path accordingly:
    file = Path(msg_dir)
    if file.is_file():
        direc = msg_dir
    else:
        direc = img_dir[:-4] + "_hidden_text.txt"
    
    #if the file is a docx file :
    if direc[-3:] != "txt":
        doc = docx.Document()
        doc.add_paragraph(text2)
        doc.save(direc)
    else:
        with open(direc, "w", encoding="utf-8") as f2:  # creating the new file and writing the hidden message
            f2.write(text2)
    imgf2.close()
    return (direc)
