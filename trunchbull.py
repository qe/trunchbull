#!/usr/bin/env python
"""
Trunchbull: a facial-recognition attendance tracker

"Miss Trunchbull, the Headmistress, was something else altogether. She was a
gigantic holy terror, a fierce tyrannical monster who frightened the life out
of the pupils and teachers alike" - Roald Dahl

Keyboard shortcuts: (video display window must be selected)

    r     - to begin the roll call
    f     - to finish the roll call (CSV file should automatically open)
    v     - write video output frames to file "vid_out.avi"
    SPACE - switch between multi and single threaded processing
    ESC   - exit

https://github.com/qe/trunchbull
"""


# import libraries
import cv2 as cv
import numpy as np
import video
from common import draw_str, StatValue
from time import perf_counter, sleep
from collections import deque
from multiprocessing.pool import ThreadPool
from pathlib import Path
import os, sys, subprocess
import face_recognition as fr
import datetime
import copy
# from PIL import Image

__author__ = "Alex Ismodes"
__credits__ = ["Richard Alan Peters", "Adam Geitgey", "Murtaza Hassan"]
__license__ = "MIT"
__email__ = "alex.ismodes@vanderbilt.edu"


# used to execute process_frame when in non threaded mode
class DummyTask:
    def __init__(self, data):
        self.data = data

    @staticmethod
    def ready():
        return True

    def get(self):
        return self.data


# initialize global variables
frame_counter = 0
show_frames = True
vid_frames = False
rollcall = False
finish_rollcall = False
# load_images = True
# PATH = str(Path().absolute())
# IMAGE_TYPES = ('PNG', 'JPG', 'JPEG')
# second = 1


# this routine is run each time a new video frame is captured
def process_frame(_frame, _prev_frame, _curr_count):
    # current frame
    this_frame = _frame.copy()

    return this_frame, _prev_frame, _curr_count


# create a video capture object
# noinspection DuplicatedCode
def create_capture(source=0):
    # parse source name (defaults to 0 which is the first USB camera attached)

    source = str(source).strip()
    chunks = source.split(':')
    # handle drive letter ('c:', ...)
    if len(chunks) > 1 and len(chunks[0]) == 1 and chunks[0].isalpha():
        chunks[1] = chunks[0] + ':' + chunks[1]
        del chunks[0]

    source = chunks[0]
    try:
        source = int(source)
    except ValueError:
        pass

    params = dict(s.split('=') for s in chunks[1:])

    # video capture object defined on source
    timeout = 100
    _iter = 0
    _cap = cv.VideoCapture(source)

    while (_cap is None or not _cap.isOpened()) & (_iter < timeout):
        sleep(0.1)
        _iter = _iter + 1
        _cap = cv.VideoCapture(source)

    if _iter == timeout:
        print('camera timed out')
        return None
    else:
        print(_iter)

    if 'size' in params:
        w, h = map(int, params['size'].split('x'))
        _cap.set(cv.CAP_PROP_FRAME_WIDTH, w)
        _cap.set(cv.CAP_PROP_FRAME_HEIGHT, h)

    if _cap is None or not _cap.isOpened():
        print('Warning: unable to open video source: ', source)
        return None

    return _cap


# def get_concat_h_multi_resize(im_list, resample=Image.BICUBIC):
#     min_height = min(im.height for im in im_list)
#     im_list_resize = [im.resize((int(im.width * min_height / im.height), min_height),resample=resample)
#                       for im in im_list]
#     total_width = sum(im.width for im in im_list_resize)
#     dst = Image.new('RGB', (total_width, min_height))
#     pos_x = 0
#     for im in im_list_resize:
#         dst.paste(im, (pos_x, 0))
#         pos_x += im.width
#     return dst
#
#
# def get_concat_v_multi_resize(im_list, resample=Image.BICUBIC):
#     min_width = min(im.width for im in im_list)
#     im_list_resize = [im.resize((min_width, int(im.height * min_width / im.width)),resample=resample)
#                       for im in im_list]
#     total_height = sum(im.height for im in im_list_resize)
#     dst = Image.new('RGB', (min_width, total_height))
#     pos_y = 0
#     for im in im_list_resize:
#         dst.paste(im, (0, pos_y))
#         pos_y += im.height
#     return dst
#
#
# def get_concat_tile_resize(im_list_2d, resample=Image.BICUBIC):
#     im_list_v = [get_concat_h_multi_resize(im_list_h, resample=resample) for im_list_h in im_list_2d]
#     return get_concat_v_multi_resize(im_list_v, resample=resample)


