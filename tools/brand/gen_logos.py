"""Generate the Watchdog and Malinois logos as low-poly faceted vector marks.

    python3 tools/brand/gen_logos.py

Writes assets/logo.svg, plugins/{malinois,husky,collie,bloodhound}/assets/icon.svg.
"""
import math
import os
import random

import numpy as np
from scipy.spatial import Delaunay

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Malinois profile facing right, 1024 canvas. Tall erect ears, long tapered muzzle.
HEAD = [
    (306, 980), (296, 860), (302, 740), (322, 640),     # back of neck
    (350, 560), (376, 486),                             # nape
    (390, 400), (402, 300), (420, 200), (444, 112),     # rear edge of ear to tip
    (478, 186), (506, 262), (532, 330), (556, 376),     # front edge of ear
    (604, 384), (646, 396), (680, 418),                 # forehead
    (704, 448),                                         # stop
    (762, 470), (822, 494), (872, 516), (902, 536),     # bridge of muzzle
    (920, 558), (926, 584), (916, 604),                 # nose
    (888, 616), (846, 624), (798, 634), (752, 648),     # upper lip
    (716, 668), (682, 692), (652, 716),                 # jaw to jaw angle
    (628, 752), (608, 804), (598, 884), (602, 980),     # throat to chest
]
EYE = (676, 486)
# far ear peeks out behind the skull; rendered darker for depth
FAR_EAR = [(566, 386), (588, 270), (620, 160), (648, 242), (674, 334), (690, 424)]
NOSE = "M896 538 Q930 552 928 586 Q922 610 898 608 Q884 576 896 538 Z"
MOUTH = "M914 608 L798 634 L750 646 L726 664"

# Height bumps (x, y, height, radius) that sculpt the lit form.
BUMPS = [
    (650, 440, 46, 90),    # brow ridge over the eye
    (640, 600, 40, 110),   # cheekbone / masseter
    (800, 520, 30, 120),   # crest of the muzzle
    (450, 260, 24, 80),    # cup of the ear
    (420, 760, 36, 200),   # neck muscle
]
# Husky profile facing right: thick triangular ears, domed skull, shorter muzzle, fur ruff.
HUSKY_HEAD = [
    (300, 980), (280, 900), (300, 860), (276, 800), (306, 760),   # ruff down the back of neck
    (290, 700), (326, 660), (318, 600), (352, 560),
    (372, 500), (384, 430),                                       # nape
    (396, 360), (420, 270), (452, 180), (468, 150),               # rear edge of ear to tip
    (500, 210), (530, 280), (560, 340),                           # front edge of ear
    (600, 362), (648, 380), (690, 410),                           # domed forehead
    (714, 450),                                                   # stop
    (770, 470), (830, 494), (870, 516),                           # bridge of muzzle
    (890, 532), (902, 556), (892, 580),                           # nose
    (862, 592), (820, 602), (772, 616),                           # upper lip
    (740, 640), (712, 664), (690, 690),                           # jaw
    (700, 730), (668, 760), (684, 800), (648, 830),               # ruff under the throat
    (664, 880), (628, 920), (640, 980),
]
HUSKY_FAR_EAR = [(560, 360), (584, 260), (606, 190), (632, 260), (660, 340), (684, 400)]
HUSKY_NOSE = "M880 532 Q910 540 906 566 Q900 586 880 584 Q868 558 880 532 Z"
HUSKY_MOUTH = "M892 584 L820 602 L770 616 L742 636"
HUSKY_BUMPS = [
    (650, 440, 46, 90),    # brow
    (650, 590, 44, 120),   # full cheek
    (800, 530, 26, 90),    # short muzzle
    (450, 260, 24, 70),    # ear
    (440, 760, 40, 210),   # thick neck
]

# Border collie profile facing right: semi-erect ears with tipped-over tips, medium muzzle, soft ruff.
COLLIE_HEAD = [
    (304, 980), (290, 900), (306, 840), (292, 780), (318, 720),   # soft coat down the neck
    (330, 650), (352, 580), (372, 510),                           # nape
    (388, 440), (404, 360), (424, 290), (452, 236),               # rear edge of ear
    (488, 214), (520, 240), (512, 262),                           # tipped-over ear tip
    (536, 310), (566, 362),                                       # front edge of ear
    (606, 380), (650, 398), (688, 424),                           # forehead
    (710, 456),                                                   # stop
    (764, 476), (818, 498), (860, 518),                           # bridge
    (884, 536), (896, 560), (884, 584),                           # nose
    (852, 598), (806, 610), (762, 624),                           # upper lip
    (728, 648), (700, 676), (678, 706),                           # jaw
    (690, 750), (660, 790), (676, 840), (644, 890), (650, 980),   # chest ruff
]
COLLIE_FAR_EAR = [(566, 372), (588, 300), (618, 252), (650, 262), (640, 280), (662, 344), (686, 410)]
COLLIE_NOSE = "M872 536 Q902 544 900 568 Q894 588 874 586 Q862 560 872 536 Z"
COLLIE_MOUTH = "M884 588 L806 610 L762 624 L734 644"
COLLIE_BUMPS = [
    (650, 446, 44, 90),    # brow
    (640, 594, 40, 110),   # cheek
    (790, 524, 28, 100),   # muzzle
    (460, 300, 22, 70),    # ear
    (430, 770, 38, 200),   # neck
]

# Bloodhound profile facing right: low skull, long deep muzzle, hanging flews and dewlap.
HOUND_HEAD = [
    (296, 980), (300, 856), (324, 736), (360, 616), (404, 516),   # thick back of neck
    (450, 440), (520, 400), (596, 386), (662, 396),               # long flat skull
    (700, 448),                                                   # stop
    (760, 462), (830, 476), (890, 492),                           # long muzzle
    (914, 508), (924, 536), (912, 560),                           # nose
    (904, 600), (896, 640),                                       # deep square muzzle
    (880, 680), (850, 706), (810, 712), (770, 700),               # hanging flews
    (740, 720), (712, 760), (690, 800),                           # dewlap
    (672, 850), (660, 920), (660, 980),
]
# The long ear hangs in front of the neck, so it is drawn over the head.
HOUND_EAR = [(500, 424), (552, 412), (598, 442), (622, 528), (628, 636), (612, 744),
             (578, 836), (528, 864), (484, 812), (458, 690), (450, 552), (468, 468)]
