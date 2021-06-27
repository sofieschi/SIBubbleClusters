from libPySI import PySI
from plugins.standard_environment_library.SIEffect import SIEffect
from plugins.E import E

class Lassoable(SIEffect):
    regiontype = PySI.EffectType.SI_CUSTOM_NON_DRAWABLE
    regionname = "__LASSOABLE__"

    def __init__(self, shape=PySI.PointVector(), uuid="", r="", t="", s="", kwargs={}):
        super(Lassoable, self).__init__(shape, uuid, r, t, s, kwargs)
        self.source = "libStdSI"
        self.old_lasso_uuid = ''
        self.new_lasso_uuid = ''

    @SIEffect.on_enter(E.id.lasso_capabiliy, SIEffect.RECEPTION)
    def on_lasso_enter_recv(self, parent_uuid):
        print('lasso_enter_recv parent=')
        print(parent_uuid)
        print(self._uuid)
        ret = self.merge_link(parent_uuid, PySI.LinkingCapability.POSITION, self._uuid, PySI.LinkingCapability.POSITION)
        if ret != 0:
            print('bubble_loeschen')
            self.new_lasso_uuid = ret
            self.old_lasso_uuid = parent_uuid


    @SIEffect.on_leave(E.id.lasso_capabiliy, SIEffect.RECEPTION)
    def on_lasso_leave_recv(self, parent_uuid):
        print('on_lasso_leave_recv parent=')
        print(parent_uuid)
        print(self._uuid)
        self.remove_link(parent_uuid, PySI.LinkingCapability.POSITION, self._uuid, PySI.LinkingCapability.POSITION)

    @SIEffect.on_link(SIEffect.RECEPTION, PySI.LinkingCapability.POSITION, PySI.LinkingCapability.POSITION)
    def set_position_from_position(self, rel_x, rel_y, abs_x, abs_y):
        self.move(self.x + rel_x, self.y + rel_y)
        self.delta_x, self.delta_y = rel_x, rel_y

    @SIEffect.on_enter('__bubble_loeschen__', SIEffect.EMISSION)
    def bubble_loeschen(self, parent):
        if self.old_lasso_uuid != '':
            print('__bubble_loeschen__ gesendet')
            tmp_old = self.old_lasso_uuid
            tmp_new = self.new_lasso_uuid
            self.old_lasso_uuid = ''
            self.new_lasso_uuid = ''
            return tmp_old, tmp_new
        return '', ''

    @SIEffect.on_enter('__bubble_loeschen__', SIEffect.RECEPTION)
    def relink_to_new_bubble2(self, lasso_old_uuid, lasso_new_uuid):
        print('__relink_to_new_bubble__ empfangen')
        nr_relinks = self.relink_to_new_bubble(lasso_old_uuid, lasso_new_uuid)
        if nr_relinks > 0:
            self.move(100,0)