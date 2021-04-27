#!/usr/bin/env python
"""
Trunchbull: a facial-recognition attendance tracker

"Miss Trunchbull, the Headmistress, was something else altogether. She was a
gigantic holy terror, a fierce tyrannical monster who frightened the life out
of the pupils and teachers alike" - Roald Dahl

Keyboard shortcuts: (video display window must be selected)

    ESC   - exit
    SPACE - switch between multi and single threaded processing
    v     - write video output frames to file "vid_out.avi"

Option 1 (no timer)
    i     - load images
    r     - start the roll call (no timer)

Option 2 (with timer)
    i     - load images
    t     - start the roll call (with timer)


https://github.com/qe/trunchbull
"""


# import libraries
import cv2 as cv
import numpy as np
# import math
import video
from common import draw_str, StatValue
from time import perf_counter, sleep
from collections import deque
from multiprocessing.pool import ThreadPool
from pathlib import Path
import os, sys
from PIL import Image
# import Image

__author__ = "Alex Ismodes"
__credits__ = ["Richard Alan Peters"]
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
load_images = True
# import pathlib
# pathlib.Path().absolute()
PATH = str(Path().absolute())
IMAGE_TYPES = ('PNG', 'JPG', 'JPEG')


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


# additional functions go here
def get_concat_h_multi_resize(im_list, resample=Image.BICUBIC):
    min_height = min(im.height for im in im_list)
    im_list_resize = [im.resize((int(im.width * min_height / im.height), min_height),resample=resample)
                      for im in im_list]
    total_width = sum(im.width for im in im_list_resize)
    dst = Image.new('RGB', (total_width, min_height))
    pos_x = 0
    for im in im_list_resize:
        dst.paste(im, (pos_x, 0))
        pos_x += im.width
    return dst


def get_concat_v_multi_resize(im_list, resample=Image.BICUBIC):
    min_width = min(im.width for im in im_list)
    im_list_resize = [im.resize((min_width, int(im.height * min_width / im.width)),resample=resample)
                      for im in im_list]
    total_height = sum(im.height for im in im_list_resize)
    dst = Image.new('RGB', (min_width, total_height))
    pos_y = 0
    for im in im_list_resize:
        dst.paste(im, (0, pos_y))
        pos_y += im.height
    return dst


def get_concat_tile_resize(im_list_2d, resample=Image.BICUBIC):
    im_list_v = [get_concat_h_multi_resize(im_list_h, resample=resample) for im_list_h in im_list_2d]
    return get_concat_v_multi_resize(im_list_v, resample=resample)

# get_concat_tile_resize([[im1], [im1, im2], [im1, im2, im1]]).save('data/dst/pillow_concat_tile_resize.jpg')


# main program
if __name__ == '__main__':
    import sys

    # print in the program shell window the text at the beginning of the file
    print(__doc__)

    # ------------------------------------------------------------------------
    blank = Image.new('RGB', (420, 420))

    path_images = PATH + '/images'
    count_images = 0
    images_names = []
    images_filenames = []
    images = []

    for path in Path(path_images).iterdir():
        if path.is_file() and str(path).split('.')[1].upper() in IMAGE_TYPES:
            count_images += 1
            # Path(str(path)).name

            raw_filename = Path(str(path)).name
            images_filenames.append(raw_filename)

            filename = raw_filename.rsplit(".", 1)[0]
            full_name = ' '.join(filename.split('-')).title()
            images_names.append(full_name)

            full_path = str('Path(str(path))')
            exec('img' + str(count_images) + ' = ' + 'Image.open(' + full_path + ')')
            exec('images.append(' + str('img') + str(count_images) + ')')

    print("images_filenames:", images_filenames)
    print()
    print("images_names:", images_names)
    print()
    print("count_images:", count_images)
    print()
    print("images", images)
    print()

    # determine how to nest the images depending on the size of `images`



    # composite = get_concat_tile_resize([[img1, img2, img3, img4, img5]])
    composite = get_concat_tile_resize([
                                        [img1],
                                        [img2, img3],
                                        [blank, img5]
                                        ])
    composite = np.array(composite.convert('RGB'))[:, :, ::-1].copy()

    # get_concat_tile_resize([[img1, img2], [img3]]).save('DELETEME.jpg')

    # ------------------------------------------------------------------------

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

    # create video of Frame sequence -- define the codec and create VideoWriter object
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

    absent = []
    # main program loop
    while True:
        while len(pending) > 0 and pending[0].ready():  # there are frames in the queue
            res, prev_frame, t0 = pending.popleft().get()
            latency.update(perf_counter() - t0)


            # additional functions go here
            if rollcall:
                if load_images:
                    # display current students


                    # #
                    #
                    # if here =

                    # get the dimensions of the compisite image
                    h, w, _ = composite.shape
                    print("height: ", h)
                    print("height: ", w)

                    # status
                    cv.namedWindow('absent', cv.WINDOW_NORMAL)
                    cv.resizeWindow('absent', w, h)
                    # may need to resize it before displaying
                    cv.imshow('absent', composite)
                    # gather the number if images in folder
                    # path_images = PATH + '/images'
                    # dirs = os.listdir(path_images)
                    load_images = False



                # if here:
                    # removes images if student is found

                # rollcall = False








            # # set image composite to specific size and set to specific x-y location
            # # window compsiite size
            #
            # # take the total number of images
            #
            # if do_image:
            #     # if no window yet..
            #     if not count_window:
            #         # adds the image to the new window
            #         cv.namedWindow("captures")
            #         # moves the window to the side
            #         cv.moveWindow("captures", 100, 100)
            #         # resizes window to match with next second capture
            #         resized = cv.resize(res, (712, 400))
            #         cv.imshow("captures", resized)
            #         count_window += 1
            #     # if there is already an existing window..
            #     else:
            #         prev_image = cv.imread(
            #             "captured" + str(count_image) + ".png")
            #         vertical_window = np.concatenate((res, prev_image),
            #                                          axis=0)
            #         cv.imshow("captures", vertical_window)
            #
            #     # saves the image to the working directory
            #     count_image += 1
            #     cv.imwrite("captured" + str(count_image) + ".png", res)
            #
            #     do_image = False














            # plot info on threading and timing on the current image
            # comment out the next 3 lines to skip the plotting
            draw_str(res, (20, 20), "threaded          :  " + str(threaded_mode))
            draw_str(res, (20, 40), "latency            :  %.1f ms" % (latency.value * 1000))
            draw_str(res, (20, 60), "frame interval     :  %.1f ms" % (frame_interval.value * 1000))
            # draw_str(res,(20, 80), "min threshold     :  " + str(thresh_low))

            if vid_frames:
                vid_out.write(res)
            # show the current image
            cv.imshow('video', res)

        if len(pending) < threadn:  # fewer frames than threads -> get another frame
            # get frame
            ret, frame = cap.read()
            frame_counter += 1
            t = perf_counter()
            frame_interval.update(t - last_frame_time)
            last_frame_time = t
            if threaded_mode:
                task = pool.apply_async(process_frame, (frame.copy(), prev_frame.copy(), t))
            else:
                task = DummyTask(process_frame(frame, prev_frame, t))
            pending.append(task)

        # check for a keypress
        key = cv.waitKey(1) & 0xFF

        # threaded or non threaded mode
        if key == ord(' '):
            threaded_mode = not threaded_mode

        # # additional functions go here
        # if key == ord('i'):
        #     load_images = not load_images

        # additional functions go here
        if key == ord('r'):
            rollcall = not rollcall




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
