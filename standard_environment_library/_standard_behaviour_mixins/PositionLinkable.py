from libPySI import PySI
from plugins.standard_environment_library.SIEffect import SIEffect
from plugins.E import E


class PositionLinkable(SIEffect):
    regiontype = PySI.EffectType.SI_CUSTOM_NON_DRAWABLE
    regionname = "__POSITION_LINKABLE__"

    def __init__(self, shape=PySI.PointVector(), uuid="", r="", t="", s="", kwargs={}):
        super(PositionLinkable, self).__init__(shape, uuid, r, t, s, kwargs)

        self.transform_x = 0
        self.transform_y = 0

    @SIEffect.on_link(SIEffect.RECEPTION, PySI.LinkingCapability.POSITION, PySI.LinkingCapability.POSITION)
    def set_position_from_position(self, rel_x, rel_y, abs_x, abs_y):
        #SIEffect.debug('PositionLinkable.set_position_from_position self_uuid={} rel={},{} abs={},{}'.format(SIEffect.short_uuid(self._uuid), rel_x, rel_y, abs_x, abs_y))
        #SIEffect.debug('PositionLinkable.position aabb[0]={},{},{}'.format(self.aabb[0].x,self.aabb[0].y, self.aabb[0].z))
        self.move(self.x + rel_x, self.y + rel_y)

        self.delta_x, self.delta_y = rel_x, rel_y
        self.transform_x += int(self.delta_x)
        self.transform_y += int(self.delta_y)


        if self.is_under_user_control:
            self.mouse_x = abs_x
            self.mouse_y = abs_y
        else:
            self.mouse_x = 0
            self.mouse_y = 0