HOUND_FAR_EAR = [(580, 400), (614, 372), (646, 384), (650, 412), (612, 416)]
HOUND_NOSE = "M904 504 Q930 516 926 544 Q920 564 902 560 Q892 532 904 504 Z"
HOUND_MOUTH = "M906 600 Q888 652 852 690"
HOUND_LINES = "M624 418 Q652 430 686 426 M608 438 Q636 458 672 452 M700 520 Q720 560 716 600"
HOUND_BUMPS = [
    (652, 428, 40, 90),    # brow
    (700, 600, 46, 130),   # heavy cheek and flews
    (800, 540, 34, 120),   # deep muzzle
    (540, 640, 30, 90),    # ear fold
    (420, 780, 38, 208),   # neck
]


# Beagle profile facing right: rounded skull, medium square muzzle, long low-set hanging ear.
BEAGLE_HEAD = [
    (280, 980), (292, 876), (314, 780), (346, 690), (388, 610), (436, 540),   # back of neck
    (476, 484),                                                               # nape
    (510, 436), (548, 394), (602, 366), (658, 358), (708, 370), (738, 398),   # broad, gently rounded skull
    (746, 420),                                                               # brow
    (712, 444),                                                               # stop
    (770, 462), (834, 484), (888, 508),                                       # straight bridge
    (914, 528), (926, 558), (910, 584),                                       # square nose
    (874, 598), (822, 614), (772, 630),                                       # upper lip
    (734, 658), (706, 694),                                                   # short jaw
    (694, 742), (686, 806), (694, 880), (702, 936), (704, 980),               # clean throat
]
# The broad ear hangs low over the cheek and neck, so it is drawn over the head.
BEAGLE_EAR = [(516, 448), (566, 418), (620, 446), (652, 528), (666, 640), (650, 760),
              (608, 872), (540, 894), (486, 830), (458, 690), (452, 546), (472, 476)]
BEAGLE_FAR_EAR = [(582, 372), (604, 338), (644, 334), (664, 360), (632, 378), (604, 380)]
BEAGLE_NOSE = "M900 526 Q934 538 930 566 Q924 590 900 586 Q888 556 900 526 Z"
BEAGLE_MOUTH = "M908 588 L822 614 L772 630 L744 656"
BEAGLE_BUMPS = [
    (662, 404, 44, 92),    # brow
    (676, 580, 46, 108),   # full cheek under the eye
    (838, 510, 34, 112),   # muzzle crest
    (556, 660, 26, 96),    # ear fold
    (416, 790, 40, 215),   # neck
]


def beagle_mask(x, y):
    """Tricolour: black saddle down the back of the neck, tan head, white muzzle and throat."""
    if x > 830 or (y > 700 and x > 650):
        return 0.42                                 # white muzzle and throat
    if x < 470 + 0.21 * (y - 500):
        return -0.7                                 # black saddle over the shoulder
    return 0.1                                      # tan head and neck


def hound_mask(x, y):
    """Black-and-tan: dark saddle down the back of the neck, tan face."""
    if x < 402 + 0.17 * (y - 500) or (y < 425 and x < 640):
        return -0.6
    return 0.15


def collie_mask(x, y):
    """Black coat with a white blaze up the muzzle, white face front and white chest."""
    if x > 740 or (x > 690 and y < 470 and abs(y - (450 - 0.4 * (x - 690))) < 26):
        return 0.6                                  # white muzzle and blaze
    if y > 700 and x > 520:
        return 0.6                                  # white chest
    return -0.55                                    # black coat


def malinois_mask(x, y):
    """Black mask: dark muzzle, dark around the eye, dark ear tips."""
    if x > 730 or ((x - EYE[0]) / 80) ** 2 + ((y - EYE[1]) / 56) ** 2 < 1:
        return -0.85                                # black muzzle and eye mask
    if y < 260:
        return -0.7                                 # dark ear tips
    if x > 660 and y > 560:
        return -0.45                                # mask fades down the jaw
    return 0.12                                     # fawn coat a touch brighter


def husky_mask(x, y):
    """Dark cap over skull, ears and back of neck; white brow spot, face, cheeks and throat."""
    if ((x - 700) / 34) ** 2 + ((y - 432) / 22) ** 2 < 1:
        return 0.6                                  # brow spot
    if y < 470 - 0.05 * (x - EYE[0]) and x < 820 or x < 350 + 0.1 * (y - 500):
        return -0.6                                 # cap and saddle
    return 0.45                                     # white face and ruff


BREEDS = {
    "watchdog": dict(head=HEAD, far_ear=FAR_EAR, nose=NOSE, mouth=MOUTH, bumps=BUMPS, mask=None),
    "malinois": dict(head=HEAD, far_ear=FAR_EAR, nose=NOSE, mouth=MOUTH, bumps=BUMPS, mask=malinois_mask),
    "bloodhound": dict(head=HOUND_HEAD, far_ear=HOUND_FAR_EAR, near_ear=HOUND_EAR, lines=HOUND_LINES,
                       nose=HOUND_NOSE, mouth=HOUND_MOUTH, bumps=HOUND_BUMPS, mask=hound_mask),
    "collie": dict(head=COLLIE_HEAD, far_ear=COLLIE_FAR_EAR, nose=COLLIE_NOSE, mouth=COLLIE_MOUTH, bumps=COLLIE_BUMPS, mask=collie_mask),
    "husky": dict(head=HUSKY_HEAD, far_ear=HUSKY_FAR_EAR, nose=HUSKY_NOSE, mouth=HUSKY_MOUTH, bumps=HUSKY_BUMPS, mask=husky_mask),
    "beagle": dict(head=BEAGLE_HEAD, far_ear=BEAGLE_FAR_EAR, near_ear=BEAGLE_EAR,
                   nose=BEAGLE_NOSE, mouth=BEAGLE_MOUTH, bumps=BEAGLE_BUMPS, mask=beagle_mask),
}
# The ten dogs below share one icon template (ringed()); each adds a head, coat mask and ring motif.
ROTT_HEAD = [(250, 980), (262, 860), (290, 740), (330, 630), (380, 540), (440, 470), (510, 410), (590, 372),
             (660, 368), (712, 392), (736, 424), (716, 446), (780, 460), (840, 478), (880, 500), (898, 524),
             (902, 556), (884, 580), (840, 596), (800, 614), (770, 640), (746, 684), (730, 740), (722, 820),
             (724, 900), (730, 980)]
