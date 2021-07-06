from libPySI import PySI
from plugins.standard_environment_library.SIEffect import SIEffect
from plugins.E import E

class Lassoable(SIEffect):
    regiontype = PySI.EffectType.SI_CUSTOM_NON_DRAWABLE
    regionname = "__LASSOABLE__"

    def __init__(self, shape=PySI.PointVector(), uuid="", r="", t="", s="", kwargs={}):
        super(Lassoable, self).__init__(shape, uuid, r, t, s, kwargs)
        self.source = "libStdSI"

    @SIEffect.on_enter(E.id.lasso_capabiliy, SIEffect.RECEPTION)
    def on_lasso_enter_recv(self, collided_bubble_uuid):
        # A textfile self collided with a bubble collided_bubble_uuid
        # If the textfile contains to another bubble (new_bubble), the collided_bubble (old_bubble) should be deleted
        # and all texfiles linked to collided_bubble (old_bubble) should be relinked to new_bubble.
        # If a textfile of the collided_bubble also enters the new_bubble, this method is also called, but both
        # are already linked (because of the previous relink) therefore the first step is to check
        # if the testfile is not already linked to collided_bubble.
        if collided_bubble_uuid not in self.get_all_lnk_sender():
            old_lasso_uuid = collided_bubble_uuid
            SIEffect.debug('LASSOABLE: lasso_enter_recv old_bubble={}, self={}'.format(SIEffect.short_uuid(old_lasso_uuid), SIEffect.short_uuid(self._uuid)))
            new_lasso_uuid = self.merge_link(old_lasso_uuid, PySI.LinkingCapability.POSITION, self._uuid, PySI.LinkingCapability.POSITION)
            if new_lasso_uuid != 0:
                SIEffect.debug('LASSOABLE: for the merge, bubble {} shall be deleted and bubble link to {} should persist'.format(SIEffect.short_uuid(old_lasso_uuid), SIEffect.short_uuid(new_lasso_uuid)))
                old_bubble = SIEffect.get_object_with(old_lasso_uuid)
                # get all connected objects of old bubble
                # They must be relinked to new bubble
                all_lassoable = SIEffect.get_all_objects_extending_class(Lassoable);
                SIEffect.debug('LASSOABLE: nr of lassoables={}'.format(len(all_lassoable)))
                bboxes_points = []
                for l in all_lassoable:
                    nr_relinks = l.relink_to_new_bubble(old_bubble.get_uuid(), new_lasso_uuid)
                    if nr_relinks > 0:
                        new_bubble = SIEffect.get_object_with(new_lasso_uuid)
                        # move the textfile to the new bubble
                        # condition: l.abs_xy = new_bubble.abs_xy
                        # => l.abs_xy = l.xy + l.aabb[0] = new_bubble.abs_xy
                        # => l.xy = new_bubble.abs_xy - l.aabb[0]
                        l.move(new_bubble.absolute_x_pos() - l.aabb[0].x, new_bubble.absolute_y_pos() - l.aabb[0].y)
                        # the new_bubble must change ist hull according to the newly linked textfiles
                        # therefore prepare the bounding boxes points of the textfile for hull recalculation
                        # They are provided in absolute coordinates
                        for i in list(range(4)):
                            bboxes_points.append([l.x + l.aabb[i].x, l.y + l.aabb[i].y])
                        #SIEffect.debug('LASSOABLE: move to {},{}'.format(new_bubble.x, new_bubble.y))
                old_bubble.delete()
                new_bubble.recalculate_hull(bboxes_points)

    @SIEffect.on_leave(E.id.lasso_capabiliy, SIEffect.RECEPTION)
    def on_lasso_leave_recv(self, parent_uuid):
        SIEffect.debug('LASSOABLE: on_lasso_leave_recv parent={} self={}'.format(SIEffect.short_uuid(parent_uuid), SIEffect.short_uuid(self._uuid)))
        self.remove_link(parent_uuid, PySI.LinkingCapability.POSITION, self._uuid, PySI.LinkingCapability.POSITION)

    @SIEffect.on_link(SIEffect.RECEPTION, PySI.LinkingCapability.POSITION, PySI.LinkingCapability.POSITION)
    def set_position_from_position(self, rel_x, rel_y, abs_x, abs_y):
        SIEffect.debug('LASSOABLE: set_position_from_position self={} rel={},{} abd={},{}'.format(SIEffect.short_uuid(self._uuid), rel_x, rel_y, abs_x, abs_y))
        self.move(self.x + rel_x, self.y + rel_y)
        self.delta_x, self.delta_y = rel_x, rel_y
