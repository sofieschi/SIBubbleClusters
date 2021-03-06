from libPySI import PySI
from plugins.standard_environment_library.SIEffect import SIEffect
#from plugins.standard_environment_library.lasso.Lasso import Lasso
from plugins.standard_environment_library._standard_behaviour_mixins.Mergeable import Mergeable
from plugins.E import E

class Lassoable(SIEffect):
    regiontype = PySI.EffectType.SI_CUSTOM_NON_DRAWABLE
    regionname = "__LASSOABLE__"

    def __init__(self, shape=PySI.PointVector(), uuid="", r="", t="", s="", kwargs={}):
        super(Lassoable, self).__init__(shape, uuid, r, t, s, kwargs)
        self.source = "libStdSI"
        self.recorded_events = None
        self.workaround_active = False

    def set_workaround_active(self, is_active):
        self.workaround_active = is_active

    def set_ignore_lasso_capability(self, is_active):
        if SIEffect.is_logging():
            SIEffect.debug("Lassoable set_ignore_lasso_capability {} {}".format(self.get_uuid(), is_active))
        if is_active:
            if self.recorded_events == None:
                self.recorded_events = {}
        else:
            if self.recorded_events != None:
                for key,value in self.recorded_events.items():
                    #SIEffect.debug("Lassoable: self={} recorded_event={},{}".format(SIEffect.short_uuid(self.get_uuid()),SIEffect.short_uuid(key),value))
                    if value == 1: # enter event
                        self.on_lasso_enter_recv_internal(key) # postponed event will be released now
                self.recorded_events = None

    # workaround for the collision detection bug
    def process_collision(self):
        if SIEffect.is_logging():
            SIEffect.debug("Lassoable: process_collision")
        all_lassos = SIEffect.get_all_objects_extending_class(Mergeable);
        for lasso in all_lassos:
            ll = lasso.get_linked_lassoables()
            if self not in ll:
                if Lassoable.intersect(self,lasso):
                    self.on_lasso_enter_recv(lasso.get_uuid())

    @SIEffect.on_enter(E.id.lasso_capabiliy, SIEffect.RECEPTION)
    def on_lasso_enter_recv(self, parent_uuid):
        if SIEffect.is_logging():
            SIEffect.debug('LASSOABLE: on_lasso_enter_recv self={} {}'.format(SIEffect.short_uuid(self.get_uuid()), SIEffect.short_uuid(parent_uuid)))
        parent = SIEffect.get_object_with(parent_uuid)
        if self.workaround_active and parent != None and not Lassoable.intersect(self,parent):
            if SIEffect.is_logging():
                SIEffect.debug('LASSOABLE: on_lasso_enter_recv ignored! self={}'.format(SIEffect.short_uuid(self.get_uuid())))
            return # workaround for collision detection bug
        #if SIEffect.is_logging():
        if self.recorded_events != None:
            if SIEffect.is_logging():
                SIEffect.debug("Lassoable recorded_events")
            self.recorded_events[parent_uuid] = 1
            return
        self.on_lasso_enter_recv_internal(parent_uuid)
    
    # 
    def on_lasso_enter_recv_internal(self, parent_uuid):
        # A textfile self collided with a bubble collided_bubble_uuid
        # If the textfile contains to another bubble (new_bubble), the collided_bubble (old_bubble) should be deleted
        # and all texfiles linked to collided_bubble (old_bubble) should be relinked to new_bubble.
        # If a textfile of the collided_bubble also enters the new_bubble, this method is also called, but both
        # are already linked (because of the previous relink) therefore the first step is to check
        # if the testfile is not already linked to collided_bubble.
        parent = SIEffect.get_object_with(parent_uuid)
        # parent could be None !!!
        create_link = True
        parent_is_lasso = isinstance(parent, Mergeable)
        if parent_is_lasso:
            create_link = self.lasso_collision(parent)
        if create_link:
            self.create_link(parent_uuid, PySI.LinkingCapability.POSITION, self._uuid, PySI.LinkingCapability.POSITION)
            if parent_is_lasso:
                parent.recalculate_hull()
                parent.collapse_status = 0 # 0 = not expanded not collapsed

    # processes the lasso collision
    # True is returned, if the the link schould be created
    def lasso_collision(self, collided_bubble):
        linked_bubbles = self.get_all_lnk_sender_extending_class(Mergeable)
        if collided_bubble not in linked_bubbles:
            if len(linked_bubbles) > 0:
                # there is already a bubble linked, so we have to merge
                # That means, do not link the collided_bubble, instead delete it
                # and relink all links from collided_bubble to the new_bubble
                new_bubble = linked_bubbles[0]
                #collided_bubble.disable_effect(E.id.lasso_capabiliy, True)
                self.merge_bubbles(collided_bubble, new_bubble)
                return False
            else:
                return True
        return False
            
    def merge_bubbles(self, collided_bubble, new_bubble):
        # get all connected objects of old bubble
        # They must be relinked to new bubble
        all_lassoable = SIEffect.get_all_objects_extending_class(Lassoable);
        if SIEffect.is_logging():
            SIEffect.debug('LASSOABLE: nr of lassoables={}'.format(len(all_lassoable)))
        bboxes_points = []
        for l in all_lassoable:
            l.set_ignore_lasso_capability(True)
            # for each l, which is in the old bubble or the new bubble
            # the merged bubble hull schould contain all of l
            # To decide weather l is linked to old or new bubble, the variable add_to_bboxes_points is used
            add_to_bboxes_points = False
            nr_relinks = l.relink_to_new_bubble(collided_bubble.get_uuid(), new_bubble.get_uuid())
            if nr_relinks > 0:
                # Since nr_of (changed) links is greater 0, the lassoable was linked to old bubble
                # and was relinked to new bubble
                #
                # The lassoable is moved towars the new bubble
                # All coordinates are in absolute coordinates
                ax,ay = Lassoable.get_absolute_point_on_line(0.8, l.absolute_x_pos(), l.absolute_y_pos(), new_bubble.absolute_x_pos(), new_bubble.absolute_y_pos())
                # 
                # for the move function, the new origin x,y must be calculated
                # Here an explanation for the special case of ax,ay = new_bubble.abs_xy
                # condition: l.abs_xy = new_bubble.abs_xy
                # => l.abs_xy = l.xy + l.aabb[0] = new_bubble.abs_xy
                # => l.xy = new_bubble.abs_xy - l.aabb[0]
                l.move(ax - l.aabb[0].x, ay - l.aabb[0].y)
                add_to_bboxes_points = True
                #SIEffect.debug('LASSOABLE: move to {},{}'.format(new_bubble.x, new_bubble.y))
            else:
                if new_bubble.get_uuid() in l.get_all_lnk_sender():
                    # lassoable is already connected to new bubble
                    # To include it in the convex hull, too, add to bboxes_points
                    add_to_bboxes_points = True
            if add_to_bboxes_points:
                # the new_bubble must change its hull according to the newly linked textfiles
                # therefore prepare the bounding boxes points of the textfile for hull recalculation
                # They are provided in absolute coordinates
                for i in list(range(4)):
                    bboxes_points.append([l.x + l.aabb[i].x, l.y + l.aabb[i].y])       
        collided_bubble.delete()
        new_bubble.recalculate_hull_with_additional_points(bboxes_points)
        for l in all_lassoable:
            l.set_ignore_lasso_capability(False)
    
    def get_center(self):
        return self.absolute_x_pos() + 0.5 * self.get_region_width(), self.absolute_y_pos() + 0.5 * self.get_region_height()
        
    @staticmethod
    def intersect(l1,l2):
        # we assume l1x < l2x. If not exchange arguments
        l1x = l1.absolute_x_pos()
        l2x = l2.absolute_x_pos()
        if l1x > l2x:
            return Lassoable.intersect(l2,l1)
        l1y = l1.absolute_y_pos()
        l2y = l2.absolute_y_pos()
        e1x = l1x+l1.get_region_width()
        e1y = l1y+l1.get_region_height()
        e2y = l2y+l2.get_region_height()
        #
        if l2x > e1x:
            return False
        if e1y < l2y:
            return False
        if l1y > e2y:
            return False
        return True
    
    #Get the absolute point on the line between p and q given by a factor.
    # If factor is 0, p is returned. If factor is 1, q is returned. 
    @staticmethod
    def get_absolute_point_on_line(factor, px, py, qx, qy):
        return px + factor*(qx - px), py + factor*(qy - py)

    @SIEffect.on_leave(E.id.lasso_capabiliy, SIEffect.RECEPTION)
    def on_lasso_leave_recv(self, parent_uuid):
        if SIEffect.is_logging():
            SIEffect.debug('LASSOABLE: on_lasso_leave_recv self={} {}'.format(SIEffect.short_uuid(self.get_uuid()), SIEffect.short_uuid(parent_uuid)))
        parent = SIEffect.get_object_with(parent_uuid)
        #SIEffect.debug('LASSOABLE: on_lasso_leave_recv self.aabb={}'.format(self.aabb))
        #SIEffect.debug('LASSOABLE: on_lasso_leave_recv lasso.aabb={}'.format(parent.aabb))
        if self.workaround_active and parent != None and Lassoable.intersect(self,parent):
            if SIEffect.is_logging():
                SIEffect.debug('LASSOABLE: on_lasso_leave_recv ignored!self={}'.format(SIEffect.short_uuid(self.get_uuid())))
            return # workaround fpr collision detection bug
        if self.recorded_events != None:
            if SIEffect.is_logging():
                SIEffect.debug("Lassoable leave recorded events")
            self.recorded_events[parent_uuid] = 0
            return
        #parent = SIEffect.get_object_with(parent_uuid)
        if isinstance(parent, Mergeable):
            if parent.is_remove_link_blocked():
                return # ignore. This is the remove_link bug
        if SIEffect.is_logging():
            SIEffect.debug('LASSOABLE: on_lasso_leave_recv parent={} self={}'.format(SIEffect.short_uuid(parent_uuid), SIEffect.short_uuid(self._uuid)))
        self.remove_link(parent_uuid, PySI.LinkingCapability.POSITION, self._uuid, PySI.LinkingCapability.POSITION)

    @SIEffect.on_link(SIEffect.RECEPTION, PySI.LinkingCapability.POSITION, PySI.LinkingCapability.POSITION)
    def set_position_from_position(self, rel_x, rel_y, abs_x, abs_y):
        if SIEffect.is_logging():
            SIEffect.debug('LASSOABLE: set_position_from_position self={} rel={},{} abd={},{}'.format(SIEffect.short_uuid(self._uuid), rel_x, rel_y, abs_x, abs_y))
        self.move(self.x + rel_x, self.y + rel_y)
        self.delta_x, self.delta_y = rel_x, rel_y