ROTT_EAR = [(556, 404), (616, 386), (662, 420), (640, 492), (596, 516), (560, 468)]  # folded forward
ROTT_FAR_EAR = [(600, 380), (630, 358), (664, 370), (650, 400), (620, 404)]
ROTT_NOSE = "M872 510 Q904 518 902 548 Q896 568 876 566 Q864 538 872 510 Z"
ROTT_MOUTH = "M880 576 L820 600 L780 616 L756 640"
ROTT_BUMPS = [(668, 400, 46, 96), (690, 590, 50, 120), (830, 520, 30, 90), (600, 450, 24, 70), (420, 780, 44, 230)]

DOBE_HEAD = [(300, 980), (310, 860), (336, 740), (376, 630), (424, 540), (470, 470), (500, 400), (520, 300),
             (540, 190), (566, 110), (600, 180), (634, 290), (662, 380), (704, 432), (740, 452), (820, 476),
             (890, 500), (930, 520), (940, 544), (928, 566), (900, 578), (840, 594), (786, 610), (752, 632),
             (726, 668), (708, 724), (698, 800), (700, 890), (706, 980)]
DOBE_FAR_EAR = [(560, 350), (590, 240), (620, 140), (644, 240), (664, 330), (680, 400)]
DOBE_NOSE = "M904 512 Q938 522 938 548 Q932 570 908 568 Q894 540 904 512 Z"
DOBE_MOUTH = "M912 576 L840 596 L790 612 L758 634"
DOBE_BUMPS = [(668, 430, 34, 80), (680, 590, 34, 100), (840, 520, 28, 110), (560, 260, 24, 80), (440, 780, 34, 200)]

SHEP_HEAD = [(230, 980), (236, 860), (262, 740), (304, 630), (360, 540), (420, 470), (462, 400), (478, 300),
             (496, 180), (520, 110), (560, 190), (600, 290), (630, 370), (670, 410), (712, 436), (780, 460),
             (850, 480), (904, 500), (926, 524), (922, 556), (898, 572), (840, 590), (786, 610), (750, 636),
             (726, 680), (712, 740), (730, 790), (708, 840), (744, 900), (724, 940), (740, 980)]
SHEP_FAR_EAR = [(556, 360), (580, 250), (612, 160), (640, 250), (664, 330), (684, 400)]
SHEP_NOSE = "M896 500 Q928 510 926 538 Q920 560 898 558 Q884 528 896 500 Z"
SHEP_MOUTH = "M904 566 L834 590 L784 610 L752 634"
SHEP_BUMPS = [(660, 420, 40, 90), (690, 590, 40, 110), (830, 510, 32, 120), (520, 240, 22, 80), (400, 790, 46, 230)]

DACH_HEAD = [(240, 980), (260, 880), (300, 790), (350, 710), (410, 630), (470, 560), (530, 480), (590, 430),
             (650, 416), (700, 430), (712, 452), (780, 476), (850, 500), (910, 520), (940, 540), (944, 566),
             (922, 582), (860, 600), (800, 616), (760, 640), (728, 676), (704, 730), (692, 800), (694, 880),
             (700, 980)]
DACH_EAR = [(560, 460), (612, 440), (660, 470), (672, 560), (668, 660), (640, 740), (590, 760), (548, 700),
            (530, 600), (534, 510)]
DACH_FAR_EAR = [(600, 430), (630, 410), (660, 424), (650, 446), (620, 450)]
DACH_NOSE = "M914 520 Q946 530 944 558 Q938 580 916 578 Q902 548 914 520 Z"
DACH_MOUTH = "M920 584 L850 604 L796 620 L762 644"
DACH_BUMPS = [(640, 440, 44, 90), (690, 600, 34, 100), (850, 530, 30, 120), (600, 600, 24, 90), (420, 780, 36, 200)]

AKITA_HEAD = [(220, 980), (226, 860), (252, 740), (300, 630), (360, 540), (420, 470), (476, 420), (520, 360),
              (556, 300), (600, 280), (640, 340), (680, 400), (720, 428), (722, 448), (780, 466), (840, 484),
              (880, 504), (896, 528), (892, 556), (872, 572), (820, 590), (780, 606), (752, 632), (730, 680),
              (716, 740), (724, 800), (706, 850), (740, 910), (730, 980)]
AKITA_FAR_EAR = [(500, 400), (520, 330), (546, 290), (572, 330), (590, 380)]
AKITA_NOSE = "M866 504 Q896 512 894 538 Q888 558 868 556 Q856 530 866 504 Z"
AKITA_MOUTH = "M876 566 L816 588 L776 604 L750 628"
AKITA_BUMPS = [(660, 420, 46, 100), (680, 600, 50, 130), (820, 520, 30, 90), (580, 320, 24, 60), (400, 780, 52, 240)]

POINTER_HEAD = [(280, 980), (294, 870), (320, 770), (356, 680), (400, 600), (450, 530), (500, 470), (550, 420),
                (610, 392), (670, 392), (714, 420), (720, 442), (790, 452), (860, 460), (920, 466), (950, 478),
                (956, 504), (940, 524), (880, 546), (820, 566), (776, 592), (740, 630), (716, 690), (704, 760),
                (702, 860), (706, 980)]
POINTER_EAR = [(540, 450), (590, 430), (636, 460), (652, 550), (650, 660), (626, 740), (580, 760), (546, 700),
               (530, 600), (528, 510)]
