from libPySI import PySI
from plugins.standard_environment_library.SIEffect import SIEffect
from plugins.E import E
from plugins.standard_environment_library._standard_behaviour_mixins.Movable import Movable
from plugins.standard_environment_library._standard_behaviour_mixins.Deletable import Deletable
from plugins.standard_environment_library._standard_behaviour_mixins.Mergeable import Mergeable
from plugins.standard_environment_library._standard_behaviour_mixins.Lassoable import Lassoable
from threading import Thread
import time
import math

class Split(Deletable, Movable, SIEffect):
    regiontype = PySI.EffectType.SI_CUSTOM
    regionname = "__SPLIT__"
    region_display_name = "Split"
    splitcounter = 1

    def __init__(self, shape=PySI.PointVector(), uuid="", kwargs={}):
        super(Split, self).__init__(self.prepare_shape(shape), uuid, E.id.split_texture, Split.regiontype, Split.regionname, kwargs)
        self.set_QML_path("Split.qml")
        self.color = E.id.split_color
        #splitpoints = [(p.x, p.y) for p in self.shape]
        #SIEffect.debug("Split splitpoints={}".format(len(splitpoints)))
        #for p in splitpoints:
        #    SIEffect.debug("Split splitpoints={}".format(p))
        #self.p1 = splitpoints[0]
        #self.p2 = splitpoints[1]
        self.p1 = [self._p1.x, self._p1.y]
        self.p2 = [self._p2.x, self._p2.y]
        self.lv = [self.p2[0] - self.p1[0], self.p2[1] - self.p1[1]] 
        self.normal = [self.lv[1], -self.lv[0]]
        self.normal_length = math.sqrt(self.normal[0]*self.normal[0]+self.normal[1]*self.normal[1])
        
        #self.lasso_to_split = None
        all_lassos = SIEffect.get_all_objects_extending_class(Mergeable);
        for lasso in all_lassos:
            set1, set2 = self.split_lasso(lasso)
            if len(set1)==0 or len(set2)==0:
                # no split, so ignore
                if len(set1)+len(set2) == 1:
                    self.check_if_delete_lasso(lasso)
                else:    
                    if SIEffect.is_logging():
                        SIEffect.debug("Split no lasso={}".format(lasso))
            else:
                if SIEffect.is_logging():
                    SIEffect.debug("Split lasso in {},{}".format(len(set1), len(set2)))
                factor = 60.0 / self.normal_length 
                # first we need to create the new lasso, but already with the hull, which
                # will contain all lassoables of set1, which will be moved.
                # Therefore, we must first calculate the future position of set1 lassoables,
                # then create the new lasso with that hull information, then unlink the set1 lassoables
                # and finally move the lassoables into the new lasso
                moving_list = []
                for l in set1:
                    # remove l from lasso and do not conenct it to new lasso,
                    # because there is no uuid of the new lasso
                    l.relink_to_new_bubble(lasso.get_uuid(), None)
                    mx,my = l.x + factor*self.normal[0], l.y + factor*self.normal[1] 
                    moving_list.append([l,mx,my])
                    #l.move(mx,my)
                for l in set2:
                    mx,my = l.x - factor*self.normal[0], l.y - factor*self.normal[1] 
                    l.move(mx,my)
                Split.create_new_lasso(lasso, moving_list)

                for l in moving_list:
                    l[0].move(l[1],l[2])
                lasso.recalculate_hull()
        try:
            t = Thread(target=self.delete_split, args=(2,))
            t.start()
            Split.splitcounter += 1
        except:
            if SIEffect.is_logging():
                SIEffect.debug("Start Splitend Thread failed")
    
    # Define a function for the thread
    def delete_split(self, delay):
        if SIEffect.is_logging():
            SIEffect.debug("Start Splitend Thread begin")
        time.sleep(delay)
        self.delete()
        if SIEffect.is_logging():
            SIEffect.debug("Start Splitend Thread ended")
      
    @staticmethod
    def create_new_lasso(lasso, moving_list):
        bboxes_points = []
        for lc in moving_list:
            l = lc[0]
            mx = lc[1]
            my = lc[2]
            for i in list(range(4)):
                bboxes_points.append([mx + l.aabb[i].x, my + l.aabb[i].y])  
        lasso.create_new_lasso(bboxes_points)

    # the curved shape will be changed to a straight line
    def prepare_shape(self, points):
        new_shape = PySI.PointVector()
        self._p1 = points[0]
        self._p2 = points[len(points)-1]
        #SIEffect.debug("Split splitpoints1={}".format(len(points)))
        #SIEffect.debug("Split splitpoints1={},{}".format(self._p1.x, self._p1.y))
        #SIEffect.debug("Split splitpoints1={},{}".format(self._p2.x, self._p2.y))
        new_shape.append(self._p1)
        new_shape.append(self._p2)
        return new_shape

    def split_lasso(self, lasso):
        set1 = [] # set of lassoables for the "first" side of the split
        set2 = [] # set of lassoables for the "other" side of the split
        #SIEffect.debug("Split p1={}".format(self.p1))
        #SIEffect.debug("Split p2={}".format(self.p2))
        
        # we only split the lasso, iff all points of the bounding box of the lasso are inside the section of the split
        for i in range(4):
            qx,qy = lasso.x + lasso.aabb[i].x, lasso.y + lasso.aabb[i].y
            SIEffect.debug("Split q={},{}".format(qx,qy))
        for i in range(4):
            qx,qy = lasso.x + lasso.aabb[i].x, lasso.y + lasso.aabb[i].y
            if self.check_if_point_is_inside_section(qx,qy) == False:
                return set1,set2 # no split
        
        linked_lassoables = lasso.get_linked_lassoables()
        for lassoable in linked_lassoables:
            cx,cy = lassoable.get_center()
            #SIEffect.debug("Split center={},{}".format(cx,cy))
            vx,vy = cx-self.p1[0], cy-self.p1[1]
            # scalar product of v with self.normal
            sp = vx*self.normal[0] + vy*self.normal[1]
            #SIEffect.debug("Split sp={}".format(sp))
            if sp >= 0:
                set1.append(lassoable)
            else:
                set2.append(lassoable)
        return set1,set2
    
    def check_if_delete_lasso(self,lasso):
        r = [lasso.absolute_x_pos(), lasso.absolute_y_pos()]
        width = lasso.get_region_width()
        height = lasso.get_region_height()
        if Split.check_line_completely_intersects_rectangle(self.p1, self.p2, r, width, height):
            if SIEffect.is_logging():
                SIEffect.debug("Split: lasso {} deleted".format(SIEffect.short_uuid(lasso.get_uuid())))
            lasso.delete()
    
    # checks if a point q is inside the section given by the points p1 and p2
    # Consider the given straight line segment p1p2. Let g1 be the straight line perpendicular to that 
    # straight line segment through p1 and g2 be the straight line perpendicular to that straight line segment 
    # through p2. The section s(p1,p2) between p1 and p2 is defined as
    # the set of all points between these two straight lines g1 and g2. 
    def check_if_point_is_inside_section(self, qx,qy) -> bool:
        # the point q is in section(p1,p2) exactly if v*lv >= 0 and u * lv <= 0
        # self.lv = p2 - p1
        SIEffect.debug("Split check_if_point_is_inside_section q={},{}".format(qx,qy))
        SIEffect.debug("Split check_if_point_is_inside_section p1={},{} p2={},{}".format(self.p1[0], self.p1[1], self.p2[0], self.p2[1]))
        SIEffect.debug("Split check_if_point_is_inside_section lv={},{}".format(self.lv[0], self.lv[1]))
        vx,vy = qx-self.p1[0], qy-self.p1[1]
        ux,uy = qx-self.p2[0], qy-self.p2[1]
        vlv = vx*self.lv[0] + vy*self.lv[1]
        ulv = ux*self.lv[0] + uy*self.lv[1]
        SIEffect.debug("Split check_if_point_is_inside_section vlv={}, ulv{}".format(vlv,ulv))
        if vlv < 0:
            return False
        return ulv <= 0
        
    # check if a line given by points p1 and p2 completely intersects a rectangle
    # The rectangle is given by the left upper point and width and height
    # Completely means both endpoints of the line are outside the rectangle 
    # All points are in absolute coordinates
    # 
    @staticmethod
    def check_line_completely_intersects_rectangle(p1, p2, r, width, height) -> bool:
        l = Split.line(p1,p2)
        r2 = [r[0]+width, r[1]]
        r3 = [r[0], r[1]+height]
        r4 = [r[0]+width, r[1]+height]
        
        intersection_count = 0
        r1r2 = Split.line(r, r2)
        i = Split.intersection(l,r1r2)
        if i != False:
            # intersection
            if (r[0] <= i[0]) and (i[0] <= r2[0]):
                # intersection on r1r2
                intersection_count += 1
        r3r4 = Split.line(r3, r4)
        i = Split.intersection(l,r3r4)
        if i != False:
            # intersection
            if (r3[0] <= i[0]) and (i[0] <= r4[0]):
                # intersection on r3r4
                intersection_count += 1
        if intersection_count == 2:
            return True
        
        r1r3 = Split.line(r, r3)
        i = Split.intersection(l,r1r3)
        if i != False:
            # intersection
            if (r[1] <= i[1]) and (i[1] <= r3[1]):
                # intersection on r1r3
                intersection_count += 1
        if intersection_count == 2:
            return True
        
        r2r4 = Split.line(r2, r4)
        i = Split.intersection(l,r2r4)
        if i != False:
            # intersection
            if (r2[1] <= i[1]) and (i[1] <= r4[1]):
                # intersection on r2r4
                intersection_count += 1
        return intersection_count == 2
            
    @staticmethod
    def line(p1, p2):
        A = (p1[1] - p2[1])
        B = (p2[0] - p1[0])
        C = (p1[0]*p2[1] - p2[0]*p1[1])
        return A, B, -C

    # used from https://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines
    @staticmethod
    def intersection(L1, L2):
        D  = L1[0] * L2[1] - L1[1] * L2[0]
        Dx = L1[2] * L2[1] - L1[1] * L2[2]
        Dy = L1[0] * L2[2] - L1[2] * L2[0]
        if D != 0:
            x = Dx / D
            y = Dy / D
            return x,y
        else:
            return False
