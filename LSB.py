"""
    modified LSB (least significant bit) algorithm for steganography (text hidden in an image)
    this method stores each bit of the secrect text into the image using a key in the form of
    0110000111000110 0110001011010110 11001011 =  419940193995      (this is an example) where
    (  row number  )|(column number )|(pattern) = key
    the picture is divided into a (row x col) array where in every block only one pixel can be changed
    the pixel's LSB bit is changed if the pattern bit is 0 otherwise it's the one before it that's changed for every color (RBG)
"""


from random import randint
from pathlib import Path
import docx
import cv2
import numpy as np



def plot(x, y):
    '''This function plots side by side the encoded image and the original one 
    it also labels both of them no matter what the size of the image is.
    
    Expected input :
        x the path for the first imgae
        y the path for the second image        
    Expected output:
        A window displaying two images side by side with labels
    '''
    
    # Reading images
    image = cv2.imread(y)
    image2 = cv2.imread(x)
    
    # Resizing the images
    x=image.shape[0]  
       
    #Every possible computer image width
    if x<=320 :
        s1=s2=0.7        
    elif 320<x<=640 :
        s1=s2=0.6 
    elif 640<x<=720:
        s1=s2=0.5 
    elif 720<x<=1024 :
        s1=s2=0.45
    elif 1024<x<=1280 :
        s1=s2=0.4
    elif 1280<x<=1366 :
        s1=s2=0.3
    elif 1366<x<=1600:
        s1=s2=0.25
    elif 1600<x<=1680 :
        s1=s2=0.18
    elif 1680<x<=1920 :
        s1=s2=0.15
    else :
        s1=s2=0.1      
    
    # Shaping the images
    image = cv2.resize(image, (0, 0), None, s1, s1)
    image2 = cv2.resize(image2, (0, 0), None, s2, s2)    
    
    #fitting text inside each picture
    thick = 1
    color=(255,255,255)
    line=cv2.LINE_AA
    fontfa = cv2.FONT_HERSHEY_SIMPLEX
    fontsc = 0.45
    while True:
        textSize1 = cv2.getTextSize('Original Image', fontFace=fontfa,fontScale=fontsc,thickness=thick)
        if image.shape[1] < textSize1[0][0]+6 :
            fontsc-=0.01
        else:
            break
    textSize2 = cv2.getTextSize('Encoded Image', fontFace=fontfa,fontScale=fontsc,thickness=thick)
    pos1=((image.shape[1]-textSize1[0][0])//2,textSize1[0][1]+5)
    pos2=((image.shape[1]-textSize2[0][0])//2 + image.shape[1],textSize1[0][1]+5)
    
    #stacking the images
    numpy_horizontal = np.hstack((image2, image))
    
    #inserting text
    cv2.putText(numpy_horizontal,'Original Image',pos1, fontfa, fontsc, color, thick , line)
    cv2.putText(numpy_horizontal,'Encoded  Image',pos2, fontfa, fontsc, color, thick , line)
    
    # Plotting images
    cv2.imshow( 'Displayer', numpy_horizontal)   
    cv2.waitKey(0)


def binaryUTF(char):
    """since each character in utf-8 encodng is saved in 1 to 4 bytes depending an the integer value of the character ,
    this function takes a character as an argument and returns its utf encoding in binary string form"""
    ch_en = char.encode("utf-8")  # hexadecimal utf-8 encoding  (string containing 1to4 elements)
    ch_bin = bin(ord(char))[2:]  # normal binary string representation of the character
    bin_utf = ""
    if len(ch_en) == 1:
        bin_utf = (8 - len(ch_bin)) * "0" + ch_bin  
    else:
        for i in range(len(ch_en)):
            bin_utf = bin_utf + bin(ch_en[i])[2:]
    return (bin_utf)


def charUTF(s):
    """this function takes in a binary string of a utf-8 encoded character, analyses it and returns the corresponding character"""
    char_s = ""
    l = len(s) // 8  # number of bytes
    if len(s) == 8:
        char = chr(int(s, 2))  # char is an ascii charcter
    else:
        for i in range(l - 1):
            char_s = s[-6:] + char_s  # for every byte except the first , only the last 6 bits are meaningful
            s = s[:-8]  # last byte is removed
        char_s = s[l:] + char_s  # depending on the number of bytes, the meaningful bits are extracted
        char = chr(int(char_s, 2))
    return char


def generate_key(tbn, rn, cn):  # tbn=total bit number  /// rn=picture row number /// cn=picture column number
    """this method generates the encoding key, ranomely picks row , column and pattern numbers as long as it is enough
    to store the text inside the image then returns these values and the corresponding key"""
    min_row = min(65535, rn)
    min_col = min(65535, cn)
    i = j = 1
    if (cn * rn * 3) <= tbn * 4 : #in case there is a risk the text size is too big for the picture 
        row=min_row
        col=min_col
    else:
        while True:
            if i + 10 < min_row and j + 10 < min_col: #this will make the function converge faster to the needed values
                i += 10
                j += 10
            row = randint(i, min_row)  # randomely generates the row numbers (it has to be less the the total numbers of rows and less then 2 bytes)
            col = randint(j, min_col)  # same as above
            if (col * row * 3) > tbn * 4:  # make sure there will be enough blocks to contain the hidden bits
                break
    pattern = randint(0, 255)  # randomely generate the pattern in 1 byte
    bin_row = bin(row)
    bin_col = bin(col)
    bin_pat = bin(pattern)
    key1 = (18 - len(bin_row)) * "0" + bin_row[2:]  # write the row in binary string form
    key2 = (18 - len(bin_col)) * "0" + bin_col[2:]  # same a above for col
    pat = (10 - len(bin_pat)) * "0" + bin_pat[2:]  # same as above for pattern
    key = int(key1 + key2 + pat, 2)  
    return ((row, col, pat, key))


def decode_key(key):
    """this method analyses the key , decodes it and returns the corresponding row,col and pattern values""" 
    bin_key = bin(key)
    keyb = (42 - len(bin_key)) * "0" + bin_key[2:]  # key in binary string form
    row = keyb[:16]  # write the row in binary string form
    col = keyb[16:32]  # same a above for col
    pat = keyb[32:]  # same as above for pattern
    return (int(row, 2), int(col, 2), pat)  


def code(img_dir, text):
    """this function encodes the text inside an image and generates a key corresponding to the encoding
    
    Expected input:
        img_dir path for the image to encode
        text the message to encode
        
     Expected output:
         Tuple containing the encoding key and the encoded image path
    """
    #read the picture , generate the key and initialise the variables :
    img = cv2.imread(img_dir,cv2.IMREAD_UNCHANGED)  # reading the image and storing it as a 3d array
    row = col = pati = pic = 0  # row = row iterator / col = column iterator / pati = pattern iterator / pic= pixel color iterator
    tup = generate_key(len(text) * 8, img.shape[0],img.shape[1])  # generate our key and the corresponding row number , column number and pattern
    pat = tup[2]  # pattern in binary string form
    
    #write every character into the picture :
    for char in text:
        x = binaryUTF(char)  # writing an integer in the form of a binary string (ex: '00101011')
        for char2 in x:
            y = "0" + bin(img[row][col][pic])[2:]  # creating a binary string representation of the pixel'color [pic] in postion (row,col) with at least 2 bits
            pat_i = int(pat[pati])
            if char2 != y[-1 - pat_i]:  # in case of difference of bits we change it
                y = y[:-1 - pat_i] + char2 + pat_i * y[-1]  # if the pattern bit is 0 y=y[:-1]+char2 otherwise y=y[:-2]+char2+y[-1]
            img[row][col][pic] = int(y, 2)  # new pixel color value
            pic += 1
            if pic == 3:  # if all of the pixel's colors have been changed we move to the next block/pixel
                pic = 0
                col += int(img.shape[1] / tup[1])  # we move to the next block (same row)
                if col >= img.shape[1]:  # if end of  a row is reached we move to the next row
                    row += int(img.shape[0] / tup[0])
                    col = 0
                    if row >= img.shape[0]:
                        return((-1, "ERROR : text file too big!!"))
            pati += 1
            if pati == len(pat):  # if the end if  the pattern is reached we restart at the beginning
                pati = 0
    
    #same process is done for '#' as for every other character
    a = ord('#')  # the character '#' represents here the end of file and it is used to know when the eof is reached while decoding
    x = (10 - len(bin(a))) * "0" + bin(a)[2:]
    for char2 in x:
        y = '0' + bin(img[row][col][pic])[2:]  
        if char2 != y[-1 - int(pat[pati])]:
            y = y[:-1 - int(pat[pati])] + char2 + int(pat[pati]) * y[-1]
        img[row][col][pic] = int(y, 2)
        pic += 1
        if pic == 3: 
            pic = 0
            col += int(img.shape[1] / tup[1])  
            if col >= img.shape[1]:  
                row += int(img.shape[0] / tup[0])
                col = 0
                if row >= img.shape[0]:
                    return ((-1, "ERROR : text file too big!!"))
        pati += 1
        if pati == len(pat):  
            pati = 0
            
    #save the new picture in the new path : 
    new_dir = img_dir[:img_dir.rfind('.')] + "_new" + img_dir[img_dir.rfind('.'):]
    cv2.imwrite(new_dir, img)  # saving the new image
    return ((tup[3], new_dir))  # returns the key and the new path 


def decode(img_dir, msg_dir, key):
    """this method reads the image, extracts the bits and it generates the corresponding character using the key
    as a guideline and then adds it to the text and finally it saves it in a .txt/docx file
    
    Expected input:
        img_dir path of the image to decode
        msg_dir path of the file
        key the key for decoding
        
    Expected output:
        file path of the decoded text
    """
    #read the steganography image, decode the key and initialise the variables :
    img2 = cv2.imread(img_dir)  # reading the image and storing it as a 3d array
    tup = decode_key(key)  # returns a tuple containing the row number , column number and pattern
    if tup[1] == 0 or tup[0] == 0: #since the key can never have null row and column values , this signifies a wrong key was provided
        return ("ERROR : wrong key")
    pat = tup[2]
    row = col = pic = pati = 0  # row = row iterator / col = column iterator / pati = pattern iterator / pic= pixel color iterator
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
            y = "0" + bin(img2[row][col][pic])[2:]  # binary string representation of an integer (in this case we need at least 2 bits)
            p = y[-1 - int(pat[ pati])]  # the hidden bit is added to the binary string (last bit or the one before depending on the pattern bit)
            x += p
            j += 1
            pic += 1
            if pic == 3:  # if all of the pixel's colors have been read we move to the next block/pixel
                pic = 0
                col += int(img2.shape[1] / tup[1])  # we move to the next block (same row)
                if (col >= img2.shape[1]):  # if end of  a row is reached we move to the next row
                    row += int(img2.shape[0] / tup[0])
                    col = 0
                    if row >= img2.shape[0]: #end of picture is reached: this means a wrong key was provided
                        return ("ERROR : wrong key")
            pati += 1
            if pati == 8:
                pati = 0
        
        #calculate number of bytes depending on the number of '1' read previously
        if j == 1:
            j = 7
        else:
            j = 8 - j + (j - 2) * 8
        for s in range(j):
            y = "0" + bin(img2[row][col][pic])[2:]  # binary string representation of an integer (in this case we need at least 2 bits)
            x += y[-1 - int(pat[pati])]  # the hidden bit is added to the binary string (last bit or the one before depending on the pattern bit)
            pic += 1
            if pic == 3:
                pic = 0
                col += int(img2.shape[1] / tup[1]) 
                if (col >= img2.shape[1]):  
                    row += int(img2.shape[0] / tup[0])
                    col = 0
                    if row >= img2.shape[0]:
                        return ("ERROR : wrong key")
            pati += 1
            if pati == 8:
                pati = 0
        try:    
            c = charUTF(x)
        except ValueError : #if this error is detected , this means the binary string found doesn't correspond to any utf-8 character
            return("ERROR : wrong key") #which means either the picture doesn't have the text or teh wrong key was provided
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
    return (direc)
