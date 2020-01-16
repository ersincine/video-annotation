"""

A tool for annotating objects in videos for tracking.
version 10.01.2020 by Ersin Çine (ersincine [at] gmail.com)

------------------------------------------------------------------------------------------------------------------------

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or
distribute this software, either in source code form or as a compiled
binary, for any purpose, commercial or non-commercial, and by any
means.

In jurisdictions that recognize copyright laws, the author or authors
of this software dedicate any and all copyright interest in the
software to the public domain. We make this dedication for the benefit
of the public at large and to the detriment of our heirs and
successors. We intend this dedication to be an overt act of
relinquishment in perpetuity of all present and future rights to this
software under copyright law.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

For more information, please refer to <http://unlicense.org/>

------------------------------------------------------------------------------------------------------------------------

Dependencies
- OpenCV

Known bugs
- BBox-s are not restricted to the valid coords.
- (If you found one, please report.)

Likely future works [Importance][Hardness]
- [*** ][*   ] Calc e.g. "output_%05d.png" automatically. Take vid dir path only.
- [**  ][*   ] Fix the conditions in move_bbox_up, etc.
- [**  ][*   ] Better memory management (Do not load all fra-s).
- [*   ][*   ] An option to save anns ("all") in different formats (e.g. YOLO, Pascal VOC). Consider center and/or normalized coords.
- [*   ][*   ] Interpolation with subpixel accuracy (use rounding only for visualization).
- [**  ][**  ] Magnification for manual subpixel annotation & Scaling fra-s to fit to screen.
- [*** ][*** ] Variable-size bbox-s (for each obj, maybe even for each obj-fra pair) & Rectangle bbox-s.

Unlikely future works [Importance][Hardness]                        --- Feel free to fork.
- [*** ][****] Other shapes (Circles, custom obj masks)             --> Currently I do not need.
- [*** ][*** ] Make code more efficient (Especially interpolations) --> Already works well on my system for my vid-s :)
- [*   ][**  ] Refactoring code                                     --> Maybe class structure is hard to understand.
- [*   ][**  ] Custom shortcuts for certain obj-s and/or fra-s      --> Probably it is not worth making the program harder to use/maintain.
- [*   ][*   ] An option to save vid with anns                      --> This feature deserves separate program.

------------------------------------------------------------------------------------------------------------------------

Abbreviations
- dir     : directory
- ann     : annotation
- gt      : ground truth
- bbox    : bounding box
- fra     : frame
- obj     : object
- vid     : video
- prev    : previous (has same number of letters with 'next')
- firs    : first    (has same number of letters with 'last')
- sta     : start    (has same number of letters with 'end' )
- curr    : current
- mid     : middle
- calc    : calculate
- init    : initialize
- coord   : coordinate
- del     : delete
- info    : information
- config  : configuration
- w.r.t   : with respect to
- w/      : with
- w/o     : without
- inc.    : including
- exc.    : excluding, or except
- ...-s   : plural form (e.g. bbox-s)

------------------------------------------------------------------------------------------------------------------------

Fra naming
- Firs fra : firs fra of vid
- Last fra : last fra of vid
- Sta  fra : firs fra of vid w.r.t. an object (firs fra by default)
- End  fra : last fra of vid w.r.t. an object (last fra by default)

Format of anns
- Two CSV files in gt dir (a subdir of vid dir) for each obj:
- (1) objno-key.csv (only key fra-s)
- (2) objno-all.csv (all fra-s)
- Columns: frano, tlx, tly, w, h

------------------------------------------------------------------------------------------------------------------------

How to use the tool?

An end-to-end successful scenario
  [What to do]                          : [How to do it]
- Enter vid path                        : console input
- Enter size of bbox-s                  : console input
- For every obj:
-    Create new obj (exc. firs obj)     :                     N
-    Annotate curr obj
-       (1) Mark sta fra                :    2, 3,            S
-       (2) Mark end fra                :    2, 3,            E
-       (3) Select bbox for sta fra     : 1, 2, 3,    Arrows
-       (4) Select bbox for end fra     :    2, 3, 4, Arrows
-       (5) Select bbox-s for key fra-s : 1, 2, 3, 4, Arrows, SPACE
- Save                                  :                     ENTER
- Exit                                  :                     ESC

Modifying existing anns
- Create new obj       : N
- Change active obj    : -, +
- Del curr obj         : DEL           (All anns for curr obj will be del.)
- Unmark curr key fra  : BACKSPACE     (It cannot be applied to sta/end fra-s. Related fra-s will be interpolated.)
- Mark curr fra as sta : S             (Related fra-s will be interpolated.)
- Mark curr fra as end : E             (Related fra-s will be interpolated.)
- Move curr bbox       : Arrows, SPACE (Related fra-s will be interpolated.)

Notes
- Do not forget to save! (ENTER)
- You can hide obj info (O) or fra info (F).
- Instead of annotating fra-s consecutively, you can annotate in a binary search fashion (M for going to mid).
  (It can be very human-time efficient to do so in certain kind of videos.)
- You can use numeric arrows on the keyboard for moving curr bbox by 40 pixels.
- Colors
-    Red   : Curr obj, for key fra-s (inc. sta/end fra-s)
-    Blue  : Curr obj, for other fra-s
-    Green : Other obj-s
- You can change config easily for keyboard bindings and default values.

All controls

                   Control fra-s
1, 2, 3, 4       : go to sta/prev/next/end fra
M                : go to mid fra in curr range

                   Control obj-s
-, +             : go to prev/next obj
N                : create new obj
DEL              : del curr obj (next obj-s will be shifted)

                   Control bbox-s
←, ↑, ↓, →       : move bbox by 1 pixel
Numeric arrows   : move bbox by 40 pixels
SPACE            : mark key fra (=confirm) (curr fra will be selected as key fra)
S                : mark as sta
E                : mark as end
BACKSPACE        : unmark

                   Tools
ENTER            : save
ESC              : exit (w/o saving)

                   View
F                : toggle fra info (on by default)
O                : toggle obj info (on by default)

"""

