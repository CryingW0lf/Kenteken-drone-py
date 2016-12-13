import numpy as np
import cv2
from myMath import myMath

class plate_detector:

    def __find_contours(self, img, thresh):
        #1
        src = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # 2
        src = cv2.GaussianBlur(src, (5, 5), 0)
        # Set threshold and maxValue
        #thresh = 200
        maxValue = 255

        # 3
        th, dst = cv2.threshold(src, thresh, maxValue, cv2.THRESH_BINARY);

        # 4
        edges = cv2.Canny(dst, 0, 75, apertureSize=5)

        # 5
        dst, conts, hierarchy = cv2.findContours(dst, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        return conts, hierarchy

    def __find_squares(self, conts):
        mm = myMath()
        squares = []
        current_index = 0
        for cnt in conts:
            cnt_len = cv2.arcLength(cnt, True)
            cnt = cv2.approxPolyDP(cnt, 0.02*cnt_len, True)
        # 7
            if len(cnt) == 4 and cv2.contourArea(cnt) > 1000 and cv2.isContourConvex(cnt) and cv2.isContourConvex(cnt):
                #cnt[0][0][0] x of point 1
                #cnt[0][0][1] y of point 1
                #cnt[1][0][0] x of point 2
                #cnt[1][0][1] y of point 2
                #cnt[2][0][0] x of point 3
                #cnt[2][0][1] y of point 3
                #cnt[3][0][0] x of point 4
                #cnt[3][0][1] y of point 4
                #points go counterclockwise starting with the top left one
                #1 is left
                #2 is bottom
                #3 is right
                #4 is top
                len1 = mm.distance_between_points(cnt[0][0],cnt[1][0])
                len2 = mm.distance_between_points(cnt[1][0],cnt[2][0])
                len3 = mm.distance_between_points(cnt[2][0],cnt[3][0])
                len4 = mm.distance_between_points(cnt[3][0],cnt[1][0])
                r = mm.ratio(len1, len2)
                r2 = mm.ratio(len3, len4)
                #check if ratio is licence plate like
                if (r > 3.0 and r < 8.0) and (r2 > 3.0 and r2 < 8.0):
                    square = current_index, cnt
                    squares.append(square)
            current_index = current_index + 1
        return squares

    def __find_potential_plates(self, squares, hierarchy, conts):
        recs = []
        #TODO vincent: hierarchy is een first child representatie van contours, gebruik deze info om het te optimaliseren.
        for square in squares:
            j = 0
            for hier in hierarchy[0]:
            #check if rectangle has other shapes inside it (posibly letters)
                if hier[3] == square[0]:
                    #removing potential noice
                    if cv2.contourArea(conts[j]) > 1000:
                        recs.append(square[1])
                j = j + 1
        return recs

    def __find_plate(self, recs):
        maxX = 0
        maxY = 0
        minX = 400000
        minY = 400000

        for x in recs:
            for rec in x:

                if rec[0][0][0] > maxX:
                    maxX = rec[0][0][0]
                if rec[1][0][0] > maxX:
                    maxX = rec[1][0][0]
                if rec[2][0][0] > maxX:
                    maxX = rec[2][0][0]
                if rec[3][0][0] > maxX:
                    maxX = rec[3][0][0]
                if rec[0][0][1] > maxY:
                    maxY = rec[0][0][1]
                if rec[1][0][1] > maxY:
                    maxY = rec[1][0][1]
                if rec[2][0][1] > maxY:
                    maxY = rec[2][0][1]
                if rec[3][0][1] > maxY:
                    maxY = rec[3][0][1]

                if rec[0][0][0] < minX:
                    minX = rec[0][0][0]
                if rec[1][0][0] < minX:
                    minX = rec[1][0][0]
                if rec[2][0][0] < minX:
                    minX = rec[2][0][0]
                if rec[3][0][0] < minX:
                    minX = rec[3][0][0]
                if rec[0][0][1] < minY:
                    minY = rec[0][0][1]
                if rec[1][0][1] < minY:
                    minY = rec[1][0][1]
                if rec[2][0][1] < minY:
                    minY = rec[2][0][1]
                if rec[3][0][1] < minY:
                    minY = rec[3][0][1]

        result = [minX, minY, maxX, maxY]
        return result

    def start(self, img):
        plates = []
        for x in xrange(15, 240, 15):
            conts, hierarchy = self.__find_contours(img, x)
            squares = self.__find_squares(conts)
            recs = self.__find_potential_plates(squares, hierarchy, conts)
            if recs != []:
                plates.append(recs)
        plate_cords = self.__find_plate(plates)
        return plate_cords, plates
