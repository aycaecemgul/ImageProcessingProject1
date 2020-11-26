import base64
import base64
import io
import os
import PIL
from PIL import Image
import PySimpleGUI as sg
import cv2 as cv
import numpy as np
from numpy import asarray
from skimage.transform import rotate
import Main
from io import BytesIO

def main():
    sg.theme("Black")

    # Define the window layout
    layout = [
        [sg.HorizontalSeparator(color="White")],
        [sg.Text("Image Processing Project 1 By Ayça Ecem Gül", size=(60, 1), justification="center")],
        [sg.HorizontalSeparator(color="White")],
        [sg.Text('Choose an image', size=(14, 1)), sg.Input(key='-FILE-', enable_events=True), sg.FileBrowse()],
        [sg.Image(key='-IMAGE-',enable_events=True)],
        [sg.Image(key='-IMAGE1-',enable_events=True)],
        [sg.HorizontalSeparator(color="White")],
        [
            sg.Text("Rotate",size=(14,1)),
            sg.Button("90",size=(8,1),key="-ROT-90-",enable_events=True),
            sg.Button("180", size=(8, 1),key="-ROT-180-", enable_events=True),
            sg.Button("270",size=(8, 1),key="-ROT-270-", enable_events=True)
        ],
        [
            sg.Text("Resize", size=(14, 1)),
            sg.Input(key="-X-",size=(8,1)),sg.Input(key="-Y-",size=(8,1)),
            sg.Button("Apply", size=(8, 1), key="-RESIZE-APPLY-", enable_events=True)
        ],
        [
            sg.Text("Rescale",size=(14, 1)),
            sg.Input(key="-RESCALE-AMOUNT-", size=(8, 1)),
            sg.Button("Apply", size=(8, 1), key="-RESCALE-APPLY-", enable_events=True)
        ],
        [
            sg.Text("Flip",size=(14,1)),
            sg.Button("Horizontal",key="-H-FLIP-", size=(8, 1), enable_events=True),
            sg.Button("Vertical",key="-V-FLIP-" ,size=(8, 1), enable_events=True)
        ],
        [
            sg.Text("Crop", size=(14, 1)),
            sg.Input(key="-CROPX1-",size=(5,1)),sg.Input(key="-CROPX2-",size=(5,1)),sg.Input(key="-CROPY1-",size=(5,1)),sg.Input(key="-CROPY2-",size=(5,1)),
            sg.Button("Apply", size=(8, 1), key="-CROP-APPLY-", enable_events=True)
        ],
        [
            sg.Text("Swirl", size=(14, 1)),
            sg.Text("Strength", size=(10, 1)),
            sg.Slider(
                (0, 500),
                250,
                1,
                orientation="h",
                size=(10, 10),
                key="-SWIRL-SLIDER-",
            ),
            sg.Text("Radius", size=(10, 1)),
            sg.Slider(
                (0, 500),
                250,
                1,
                orientation="h",
                size=(10, 10),
                key="-SWIRL-SLIDER2-",
            ),
            sg.Button("Apply", size=(8, 1), key="-SWIRL-APPLY-", enable_events=True)
        ],

        [
            sg.HorizontalSeparator(color="White")
        ],
        [
            sg.Text("Histogram Equalization",size=(24,1))
        ],
        [
            sg.Text("Choose an image to equalize" ,size=(24, 1)), sg.Input(key='-FILE2-', enable_events=True), sg.FileBrowse()
        ],
        [
            sg.HorizontalSeparator(color="White")
        ],
        [
            sg.Text("Görüntü İyileştirme İşlemleri",size=(24, 1))],
        [sg.Text("Choose a filter:",size=(12, 1)),
         sg.Combo(['Wiener',"Prewitt V","Prewitt H", "Hessian",'Median ', "Meijering","Frangi","Laplacian", "Gaussian",'Sato'], enable_events=True,size=(17, 4), key='-IYI-COMBO-'),
         sg.Slider(
             (0, 255),
             128,
             1,
             orientation="h",
             size=(20, 10),
             key="-IYI-SLIDER-",
         ),
         sg.Button("Apply", size=(8, 1), key="-IYILESTIRME-APPLY-", enable_events=True)],
        [
            sg.HorizontalSeparator(color="White")
        ],
        [
            sg.Text("Yoğunluk Dönüşümü İşlemleri")
        ],
        [
            sg.Combo(["","","","","",""],size=(17,3),enable_events=True,key="-YOG-COMBO-"),
            sg.Button("Apply", size=(10, 1), key="-YOG-APPLY-", enable_events=True)
        ],
        [
            sg.HorizontalSeparator(color="White")
        ],
        [sg.Text("Morphological Operations", size=(18, 1))],
        [
            sg.Text("Choose an operation:", size=(18, 1)),
            sg.Combo(['Dilation', 'Erosion', 'Thin','Skeletonize','Skeletonize-3D',
                      'Opening',"Closing","Convex Hull","White Tophat","Black Tophat"],
                     size=(17, 4), key='-MORP-COMBO-',enable_events=True),
         sg.Button("Apply", size=(10, 1), key="-IYILESTIRME-APPLY-", enable_events=True)
         ],
        [
            sg.HorizontalSeparator(color="White")
        ],
        [sg.Text("Try Ayça's special instagram filter!", size=(27, 1)),
         sg.Button("Apply", size=(8, 1), key="-INSTA-APPLY-", enable_events=True)
         ],
        [
            sg.Button("Save", size=(8, 1)),
         sg.Button("Exit", size=(8, 1))
        ]
    ]

    # Create the window and show it without the plot
    window = sg.Window("OpenCV Integration", layout, location=(500,20),resizable=True)

    def convert_to_bytes(file_or_bytes, resize=None):
        '''
        Will convert into bytes and optionally resize an image that is a file or a base64 bytes object.
        Turns into  PNG format in the process so that can be displayed by tkinter
        :param file_or_bytes: either a string filename or a bytes base64 image object
        :type file_or_bytes:  (Union[str, bytes])
        :param resize:  optional new size
        :type resize: (Tuple[int, int] or None)
        :return: (bytes) a byte-string object
        :rtype: (bytes)
        '''
        if isinstance(file_or_bytes, str):
            img = PIL.Image.open(file_or_bytes)
        else:
            try:
                img = PIL.Image.open(io.BytesIO(base64.b64decode(file_or_bytes)))
            except Exception as e:
                dataBytesIO = io.BytesIO(file_or_bytes)
                img = PIL.Image.open(dataBytesIO)

        cur_width, cur_height = img.size
        if resize:
            new_width, new_height = resize
            scale = min(new_height / cur_height, new_width / cur_width)
            img = img.resize((int(cur_width * scale), int(cur_height * scale)), PIL.Image.ANTIALIAS)
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        if event == sg.WIN_CLOSED or event == 'Exit':
            break
        if event == '-FILE-':
            filename = values['-FILE-'] #!!!!!!!!!!
            image=Image.open(filename)
            filename=filename[:-4] + '-converted.png'
            image.save(filename)
            window['-IMAGE-'].update(data=convert_to_bytes(filename, resize=(400,400)))
        elif event == "-ROT-90-" :
            filename= Main.rotate_image_90(filename)
            window['-IMAGE-'].update(data=convert_to_bytes(filename, resize=(400,400)))

        elif event == "-ROT-180-":
            filename = Main.rotate_image_180(filename)
            window['-IMAGE-'].update(data=convert_to_bytes(filename, resize=(400, 400)))

        elif event == "-ROT-270-":
            filename = Main.rotate_image_270(filename)
            window['-IMAGE-'].update(data=convert_to_bytes(filename, resize=(400, 400)))

        elif event == "-H-FLIP-":
            filename= Main.h_flip(filename)
            window['-IMAGE-'].update(data=convert_to_bytes(filename, resize=(400, 400)))

        elif event == "-V-FLIP-":
            filename= Main.v_flip(filename)
            window['-IMAGE-'].update(data=convert_to_bytes(filename, resize=(400, 400)))

        elif event=="-RESIZE-APPLY-":
            if(int(values["-X-"])>0 and int(values["-X-"])>0):
                X=int(values["-X-"])
                Y=int(values["-Y-"])
                filename=Main.resize_image(filename,X,Y)
                window['-IMAGE-'].update(data=convert_to_bytes(filename, resize=(X, Y)))
                # elif values["-THRESH-"]:
        elif event=="-SWIRL-APPLY-":
            strength=float(values["-SWIRL-SLIDER-"])
            radius=float(values["-SWIRL-SLIDER2-"])
            filename=Main.swirl_image(filename,strength,radius)
            window['-IMAGE-'].update(data=convert_to_bytes(filename,resize=(400, 400)))

        #!!!!!!!!!!!!!!
        elif event=="-CROP-APPLY-":
            x1=int(values["-CROPX1-"])
            x2 = int(values["-CROPX2-"])
            y1=int(values["-CROPY1-"])
            y2=int(values["-CROPY2-"])

            filename=Main.crop_image(filename,x1,x2,y1,y2)
            window['-IMAGE-'].update(data=convert_to_bytes(filename, resize=(400, 400)))
        #!!!!!!!!!!!!!!!!!!!!!!
        elif event == "-RESCALE-APPLY-":
            amount=float(values["-RESCALE-AMOUNT-"])
            filename=Main.rescale_image(filename,amount)
            window['-IMAGE-'].update(data=convert_to_bytes(filename, resize=(400, 400)))

        # elif values["-HUE-"]:
        #     frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        #     frame[:, :, 0] += int(values["-HUE SLIDER-"])
        #     frame = cv2.cvtColor(frame, cv2.COLOR_HSV2BGR)
        # elif values["-ENHANCE-"]:
        #     enh_val = values["-ENHANCE SLIDER-"] / 40
        #     clahe = cv2.createCLAHE(clipLimit=enh_val, tileGridSize=(8, 8))
        #     lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        #     lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        #     frame = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        #
        # imgbytes = cv2.imencode(".png", frame)[1].tobytes()
        # window["-IMAGE-"].update(data=imgbytes)

    window.close()

main()