def encode(imgs):
    encodings = []

    for i in imgs:
        # convert to RGB
        i = cv.cvtColor(i, cv.COLOR_BGR2RGB)

        # find the encodings
        encoded = fr.face_encodings(i)[0]
        encodings.append(encoded)
    return encodings


def mark(name, date):
    now = datetime.datetime.now()

    # open the csv file
    with open(date + ".csv", "a") as file:
        hms = str(now.hour) +':'+ str(now.minute) +':'+ str(now.second)
        # log status, name, and time
        log = 'P,'+ name.lower() + ',' + hms
        file.writelines(log+'\n')


def final_rollcall(absent, date):
    now = datetime.datetime.now()

    # open the csv file
    with open(date + ".csv", "a") as file:
        for name in absent:
            log = 'A,' + name.lower() + ',' + 'NA'
            file.writelines(log + '\n')


def main():
    global frame_counter
    global show_frames
    global vid_frames
    global rollcall
    global finish_rollcall

    # print in the program shell window the text at the beginning of the file
    print(__doc__)

    # get the current date
    now = datetime.datetime.now()
    date = str(now.year) + "-" + str(now.month) + "-" + str(now.day)
    # create empty CSV file
    with open(date + ".csv", "w") as file:
        # write column headers
        file.writelines('status,name,time\n')

    names = []
    images = []
    path_images = 'images'
    list_images = os.listdir(path_images)

    for filename in list_images:
        if filename != ".DS_Store":
            cur_img = cv.imread(f'{path_images}/{filename}')
            images.append(cur_img)
            names.append(os.path.splitext(filename)[0])

    # create a copy of the list of names to later determine who is still absent
    absent = copy.deepcopy(names)
    marked = []

    # gets the encodings of all the headshots
    rc_encoded = encode(images)

    # if there is no argument in the program invocation default to camera 0
    # noinspection PyBroadException
    # try:
    #     fn = sys.argv[1]
    # except:
    #     fn = 0
    if len(sys.argv) < 2:
        fn = 0
    else:
        fn = sys.argv[1]

    # grab initial frame, create window
    cv.waitKey(1) & 0xFF
    cap = video.create_capture(fn)
    ret, frame = cap.read()
    frame_counter += 1
    height, width, channels = frame.shape
    prev_frame = frame.copy()
    cv.namedWindow("video")

    # create video of Frame sequence
    # define the codec and create VideoWriter object
    fourcc = cv.VideoWriter_fourcc(*'XVID')
    cols = np.int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    rows = np.int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    vid_out = cv.VideoWriter('vid_out.avi', fourcc, 20.0, (cols, rows))

    # set up multiprocessing
    threadn = cv.getNumberOfCPUs()
    pool = ThreadPool(processes=threadn)
    pending = deque()

    threaded_mode = True
    onOff = False

    # initialize time variables
    latency = StatValue()
    frame_interval = StatValue()
    last_frame_time = perf_counter()

    # main program loop
    while True:
        while len(pending) > 0 and pending[
            0].ready():  # there are frames in the queue
            res, prev_frame, t0 = pending.popleft().get()
            latency.update(perf_counter() - t0)

            if finish_rollcall:
                rollcall = not rollcall
                final_rollcall(absent, date)

                # open the completed CSV file
                date = str(now.year) + "-" + str(now.month) + "-" + str(
                    now.day)
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, date + ".csv"])
                finish_rollcall = not finish_rollcall

            # additional functions go here
            if rollcall:

                # resize current frame
                small = cv.resize(res, (0, 0), None, 0.25, 0.25)

                # convert to RGB
                cur_small = cv.cvtColor(small, cv.COLOR_BGR2RGB)

                # get the face locations of all the ppl in the webcame frame
                cur_faces = fr.face_locations(cur_small)

                # get encoding of the webcam
                cur_encoded = fr.face_encodings(cur_small, cur_faces)

                # now, find the matches
                for face_loc, encode_face in zip(cur_faces, cur_encoded):
                    matches = fr.compare_faces(rc_encoded, encode_face)
                    # calculate the distance
                    distance = fr.face_distance(rc_encoded, encode_face)
                    # print(distance)
                    match_idx = np.argmin(distance)

                    if matches[match_idx]:
                        name = names[match_idx]

                        # unpack face coordinates
                        y1, x2, y2, x1 = face_loc

                        # rescale it back to normal
                        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

                        # draw a rectangle
                        cv.rectangle(res, (x1, y1), (x2, y2), (0, 0, 255), 2)
                        cv.rectangle(res, (x1, y2 - 35), (x2, y2), (0, 0, 255),
                                     cv.FILLED)

                        # adjust font size scale
                        scale = 1
                        fontScale = min(x2 - x1, y2 - y1) / (400 / scale)

                        cv.putText(res, name.upper().replace('-', ' '),
                                   (x1 + 6, y2 - 6), cv.FONT_HERSHEY_SIMPLEX,
                                   fontScale, (255, 255, 255), 1)
                        if name not in marked:
                            mark(name, date)
                            marked.append(name)
                            absent.remove(name)

            # plot info on threading and timing on the current image
            # comment out the next 3 lines to skip the plotting
            draw_str(res, (20, 20), "status             :  " + str(
                len(names) - len(absent)) + "/" + str(len(names)) + " present")
            now = datetime.datetime.now()
            hms = str(now.hour) + ':' + str(now.minute) + ':' + str(now.second)
            draw_str(res, (20, 40), "time             :  " + hms)
            draw_str(res, (20, 60),
                     "threaded          :  " + str(threaded_mode))
            draw_str(res, (20, 80),
                     "latency            :  %.1f ms" % (latency.value * 1000))
            draw_str(res, (20, 100), "frame interval     :  %.1f ms" % (
                        frame_interval.value * 1000))

            if vid_frames:
                vid_out.write(res)
            # show the current image
            cv.imshow('video', res)

        if len(
                pending) < threadn:  # fewer frames than threads -> get another frame
            # get frame
            ret, frame = cap.read()
            frame_counter += 1
            t = perf_counter()
            frame_interval.update(t - last_frame_time)
            last_frame_time = t
            if threaded_mode:
                task = pool.apply_async(process_frame,
                                        (frame.copy(), prev_frame.copy(), t))
            else:
                task = DummyTask(process_frame(frame, prev_frame, t))
            pending.append(task)

        # check for a keypress
        key = cv.waitKey(1) & 0xFF

        # threaded or non threaded mode
        if key == ord(' '):
            threaded_mode = not threaded_mode

        # additional functions go here
        if key == ord('r'):
            rollcall = not rollcall

        if key == ord('f'):
            finish_rollcall = not finish_rollcall

        # ESC terminates the program
        if key == ord('v'):
            vid_frames = not vid_frames
            if vid_frames:
                print("Frames are being output to video")
            else:
                print("Frames are not being output to video")

        # ESC terminates the program
        if key == 27:
            # release video capture object
            cap.release()
            # release video output object
            vid_out.release()
            cv.destroyAllWindows()
            break


if __name__ == '__main__':
    main()