POINTER_FAR_EAR = [(600, 400), (632, 384), (662, 394), (650, 418), (620, 420)]
POINTER_NOSE = "M922 462 Q956 470 956 498 Q950 520 928 518 Q914 490 922 462 Z"
POINTER_MOUTH = "M930 522 L840 552 L790 576 L760 604"
POINTER_BUMPS = [(650, 420, 36, 80), (680, 580, 30, 100), (850, 490, 26, 120), (590, 600, 22, 90), (430, 780, 34, 200)]

SAINT_HEAD = [(200, 980), (206, 860), (232, 740), (276, 630), (334, 540), (400, 460), (470, 400), (550, 356),
              (630, 346), (700, 372), (742, 410), (730, 440), (790, 456), (860, 476), (904, 496), (920, 524),
              (916, 556), (900, 580), (902, 620), (890, 660), (860, 690), (820, 700), (780, 690), (756, 720),
              (736, 770), (720, 840), (718, 910), (724, 980)]
SAINT_EAR = [(500, 420), (560, 400), (612, 430), (630, 510), (620, 600), (586, 660), (536, 660), (500, 600),
             (488, 510)]
SAINT_FAR_EAR = [(580, 360), (612, 340), (646, 350), (640, 376), (606, 380)]
SAINT_NOSE = "M880 494 Q914 504 914 534 Q908 556 886 554 Q872 524 880 494 Z"
SAINT_MOUTH = "M900 580 Q880 640 840 690"
SAINT_LINES = "M630 410 Q664 398 704 412 M640 432 Q670 424 700 434"
SAINT_BUMPS = [(660, 400, 52, 100), (720, 620, 54, 140), (830, 520, 34, 110), (560, 520, 26, 90), (400, 780, 52, 250)]

SHIBA_HEAD = [(250, 980), (258, 860), (286, 740), (330, 630), (390, 540), (450, 470), (500, 410), (530, 330),
              (556, 250), (586, 200), (616, 260), (644, 340), (680, 400), (716, 432), (720, 448), (790, 468),
              (850, 490), (890, 512), (902, 536), (890, 558), (850, 572), (800, 590), (760, 610), (730, 640),
              (700, 660), (720, 700), (700, 740), (704, 820), (712, 900), (716, 980)]
SHIBA_FAR_EAR = [(540, 380), (566, 300), (592, 250), (612, 310), (632, 380)]
SHIBA_NOSE = "M868 512 Q896 518 896 540 Q890 560 870 558 Q858 534 868 512 Z"
SHIBA_MOUTH = "M876 562 L816 584 L776 600 L750 624"
SHIBA_BUMPS = [(660, 420, 40, 90), (700, 620, 44, 110), (820, 520, 28, 90), (570, 300, 20, 60), (420, 780, 40, 220)]

PYR_HEAD = [(200, 980), (206, 860), (230, 740), (270, 640), (320, 560), (380, 490), (450, 430), (530, 390),
            (610, 376), (680, 392), (724, 420), (730, 444), (790, 460), (850, 480), (890, 502), (904, 530),
            (896, 560), (870, 578), (820, 592), (780, 610), (750, 640), (730, 690), (712, 740), (730, 790),
            (706, 840), (728, 900), (716, 980)]
PYR_EAR = [(540, 430), (600, 412), (640, 450), (626, 530), (590, 580), (554, 540), (536, 480)]
PYR_FAR_EAR = [(590, 390), (620, 376), (652, 384), (640, 408), (610, 410)]
PYR_NOSE = "M866 500 Q898 508 898 536 Q892 558 870 556 Q856 528 866 500 Z"
PYR_MOUTH = "M878 572 L816 594 L774 612 L748 636"
PYR_BUMPS = [(660, 410, 44, 100), (690, 600, 44, 120), (820, 520, 28, 100), (580, 490, 20, 70), (380, 790, 56, 260)]


def rott_mask(x, y):
    """Black with tan brow spot, cheeks and muzzle."""
    if ((x - 694) / 26) ** 2 + ((y - 436) / 16) ** 2 < 1 or (x > 800 and y > 520) or (680 < x < 800 and 560 < y < 660):
        return 0.15
    return -0.75


def dobe_mask(x, y):
    """Black with rust muzzle and brow spot."""
    if ((x - 704) / 26) ** 2 + ((y - 440) / 14) ** 2 < 1 or (x > 770 and y > 540):
        return 0.12
    return -0.75


def shep_mask(x, y):
    """Black saddle and muzzle mask, tan cheeks and neck."""
    if x < 330 + 0.15 * (y - 500) or x > 770 or y < 330:
        return -0.7
    return 0.15


def dach_mask(x, y):
    """Uniform red-brown, a shade darker behind the skull."""
    return -0.2 if x < 520 else 0


def urajiro_mask(x, y):
    """Akita/Shiba urajiro: white muzzle, cheeks and throat; darker top."""
    if (x > 740 and y > 500) or (y > 620 and x > 600):
        return 0.5
    return -0.3


def pointer_mask(x, y):
    """Liver head patch, white muzzle and neck."""
    if x < 770 and y < 620:
        return -0.5
    return 0.45


def saint_mask(x, y):
    """Red patches over ears and eyes; white blaze, muzzle and chest."""
    if x > 770 or y > 720 or (700 < x < 760 and y < 450):
        return 0.55
    return -0.35


