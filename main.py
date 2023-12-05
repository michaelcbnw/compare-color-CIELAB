#!/usr/bin/env python
import PySimpleGUI as sg
import cv2
import numpy as np

"""
Machine Vision Demo - Color Distance
michaelcbnw
"""

'Input global function here'


def nothing(x):
    pass


def col(frame):
    avg_color_per_row = np.average(frame, axis=0)
    avg_color = np.average(avg_color_per_row, axis=0)
    return avg_color


def dist(x, y):
    return round(sum([z*z for z in (x-y)])**0.5)


def preImg(frame, x, y, w):
    lebar = 10
    cv2.rectangle(frame, (x-w, y-w), (lebar+x+w, lebar+y+w), (0, 0, 255), 2)
    cop = frame.copy()
    cop = cop[y-w:lebar+y+w, x-w:lebar+x+w]
    lab = cv2.cvtColor(cop, cv2.COLOR_BGR2Lab)
    # # define kernel size
    kernel = np.ones((7, 7), np.uint8)
    # # Remove unnecessary noise from mask
    mask = cv2.morphologyEx(lab, cv2.MORPH_CLOSE, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    blur = cv2.GaussianBlur(mask, (5, 5), 2)

    return blur


''' Input global variable '''
# Create a trackbar
cv2.namedWindow('move')
cv2.createTrackbar('x', 'move', 300, 400, nothing)
cv2.createTrackbar('y', 'move', 250, 400, nothing)
cv2.createTrackbar('w', 'move', 0, 100, nothing)

'''Main routine'''


def main():

    sg.theme('Black')

    # define the window layout
    camera = [[sg.Frame(" ",
                        [[sg.Text('Machine Vision Demo', size=(40, 1), justification='center', font='Helvetica 20')],
                         [sg.Image(filename='', key='image')],
                            [sg.Button('Train', size=(10, 1), font='Helvetica 14'),
                             sg.Button('Compare', size=(10, 1),
                                       font='Helvetica 14'),
                             sg.Button('Toggle', size=(10, 1), font='Any 14'),
                             sg.Button('Exit', size=(10, 1), font='Helvetica 14'), ]]
                        )]]
    notes = [[sg.Text('Region of Interest')],
             [sg.Image(filename='', key='roi')],
             [sg.Text("", justification='center',
                      key='hasil', font='Helvetica 20')],
             [sg.Text('Threshold '), sg.Text("20", key='th')],
             [sg.Text('Compare '), sg.Text("", key='comp')],
             [sg.Image(filename='', key='preview')]]
    # create the window and show it without the plot
    layout = [[sg.Column(camera, element_justification='c'),
               sg.Column(notes, element_justification='c')]]
    window = sg.Window('Machine Vision Demo',
                       layout, location=(400, 200))

    # --- Event LOOP Read and display frames, operate the GUI --- #
    cap = cv2.VideoCapture(0)
    recording = True
    dataTaken = False
    pos_x = pos_y = 0
    while True:

        x = int(cv2.getTrackbarPos('x', 'move'))+10
        y = int(cv2.getTrackbarPos('y', 'move'))+10
        w = int(cv2.getTrackbarPos('w', 'move'))+10

        event, values = window.read(timeout=10)

        if event == 'Exit' or event == sg.WIN_CLOSED:
            return

        if recording:
            _, frame = cap.read()

            pre = preImg(frame, x, y, w)

            imgbytes = cv2.imencode('.png', frame)[1].tobytes()  # ditto
            window['image'].update(data=imgbytes)
            imgbytes = cv2.imencode('.png', pre)[1].tobytes()  # ditto
            window['roi'].update(data=imgbytes)
            if dataTaken:
                # window['training'].update(str(data))
                window['comp'].update(dist(data, col(pre)))
                window['Compare'].update(disabled=False)
                if dist(data, col(pre)) < 20:
                    window['hasil'].update('OK', text_color='green')
                else:
                    window['hasil'].update('NG', text_color='red')
            else:
                window['Compare'].update(disabled=True)

        if event == 'Train':
            if recording:
                dataTaken = True
                data = col(pre)
                print(f"referensi {col(pre)}")

        elif event == 'Compare':
            if recording:

                if dataTaken == False:
                    print("masukkan referensi!")
                else:
                    print(data)
                    print(dist(data, col(pre)))
                    # window['comp'].update(dist(data, col(pre)))
                    # print("type data", type(data))

        elif event == 'Toggle':
            recording ^= True
            # img = np.full((480, 640), 255)
            # this is faster, shorter and needs less includes
            imgbytes = cv2.imencode('.png', frame)[1].tobytes()
            window['image'].update(data=imgbytes)

        k = cv2.waitKey(1) & 0xFF
        if k == ord('w'):
            pos_y += 1
        if k == ord('s'):
            pos_y -= 1
        if k == ord('d'):
            pos_x += 1
        if k == ord('a'):
            pos_x -= 1


if __name__ == '__main__':
    main()