### Info

__author__  = "Ersin Çine"
__email__   = "ersincine [at] gmail.com"
__version__ = "10.01.2020"
__license__ = "unlicense"

### Config

FRA_INFO_COLOR  = (0   , 0   , 255) # (blue, green, red)
OBJ_INFO_COLOR  = (0   , 255 , 0  ) # other obj
KEY_FRA_COLOR   = (0   , 0   , 255) # curr obj if key fra
OTHER_FRA_COLOR = (255 , 0   , 0  ) # curr obj if other fra

DEFAULT_THICKNESS = 1

DEFAULT_FRA_INFO = True
DEFAULT_OBJ_INFO = True

FRA_INFO_COORDS = (100, 50 )
OBJ_INFO_COORDS = (100, 100)

DEFAULT_ANN_DIR = "gt"

DEFAULT_FAST_MOV_AMOUNT = 40

GO_TO_STA_FRA_KEY  = 49
GO_TO_END_FRA_KEY  = 52
GO_TO_PREV_FRA_KEY = 50
GO_TO_NEXT_FRA_KEY = 51
GO_TO_MID_FRA_KEY  = 109

GO_TO_PREV_OBJ_KEY = 45
GO_TO_NEXT_OBJ_KEY = 43
CREATE_NEW_OBJ_KEY = 110
DEL_CURR_OBJ_KEY   = 255

MOVE_BBOX_LEFT_KEY  = 81
MOVE_BBOX_RIGHT_KEY = 83
MOVE_BBOX_UP_KEY    = 82
MOVE_BBOX_DOWN_KEY  = 84