BREEDS.update({
    "rottweiler": dict(head=ROTT_HEAD, far_ear=ROTT_FAR_EAR, near_ear=ROTT_EAR, nose=ROTT_NOSE, mouth=ROTT_MOUTH,
                       bumps=ROTT_BUMPS, mask=rott_mask),
    "doberman": dict(head=DOBE_HEAD, far_ear=DOBE_FAR_EAR, nose=DOBE_NOSE, mouth=DOBE_MOUTH, bumps=DOBE_BUMPS,
                     mask=dobe_mask),
    "shepherd": dict(head=SHEP_HEAD, far_ear=SHEP_FAR_EAR, nose=SHEP_NOSE, mouth=SHEP_MOUTH, bumps=SHEP_BUMPS,
                     mask=shep_mask),
    "dachshund": dict(head=DACH_HEAD, far_ear=DACH_FAR_EAR, near_ear=DACH_EAR, nose=DACH_NOSE, mouth=DACH_MOUTH,
                      bumps=DACH_BUMPS, mask=dach_mask),
    "akita": dict(head=AKITA_HEAD, far_ear=AKITA_FAR_EAR, nose=AKITA_NOSE, mouth=AKITA_MOUTH, bumps=AKITA_BUMPS,
                  mask=urajiro_mask),
    "pointer": dict(head=POINTER_HEAD, far_ear=POINTER_FAR_EAR, near_ear=POINTER_EAR, nose=POINTER_NOSE,
                    mouth=POINTER_MOUTH, bumps=POINTER_BUMPS, mask=pointer_mask),
    "saintbernard": dict(head=SAINT_HEAD, far_ear=SAINT_FAR_EAR, near_ear=SAINT_EAR, lines=SAINT_LINES,
                         nose=SAINT_NOSE, mouth=SAINT_MOUTH, bumps=SAINT_BUMPS, mask=saint_mask),
    "shiba": dict(head=SHIBA_HEAD, far_ear=SHIBA_FAR_EAR, nose=SHIBA_NOSE, mouth=SHIBA_MOUTH, bumps=SHIBA_BUMPS,
                  mask=urajiro_mask),
    "pyrenees": dict(head=PYR_HEAD, far_ear=PYR_FAR_EAR, near_ear=PYR_EAR, nose=PYR_NOSE, mouth=PYR_MOUTH,
                     bumps=PYR_BUMPS, mask=lambda x, y: 0.35),
})


LIGHT = np.array([0.55, -0.62, 0.56])  # from upper-right front (y grows downward)
LIGHT = LIGHT / np.linalg.norm(LIGHT)


def densify(poly, step):
    out = []
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        n = max(1, int(math.hypot(x1 - x0, y1 - y0) // step))
        out += [(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n) for i in range(n)]
    return out


def inside(pt, poly):
    x, y = pt
    hit = False
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
            hit = not hit
    return hit


def mesh(poly, seed, interior=260):
    rng = random.Random(seed)
    pts = densify(poly, 52)
    xs, ys = zip(*poly)
    added = 0
    for _ in range(40000):  # bounded: stop once the shape is full
        if added == interior:
            break
        p = (rng.uniform(min(xs), max(xs)), rng.uniform(min(ys), max(ys)))
        # finer facets on the face, coarser down the neck
        gap = 26 if math.hypot(p[0] - EYE[0], p[1] - EYE[1]) < 220 else 40
        if inside(p, poly) and all(math.hypot(p[0] - q[0], p[1] - q[1]) > gap for q in pts):
            pts.append(p)
            added += 1
    # anchor facets around the eye so the face reads
    pts += [(EYE[0] + 40 * math.cos(a), EYE[1] + 26 * math.sin(a)) for a in np.linspace(0, 2 * math.pi, 7)[:-1]]
    arr = np.array(pts)
    tris = [t for t in Delaunay(arr).simplices if inside(arr[t].mean(axis=0), poly)]
    return arr, tris


def mix(c0, c1, t):
    t = max(0.0, min(1.0, t))
    a = [int(c0[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def heights(arr, poly, seed, bumps=BUMPS):
    """Dome the shape away from its silhouette, add anatomical bumps, a little grain."""
    rng = random.Random(seed)
    segs = list(zip(poly, poly[1:] + poly[:1]))
    out = []
    for x, y in arr:
        d = min(_seg_dist(x, y, a, b) for a, b in segs)
        h = 150 * (1 - (1 - min(d, 170) / 170) ** 2)
        for bx, by, bh, br in bumps:
            h += bh * math.exp(-((x - bx) ** 2 + (y - by) ** 2) / (2 * br * br))
        out.append(h + rng.uniform(-9, 9))
    return np.array(out)


def _seg_dist(x, y, a, b):
    (x0, y0), (x1, y1) = a, b
    dx, dy = x1 - x0, y1 - y0
    t = max(0, min(1, ((x - x0) * dx + (y - y0) * dy) / (dx * dx + dy * dy or 1)))
    return math.hypot(x - x0 - t * dx, y - y0 - t * dy)


def facets(arr, tris, dark, light, seed, poly, bumps=BUMPS, mask=None):
    h = heights(arr, poly, seed, bumps)
    out = []
    for t in tris:
        p = [np.array([arr[i][0], arr[i][1], h[i]]) for i in t]
        n = np.cross(p[1] - p[0], p[2] - p[0])
        n = n / (np.linalg.norm(n) or 1)
        if n[2] < 0:
            n = -n
        shade = 0.16 + 0.95 * max(0.0, float(n @ LIGHT))
        pts = " ".join("%.1f,%.1f" % (x, y) for x, y, _ in p)
        fill = mix(dark, light, shade)
        m = mask(*np.mean([q[:2] for q in p], axis=0)) if mask else 0
        if m:
            fill = mix(fill, dark if m < 0 else "#ffffff", abs(m))
        out.append('<polygon points="%s" fill="%s"/>' % (pts, fill))
    return "\n".join(out)


def edges(arr, tris):
    seen, out = set(), []
    for t in tris:
        for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            k = (min(a, b), max(a, b))
            if k not in seen:
                seen.add(k)
                (x0, y0), (x1, y1) = arr[a], arr[b]
                out.append("M%.1f %.1fL%.1f %.1f" % (x0, y0, x1, y1))
    return " ".join(out)


def outline(poly):
    return "M" + " L".join("%d %d" % p for p in poly) + " Z"


def head_layer(dark, light, edge, seed, eye, breed):
    b = BREEDS[breed]
    arr, tris = mesh(b["head"], seed)
    return f"""
  <g clip-path="url(#lens)">
    <g transform="translate(-60 0)">
      <g>{facets(*mesh(b["far_ear"], seed + 1, interior=10), dark, mix(dark, light, .55), seed + 1, b["far_ear"], b["bumps"], b["mask"])}</g>
      <path d="{outline(b["far_ear"])}" fill="none" stroke="{edge}" stroke-opacity=".55" stroke-width="3" stroke-linejoin="round"/>
      <g>{facets(arr, tris, dark, light, seed, b["head"], b["bumps"], b["mask"])}</g>
      <path d="{edges(arr, tris)}" fill="none" stroke="{edge}" stroke-opacity=".5" stroke-width="1.6"/>
      <path d="{outline(b["head"])}" fill="none" stroke="{edge}" stroke-width="5" stroke-linejoin="round" filter="url(#glow)"/>
      <path d="{b["nose"]}" fill="{dark}" stroke="{edge}" stroke-width="4"/>
      <path d="{b["mouth"]}" fill="none" stroke="{edge}" stroke-width="5" stroke-linecap="round" filter="url(#glow)"/>
      {near_ear(b, dark, light, edge, seed)}
      {eye}
    </g>
  </g>"""


def near_ear(b, dark, light, edge, seed):
    """Optional ear drawn over the head (hanging ears), plus wrinkle lines."""
    out = ""
    if b.get("lines"):
        out += f'<path d="{b["lines"]}" fill="none" stroke="{edge}" stroke-opacity=".7" stroke-width="4" stroke-linecap="round"/>'
    if b.get("near_ear"):
        ear = b["near_ear"]
        out += f'<g>{facets(*mesh(ear, seed + 2, interior=40), dark, mix(dark, light, .6), seed + 2, ear, b["bumps"])}</g>'
        out += f'<path d="{outline(ear)}" fill="none" stroke="{edge}" stroke-width="4" stroke-linejoin="round" filter="url(#glow)"/>'
    return out


DEFS = """
  <defs>
    <radialGradient id="bg" cx="50%" cy="42%" r="70%">
      <stop offset="0" stop-color="{bg0}"/><stop offset="1" stop-color="#000"/>
    </radialGradient>
    <clipPath id="lens"><circle cx="512" cy="512" r="400"/></clipPath>
    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur stdDeviation="7" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    {extra}
  </defs>
  <rect width="1024" height="1024" rx="224" fill="url(#bg)"/>"""


def watchdog():
    """Silver dog inside a watch dial: the dog that watches."""
    ticks = []
    for i in range(60):
        a = math.radians(i * 6 - 90)
        r0 = 418 if i % 5 else 398
        x0, y0 = 512 + r0 * math.cos(a), 512 + r0 * math.sin(a)
        x1, y1 = 512 + 436 * math.cos(a), 512 + 436 * math.sin(a)
        ticks.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" '
                     f'stroke-width="{7 if i % 5 == 0 else 3}"/>')
    eye = (f'<path d="M{EYE[0]-28} {EYE[1]+4} Q{EYE[0]} {EYE[1]-20} {EYE[0]+30} {EYE[1]-6} '
           f'Q{EYE[0]+4} {EYE[1]+16} {EYE[0]-28} {EYE[1]+4} Z" fill="#fff" filter="url(#glow)"/>')
    body = head_layer("#05080e", "#d6e4f5", "#eef5ff", 7, eye, "watchdog")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024" role="img" aria-label="Watchdog">
{DEFS.format(bg0="#1a2230", extra="")}
  <circle cx="512" cy="512" r="400" fill="#020304"/>
{body}
  <g stroke="#f4f8fc" stroke-linecap="round" opacity=".9">{''.join(ticks)}</g>
  <circle cx="512" cy="512" r="452" fill="none" stroke="#f4f8fc" stroke-opacity=".35" stroke-width="3"/>
  <circle cx="512" cy="512" r="400" fill="none" stroke="#f4f8fc" stroke-width="6" filter="url(#glow)"/>
  <circle cx="512" cy="76" r="9" fill="#2DD4BF" filter="url(#glow)"/>
</svg>
"""


def malinois():
    """Teal hunting dog seen through a scope: the dog that finds the target."""
    extra = """<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#2DD4BF" stop-opacity="0"/>
      <stop offset="1" stop-color="#2DD4BF" stop-opacity=".38"/>
    </linearGradient>"""
    eye = f"""<g filter="url(#glow)">
        <circle cx="{EYE[0]}" cy="{EYE[1]}" r="26" fill="none" stroke="#fff" stroke-width="4"/>
        <path d="M{EYE[0]} {EYE[1]-44}V{EYE[1]-30}M{EYE[0]} {EYE[1]+30}V{EYE[1]+44}M{EYE[0]-44} {EYE[1]}H{EYE[0]-30}M{EYE[0]+30} {EYE[1]}H{EYE[0]+44}" stroke="#fff" stroke-width="4" stroke-linecap="round"/>
        <circle cx="{EYE[0]}" cy="{EYE[1]}" r="7" fill="#fff"/>
      </g>"""
    body = head_layer("#010d0c", "#5eead4", "#99f6e4", 11, eye, "malinois")
    cross = []
    for a in (0, 90, 180, 270):
        r = math.radians(a)
        cross.append(f'<line x1="{512 + 400 * math.cos(r):.0f}" y1="{512 + 400 * math.sin(r):.0f}" '
                     f'x2="{512 + 468 * math.cos(r):.0f}" y2="{512 + 468 * math.sin(r):.0f}"/>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024" role="img" aria-label="Malinois">
{DEFS.format(bg0="#06302c", extra=extra)}
  <circle cx="512" cy="512" r="400" fill="#000807"/>
  <path d="M512 512 L912 512 A400 400 0 0 0 795 229 Z" fill="url(#sweep)" clip-path="url(#lens)"/>
{body}
  <g stroke="#5eead4" stroke-width="8" stroke-linecap="round" filter="url(#glow)">{''.join(cross)}</g>
  <circle cx="512" cy="512" r="400" fill="none" stroke="#5eead4" stroke-width="6" filter="url(#glow)"/>
  <circle cx="512" cy="512" r="440" fill="none" stroke="#5eead4" stroke-opacity=".3" stroke-width="2" stroke-dasharray="4 14"/>
</svg>
"""


def husky():
    """Ice-blue dog inside a snowflake ring: the dog that guards the cloud."""
    eye = (f'<path d="M{EYE[0]-28} {EYE[1]+4} Q{EYE[0]} {EYE[1]-20} {EYE[0]+30} {EYE[1]-6} '
           f'Q{EYE[0]+4} {EYE[1]+16} {EYE[0]-28} {EYE[1]+4} Z" fill="#e0f2fe" filter="url(#glow)"/>')
    body = head_layer("#020a14", "#7dd3fc", "#bae6fd", 13, eye, "husky")
    flakes = []
    for a in range(0, 360, 60):
        r = math.radians(a - 90)
        x0, y0 = 512 + 404 * math.cos(r), 512 + 404 * math.sin(r)
        x1, y1 = 512 + 470 * math.cos(r), 512 + 470 * math.sin(r)
        xm, ym = 512 + 446 * math.cos(r), 512 + 446 * math.sin(r)
        bx, by = 18 * math.cos(r + math.pi / 2), 18 * math.sin(r + math.pi / 2)
        dx, dy = 16 * math.cos(r), 16 * math.sin(r)
        flakes.append(f'<path d="M{x0:.0f} {y0:.0f}L{x1:.0f} {y1:.0f}'
                      f'M{xm - bx - dx:.0f} {ym - by - dy:.0f}L{xm:.0f} {ym:.0f}L{xm + bx - dx:.0f} {ym + by - dy:.0f}"/>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024" role="img" aria-label="Husky">
{DEFS.format(bg0="#0b2a44", extra="")}
  <circle cx="512" cy="512" r="400" fill="#01060c"/>
{body}
  <g stroke="#7dd3fc" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" fill="none" filter="url(#glow)">{''.join(flakes)}</g>
  <circle cx="512" cy="512" r="400" fill="none" stroke="#7dd3fc" stroke-width="6" filter="url(#glow)"/>
  <circle cx="512" cy="512" r="440" fill="none" stroke="#7dd3fc" stroke-opacity=".3" stroke-width="2"/>
</svg>
"""



def collie():
    """Violet dog inside a ring of network nodes: the dog that herds the agents."""
    eye = (f'<path d="M{EYE[0]-28} {EYE[1]+4} Q{EYE[0]} {EYE[1]-20} {EYE[0]+30} {EYE[1]-6} '
           f'Q{EYE[0]+4} {EYE[1]+16} {EYE[0]-28} {EYE[1]+4} Z" fill="#f5f3ff" filter="url(#glow)"/>')
    body = head_layer("#0b0518", "#c4b5fd", "#ddd6fe", 17, eye, "collie")
    nodes, links = [], []
    pts = [(512 + 452 * math.cos(math.radians(a - 90)), 512 + 452 * math.sin(math.radians(a - 90))) for a in range(0, 360, 45)]
    for i, (x, y) in enumerate(pts):
        nodes.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="13"/>')
        nx, ny = pts[(i + 3) % len(pts)]
        links.append(f'<path d="M{x:.0f} {y:.0f}L{nx:.0f} {ny:.0f}"/>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024" role="img" aria-label="Collie">
{DEFS.format(bg0="#24124a", extra="")}
  <g stroke="#a78bfa" stroke-opacity=".12" stroke-width="2">{''.join(links)}</g>
  <circle cx="512" cy="512" r="400" fill="#05020c"/>
{body}
  <circle cx="512" cy="512" r="400" fill="none" stroke="#a78bfa" stroke-width="6" filter="url(#glow)"/>
  <circle cx="512" cy="512" r="452" fill="none" stroke="#a78bfa" stroke-opacity=".35" stroke-width="2"/>
  <g fill="#c4b5fd" filter="url(#glow)">{''.join(nodes)}</g>
</svg>
"""



def bloodhound():
    """Amber dog inside a ring of scent-trail marks: the dog that follows every route."""
    eye = (f'<path d="M{EYE[0]-26} {EYE[1]} Q{EYE[0]} {EYE[1]-14} {EYE[0]+26} {EYE[1]} '
           f'Q{EYE[0]} {EYE[1]+12} {EYE[0]-26} {EYE[1]} Z" fill="#fff7ed" filter="url(#glow)"/>')
    body = head_layer("#140a02", "#fbbf24", "#fde68a", 19, eye, "bloodhound")
    trail = []
    for i in range(24):
        a = math.radians(i * 15 - 90)
        r = 446 + (10 if i % 2 else -10)
        trail.append(f'<circle cx="{512 + r * math.cos(a):.0f}" cy="{512 + r * math.sin(a):.0f}" r="{9 if i % 2 else 6}"/>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024" role="img" aria-label="Bloodhound">
{DEFS.format(bg0="#3a2206", extra="")}
  <circle cx="512" cy="512" r="400" fill="#0a0501"/>
{body}
  <circle cx="512" cy="512" r="400" fill="none" stroke="#f59e0b" stroke-width="6" filter="url(#glow)"/>
  <g fill="#fbbf24" filter="url(#glow)">{''.join(trail)}</g>
</svg>
"""


def beagle():
    """Warm tan dog inside a ring of padlocks: the dog that sniffs out personal data."""
    eye = (f'<path d="M{EYE[0]-26} {EYE[1]} Q{EYE[0]} {EYE[1]-16} {EYE[0]+26} {EYE[1]} '
           f'Q{EYE[0]} {EYE[1]+12} {EYE[0]-26} {EYE[1]} Z" fill="#fffbeb" filter="url(#glow)"/>')
    body = head_layer("#0f0a05", "#f5d0a9", "#fde8cf", 23, eye, "beagle")
    locks = []
    for i in range(12):
        a = i * 30 - 90
        r = math.radians(a)
        x, y = 512 + 452 * math.cos(r), 512 + 452 * math.sin(r)
        locks.append(f'<g transform="translate({x:.1f} {y:.1f}) rotate({a + 90})">'
                     f'<path d="M-7 -3V-9A7 7 0 0 1 7 -9V-3" fill="none" stroke="#fb923c" stroke-width="4"/>'
                     f'<rect x="-12" y="-3" width="24" height="18" rx="6" fill="#fb923c"/>'
                     f'<circle cx="0" cy="6" r="2.6" fill="#0f0a05"/></g>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024" role="img" aria-label="Beagle">
{DEFS.format(bg0="#3a1e08", extra="")}
  <circle cx="512" cy="512" r="400" fill="#0c0703"/>
{body}
  <circle cx="512" cy="512" r="400" fill="none" stroke="#fb923c" stroke-width="6" filter="url(#glow)"/>
  <circle cx="512" cy="512" r="452" fill="none" stroke="#fb923c" stroke-opacity=".3" stroke-width="2"/>
  <g filter="url(#glow)">{''.join(locks)}</g>
</svg>
"""


def ringed(breed, label, dark, light, edge, ring, bg0, inner, seed, mark, count, offset=0):
    """Shared icon for the newer dogs: breed head in a lens, `count` copies of `mark` round the ring."""
    eye = (f'<path d="M{EYE[0]-26} {EYE[1]} Q{EYE[0]} {EYE[1]-16} {EYE[0]+26} {EYE[1]} '
           f'Q{EYE[0]} {EYE[1]+12} {EYE[0]-26} {EYE[1]} Z" fill="{edge}" filter="url(#glow)"/>')
    body = head_layer(dark, light, edge, seed, eye, breed)
    marks = []
    for i in range(count):
        a = i * 360 / count - 90 + offset
        r = math.radians(a)
        marks.append(f'<g transform="translate({512 + 452 * math.cos(r):.1f} {512 + 452 * math.sin(r):.1f}) '
                     f'rotate({a + 90:.0f})">{mark}</g>')
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024" role="img" aria-label="{label}">
{DEFS.format(bg0=bg0, extra="")}
  <circle cx="512" cy="512" r="400" fill="{inner}"/>
{body}
  <circle cx="512" cy="512" r="400" fill="none" stroke="{ring}" stroke-width="6" filter="url(#glow)"/>
  <circle cx="512" cy="512" r="452" fill="none" stroke="{ring}" stroke-opacity=".3" stroke-width="2"/>
  <g fill="none" stroke="{ring}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" filter="url(#glow)">{''.join(marks)}</g>
</svg>
"""


KEY = '<circle cx="0" cy="-10" r="9"/><path d="M0 -1V20M0 12H8M0 18H6"/>'


def rottweiler():
    """Bronze dog in a ring of chain links: the dog that guards the supply chain."""
    return ringed("rottweiler", "Rottweiler", "#050505", "#a8a29e", "#e7e5e4", "#b45309", "#2a1606", "#050403", 29,
                  '<rect x="-20" y="-10" width="40" height="20" rx="10"/>', 10)


def doberman():
    """Red dog in a ring of keys: the dog that guards the login."""
    return ringed("doberman", "Doberman", "#050308", "#f87171", "#fecaca", "#dc2626", "#3a0a0a", "#060203", 31, KEY, 8)


def shepherd():
    """Green dog in a ring of phones: the dog that guards mobile apps."""
    return ringed("shepherd", "Shepherd", "#04070a", "#86efac", "#bbf7d0", "#22c55e", "#06301a", "#020604", 37,
                  '<rect x="-11" y="-18" width="22" height="36" rx="5"/><path d="M-4 12H4"/>', 6)


def dachshund():
    """Rose dog in a ring of database cylinders: the dog that digs into databases."""
    return ringed("dachshund", "Dachshund", "#0d0604", "#fb7185", "#fecdd3", "#e11d48", "#3a0814", "#070203", 41,
                  '<ellipse cx="0" cy="-12" rx="14" ry="5"/><path d="M-14 -12V12A14 5 0 0 0 14 12V-12M-14 0A14 5 0 0 0 14 0"/>', 8)


def akita():
    """Blue dog in a ring of keys: the dog that guards secrets."""
    return ringed("akita", "Akita", "#060a0f", "#93c5fd", "#dbeafe", "#3b82f6", "#0b1e40", "#02040a", 43, KEY, 6)


def pointer():
    """Yellow dog in a crosshair: the dog that points at frontend bugs."""
    return ringed("pointer", "Pointer", "#0a0a0a", "#fde047", "#fef9c3", "#eab308", "#332a04", "#050401", 47,
                  '<path d="M0 -30V30"/><circle cx="0" cy="0" r="8"/>', 4, offset=45)


def saintbernard():
    """Red dog in a ring of crosses: the dog that comes when there is an incident."""
    return ringed("saintbernard", "Saint Bernard", "#110505", "#fca5a5", "#fee2e2", "#ef4444", "#3a0a0a", "#070202", 53,
                  '<path d="M0 -14V14M-14 0H14" stroke-width="8"/>', 8)


def shiba():
    """Orange dog in a ring of hexagon blocks: the dog that audits smart contracts."""
    return ringed("shiba", "Shiba", "#0c0602", "#fdba74", "#ffedd5", "#f97316", "#3a1a04", "#070301", 59,
                  '<path d="M0 -15L13 -7.5V7.5L0 15L-13 7.5V-7.5Z"/>', 8)


def pyrenees():
    """White dog in a ring of checkmarks: the dog that maps compliance."""
    return ringed("pyrenees", "Pyrenees", "#0a0c10", "#e2e8f0", "#f8fafc", "#94a3b8", "#1e2533", "#030405", 61,
                  '<path d="M-12 0L-3 10L13 -10" stroke-width="7"/>', 8)


NEW_DOGS = ("rottweiler", "doberman", "shepherd", "dachshund", "akita", "pointer", "saintbernard", "shiba", "pyrenees")


if __name__ == "__main__":
    for rel, svg in (("assets/logo.svg", watchdog()), ("plugins/malinois/assets/icon.svg", malinois()),
                     ("plugins/husky/assets/icon.svg", husky()),
                     ("plugins/collie/assets/icon.svg", collie()),
                     ("plugins/bloodhound/assets/icon.svg", bloodhound()),
                     ("plugins/beagle/assets/icon.svg", beagle())):
        with open(os.path.join(ROOT, rel), "w") as f:
            f.write(svg)
    for dog in NEW_DOGS:
        os.makedirs(os.path.join(ROOT, "plugins", dog, "assets"), exist_ok=True)
        with open(os.path.join(ROOT, "plugins", dog, "assets", "icon.svg"), "w") as f:
            f.write(globals()[dog]())
        print("wrote", dog)