FAST_MOVE_BBOX_LEFT_KEY  = 150
FAST_MOVE_BBOX_RIGHT_KEY = 152
FAST_MOVE_BBOX_UP_KEY    = 151
FAST_MOVE_BBOX_DOWN_KEY  = 153

MARK_KEY_FRA_KEY    = 32
MARK_AS_STA_KEY     = 115
MARK_AS_END_KEY     = 101
UNMARK_KEY_FRA_KEY  = 8

SAVE_KEY            = 13

TOGGLE_FRA_INFO_KEY = 102
TOGGLE_OBJ_INFO_KEY = 111

EXIT_KEY            = 27

### Imports

import cv2 as cv
import os

### Classes

class BBox:

    def __init__(self, w, h):
        # You can read tlx and tly but do not change them outside the class.

        assert isinstance(w, int)
        assert isinstance(h, int)
        assert w % 2 == 0
        assert h % 2 == 0
        assert w > 0
        assert h > 0

        self.w   = w
        self.h   = h
        self.tlx = 0
        self.tly = 0
        self.update_all()

    def set_tl(self, tl):
        assert len(tl) == 2
        assert isinstance(tl[0], int)
        assert isinstance(tl[1], int)

        self.tlx = tl[0]
        self.tly = tl[1]
        self.update_all()
        return self

    def set_cp(self, cp):
        assert len(cp) == 2
        assert isinstance(cp[0], int)
        assert isinstance(cp[1], int)

        self.tlx = cp[0] - self.w // 2
        self.tly = cp[1] - self.h // 2
        self.update_all()
        return self

    def set_br(self, br):
        assert len(br) == 2
        assert isinstance(br[0], int)
        assert isinstance(br[1], int)

        self.tlx = br[0] - self.w
        self.tly = br[1] - self.h
        self.update_all()
        return self

    def move_up(self, pixels:int=1):
        self.tly -= pixels
        self.update_all()

    def move_down(self, pixels:int=1):
        self.tly += pixels
        self.update_all()

    def move_left(self, pixels:int=1):
        self.tlx -= pixels
        self.update_all()

    def move_right(self, pixels:int=1):
        self.tlx += pixels
        self.update_all()

    def update_all(self):
        self.tl = (self.tlx              , self.tly              )
        self.cp = (self.tlx + self.w // 2, self.tly + self.h // 2)
        self.br = (self.tlx + self.w     , self.tly + self.h     )

class Obj:

    def __init__(self, bbox_size:int, fra_count:int):
        assert fra_count > 1

        self.fra_count = fra_count
        self.bbox_size = bbox_size

        self.firs_fra_no = 0
        self.last_fra_no = fra_count - 1

        self.sta_fra_no = self.firs_fra_no
        self.end_fra_no = self.last_fra_no
        self.key_fras:dict[int,BBox] = {
            self.sta_fra_no : BBox(bbox_size, bbox_size).set_tl((0, 0)),
            self.end_fra_no : BBox(bbox_size, bbox_size).set_tl((0, 0))
        }

    def set_sta_fra(self, sta_fra_no:int, bbox:BBox):
        assert 0 <= sta_fra_no < self.fra_count

        if sta_fra_no >= self.end_fra_no:
            print("Invalid sta fra (Choose before end fra).")
            return

        if sta_fra_no == self.sta_fra_no:
            self.key_fras[sta_fra_no] = bbox
            return

        if sta_fra_no > self.sta_fra_no:
            # Delete from self.key_fras
            for fra_no in range(self.sta_fra_no, sta_fra_no):
                if self.is_key_fra(fra_no):
                    del self.key_fras[fra_no]

        # If sta_fra_no < self.sta_fra_no, old sta fra is still a key fra)

        if bbox is None: bbox = BBox(self.bbox_size, self.bbox_size).set_tl((0, 0))
        self.key_fras[sta_fra_no] = bbox
        self.sta_fra_no = sta_fra_no

    def set_end_fra(self, end_fra_no:int, bbox:BBox):
        assert 0 <= end_fra_no < self.fra_count

        if end_fra_no <= self.sta_fra_no:
            print("Invalid end fra (Choose after sta fra).")
            return

        if end_fra_no == self.end_fra_no:
            self.key_fras[end_fra_no] = bbox
            return

        if end_fra_no < self.end_fra_no:
            # Delete from self.key_fras
            for fra_no in range(end_fra_no + 1, self.end_fra_no + 1):
                if self.is_key_fra(fra_no):
                    del self.key_fras[fra_no]

        # If end_fra_no > self.end_fra_no, old end fra is still a key fra)

        if bbox is None: bbox = BBox(self.bbox_size, self.bbox_size).set_tl((0, 0))
        self.key_fras[end_fra_no] = bbox
        self.end_fra_no = end_fra_no

    def mark_key_fra(self, fra_no:int, bbox:BBox):
        assert 0 <= fra_no < self.fra_count

        if fra_no <= self.sta_fra_no or fra_no >= self.end_fra_no:
            print("Invalid key fra (Choose between sta and end fra-s).")
            return

        self.key_fras[fra_no] = bbox

    def unmark_key_fra(self, fra_no:int):
        assert 0 <= fra_no < self.fra_count

        if fra_no in (self.sta_fra_no, self.end_fra_no):
            print("It is not between sta and end fra-s.")
            return

        if fra_no in self.key_fras:
            del self.key_fras[fra_no]

    def get_bbox(self, fra_no:int):
        if fra_no < self.sta_fra_no or fra_no > self.end_fra_no:
            return None                     # Invalid frame
        elif fra_no in self.key_fras:
            return self.key_fras[fra_no]    # Key frame
        else:
            for f in reversed(range(self.sta_fra_no, fra_no)):
                if f in self.key_fras:
                    min_fra_no = f
                    min_bbox   = self.key_fras[f]
                    break
            for f in range(fra_no + 1, self.end_fra_no + 1):
                if f in self.key_fras:
                    max_fra_no = f
                    max_bbox   = self.key_fras[f]
                    break
            ratio    = (fra_no - min_fra_no) / (max_fra_no - min_fra_no)
            tlx_dist = max_bbox.tlx - min_bbox.tlx
            tly_dist = max_bbox.tly - min_bbox.tly
            tlx      = round(min_bbox.tlx + ratio * tlx_dist)
            tly      = round(min_bbox.tly + ratio * tly_dist)
            tl       = (tlx, tly)
            bbox     = BBox(self.bbox_size, self.bbox_size).set_tl(tl)
            return bbox

    def is_key_fra(self, fra_no:int):
        return fra_no in self.key_fras

class Vid:

    def __init__(self, vid_path:str, bbox_size:int, scale:float=None, fra_limit:int=None):

        def read_text_file(path):
            file = open(path)
            lines = file.read().splitlines()
            file.close()
            return lines

        print("It may take a while to read all frames.")
        # Load vid into memory
        if fra_limit is None: fra_limit = float("inf")
        reader = cv.VideoCapture(vid_path)
        fras = []
        fra_count = 0
        while True:
            if fra_count > fra_limit : break
            valid, fra               = reader.read()
            if not valid             : break
            if scale is not None     : fra = cv.resize(fra, None, fx=scale, fy=scale)
            fras.append(fra)
            fra_count += 1
        reader.release()

        # Store values
        self.vid_path   = vid_path
        self.ann_path   = vid_path[:vid_path.rfind("/")+1] + DEFAULT_ANN_DIR
        self.bbox_size  = bbox_size

        self.show_fra_info = DEFAULT_FRA_INFO
        self.show_obj_info = DEFAULT_OBJ_INFO

        self.fra_w      = fras[0].shape[1]
        self.fra_h      = fras[0].shape[0]

        self.fras       = fras
        self.active_fra = 0

        self.objs       = []
        self.active_obj = 0

        self.active_bbox = BBox(bbox_size, bbox_size)

        # Create ann dir if not exists
        if os.path.exists(self.ann_path):
            files_count = len(os.listdir(self.ann_path))
            if files_count > 0:
                for obj_no in range(files_count // 2):
                    file = "{}_key.csv".format(obj_no)
                    self.create_new_obj()
                    obj = self.objs[-1]
                    lines = read_text_file(self.ann_path + "/" + file)
                    firs_row = list(map(int, lines[ 0].split(",")))
                    last_row = list(map(int, lines[-1].split(",")))
                    sta_bbox = BBox(firs_row[3], firs_row[4]).set_tl((firs_row[1], firs_row[2]))
                    end_bbox = BBox(last_row[3], last_row[4]).set_tl((last_row[1], last_row[2]))
                    obj.set_sta_fra(firs_row[0] - 1, sta_bbox) # -1 because here we start from 0.
                    obj.set_end_fra(last_row[0] - 1, end_bbox)
                    for line in lines[1:-1]:
                        row = list(map(int, line.split(",")))
                        bbox = BBox(row[3], row[4]).set_tl((row[1], row[2]))
                        obj.mark_key_fra(row[0] - 1, bbox)
                self.update_active_bbox()
        else:
            os.mkdir(self.ann_path)

        if len(self.objs) == 0:
            self.create_new_obj()

    def update_active_bbox(self):
        self.active_bbox = self.objs[self.active_obj].get_bbox(self.active_fra)

    def go_to_sta_fra(self):
        self.active_fra = self.objs[self.active_obj].sta_fra_no
        self.update_active_bbox()

    def go_to_end_fra(self):
        self.active_fra = self.objs[self.active_obj].end_fra_no
        self.update_active_bbox()

    def go_to_prev_fra(self):
        if self.active_fra > 0:
            self.active_fra -= 1
            self.update_active_bbox()

    def go_to_next_fra(self):
        if self.active_fra < len(self.fras) - 1:
            self.active_fra += 1
            self.update_active_bbox()

    def go_to_mid_fra(self):
        obj = self.objs[self.active_obj]
        if self.active_fra <= obj.sta_fra_no:
            # go to firs mid
            min_fra = obj.sta_fra_no
            max_fra = min(obj.key_fras.keys() - {min_fra})
        elif self.active_fra >= obj.end_fra_no:
            # go to last mid
            max_fra = obj.end_fra_no
            min_fra = max(obj.key_fras.keys() - {max_fra})
        else:
            # go to curr mid
            min_fra = None
            for fra in sorted(obj.key_fras.keys()):
                if self.active_fra < fra:
                    max_fra = fra
                    break
                else:
                    min_fra = fra
        mid_fra = (max_fra + min_fra) // 2
        self.active_fra = mid_fra
        self.update_active_bbox()

    def go_to_prev_obj(self):
        if self.active_obj > 0:
            self.active_obj -= 1
            self.update_active_bbox()

    def go_to_next_obj(self):
        if self.active_obj < len(self.objs) - 1:
            self.active_obj += 1
            self.update_active_bbox()

    def create_new_obj(self):
        obj = Obj(self.bbox_size, len(self.fras))
        self.objs.append(obj)
        self.active_obj = len(self.objs) - 1
        self.update_active_bbox()

    def del_curr_obj(self):
        del self.objs[0]
        if len(self.objs) == 0:
            self.create_new_obj()
        self.update_active_bbox()

    def move_bbox_1px_up(self):
        if self.active_bbox is None: return
        if self.active_bbox.tlx > 0:
            self.active_bbox.move_up()

    def move_bbox_1px_down(self):
        if self.active_bbox is None: return
        if self.active_bbox.tlx + self.active_bbox.w < self.fra_w - 1:
            self.active_bbox.move_down()

    def move_bbox_1px_left(self):
        if self.active_bbox is None: return
        if self.active_bbox.tly > 0:
            self.active_bbox.move_left()

    def move_bbox_1px_right(self):
        if self.active_bbox is None: return
        if self.active_bbox.tly + self.active_bbox.h < self.fra_h - 1:
            self.active_bbox.move_right()

    def move_bbox_up(self):
        if self.active_bbox is None: return
        if self.active_bbox.tlx > 0:
            self.active_bbox.move_up(pixels=DEFAULT_FAST_MOV_AMOUNT)

    def move_bbox_down(self):
        if self.active_bbox is None: return
        if self.active_bbox.tlx + self.active_bbox.w < self.fra_w - 1:
            self.active_bbox.move_down(pixels=DEFAULT_FAST_MOV_AMOUNT)

    def move_bbox_left(self):
        if self.active_bbox is None: return
        if self.active_bbox.tly > 0:
            self.active_bbox.move_left(pixels=DEFAULT_FAST_MOV_AMOUNT)

    def move_bbox_right(self):
        if self.active_bbox is None: return
        if self.active_bbox.tly + self.active_bbox.h < self.fra_h - 1:
            self.active_bbox.move_right(pixels=DEFAULT_FAST_MOV_AMOUNT)

    def mark_sta(self):
        self.objs[self.active_obj].set_sta_fra(self.active_fra, self.active_bbox)
        self.active_bbox = self.objs[self.active_obj].get_bbox(self.active_fra)

    def mark_end(self):
        self.objs[self.active_obj].set_end_fra(self.active_fra, self.active_bbox)
        self.active_bbox = self.objs[self.active_obj].get_bbox(self.active_fra)

    def mark_key(self):
        self.objs[self.active_obj].mark_key_fra(self.active_fra, self.active_bbox)

    def unmark_key(self):
        self.objs[self.active_obj].unmark_key_fra(self.active_fra)

    def toggle_fra_info(self):
        self.show_fra_info = not self.show_fra_info

    def toggle_obj_info(self):
        self.show_obj_info = not self.show_obj_info

    def save(self):

        def create_text_file(path, content=""):
            file = open(path, "w")
            file.write(content)
            file.close()

        for obj_no, obj in enumerate(self.objs):
            key_csv_path = "{}/{}_key.csv".format(self.ann_path, obj_no)
            all_csv_path  = "{}/{}_all.csv".format(self.ann_path, obj_no)
            key_lines = ""
            all_lines = ""
            for fra_no in range(obj.sta_fra_no, obj.end_fra_no + 1):
                bbox = obj.get_bbox(fra_no)
                line = "{},{},{},{},{}\n".format(fra_no + 1, bbox.tlx, bbox.tly, bbox.w, bbox.h) # +1 because here we start from 0.
                if obj.is_key_fra(fra_no):
                    key_lines += line
                all_lines += line
            create_text_file(key_csv_path, content=key_lines)
            create_text_file(all_csv_path, content=all_lines)

        print("Annotations saved.")

class VidAnnGUI:

    def __init__(self, vid):
        self.vid = vid

    def run(self):

        def add_obj_info(fra):
            text = "Obj: {} (max:{})".format(self.vid.active_obj, len(self.vid.objs) - 1)
            cv.putText(fra, text, OBJ_INFO_COORDS, cv.FONT_HERSHEY_TRIPLEX, 1, OBJ_INFO_COLOR)
            for obj_no, obj in enumerate(self.vid.objs):
                if obj_no == self.vid.active_obj: continue
                bbox = obj.get_bbox(self.vid.active_fra)
                if bbox is not None:
                    cv.rectangle(fra, bbox.tl, bbox.br, OBJ_INFO_COLOR, DEFAULT_THICKNESS)
                    cv.putText(fra, str(obj_no), bbox.cp, cv.FONT_HERSHEY_TRIPLEX, 1, OBJ_INFO_COLOR)


        def add_fra_info(fra):
            obj = self.vid.objs[self.vid.active_obj]
            if self.vid.active_fra < obj.sta_fra_no:
                text = "BEFORE STA"
            elif self.vid.active_fra > obj.end_fra_no:
                text = "AFTER END"
            else:
                normal_fra_count = obj.end_fra_no - obj.sta_fra_no + 1
                text = "Fra: {}/{} (total: {})".format(self.vid.active_fra - obj.sta_fra_no + 1, normal_fra_count, obj.fra_count)
            cv.putText(fra, text, FRA_INFO_COORDS, cv.FONT_HERSHEY_TRIPLEX, 1, FRA_INFO_COLOR)


        while True:

            fra = self.vid.fras[self.vid.active_fra].copy()

            if self.vid.show_obj_info:
                add_obj_info(fra)

            if self.vid.show_fra_info:
                add_fra_info(fra)

            bbox = self.vid.active_bbox
            if bbox is not None:
                if self.vid.objs[self.vid.active_obj].is_key_fra(self.vid.active_fra):
                    color = KEY_FRA_COLOR
                else:
                    color = OTHER_FRA_COLOR
                cv.rectangle(fra, bbox.tl, bbox.br, color, DEFAULT_THICKNESS)

            cv.imshow("Video", fra)
            key = cv.waitKey(0)

            actions = {
                GO_TO_STA_FRA_KEY        : self.vid.go_to_sta_fra,
                GO_TO_END_FRA_KEY        : self.vid.go_to_end_fra,
                GO_TO_PREV_FRA_KEY       : self.vid.go_to_prev_fra,
                GO_TO_NEXT_FRA_KEY       : self.vid.go_to_next_fra,
                GO_TO_MID_FRA_KEY        : self.vid.go_to_mid_fra,
                GO_TO_PREV_OBJ_KEY       : self.vid.go_to_prev_obj,
                GO_TO_NEXT_OBJ_KEY       : self.vid.go_to_next_obj,
                CREATE_NEW_OBJ_KEY       : self.vid.create_new_obj,
                DEL_CURR_OBJ_KEY         : self.vid.del_curr_obj,
                MOVE_BBOX_LEFT_KEY       : self.vid.move_bbox_1px_left,
                MOVE_BBOX_RIGHT_KEY      : self.vid.move_bbox_1px_right,
                MOVE_BBOX_UP_KEY         : self.vid.move_bbox_1px_up,
                MOVE_BBOX_DOWN_KEY       : self.vid.move_bbox_1px_down,
                FAST_MOVE_BBOX_LEFT_KEY  : self.vid.move_bbox_left,
                FAST_MOVE_BBOX_RIGHT_KEY : self.vid.move_bbox_right,
                FAST_MOVE_BBOX_UP_KEY    : self.vid.move_bbox_up,
                FAST_MOVE_BBOX_DOWN_KEY  : self.vid.move_bbox_down,
                MARK_KEY_FRA_KEY         : self.vid.mark_key,
                MARK_AS_STA_KEY          : self.vid.mark_sta,
                MARK_AS_END_KEY          : self.vid.mark_end,
                UNMARK_KEY_FRA_KEY       : self.vid.unmark_key,
                SAVE_KEY                 : self.vid.save,
                TOGGLE_FRA_INFO_KEY      : self.vid.toggle_fra_info,
                TOGGLE_OBJ_INFO_KEY      : self.vid.toggle_obj_info
            }

            if key in actions:
                actions[key]()
            elif key == EXIT_KEY:
                break
            else:
                print("Unknown command:", key)

### Program

vid_path  = input("Enter vid path (e.g. video/vid_%05d.png):")
bbox_size = int(input("Enter bbox size (e.g. 30):"))

vid         = Vid(vid_path, bbox_size)
vid_ann_gui = VidAnnGUI(vid)
vid_ann_gui.run()
