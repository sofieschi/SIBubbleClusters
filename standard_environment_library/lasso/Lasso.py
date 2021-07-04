from libPySI import PySI
from plugins.standard_environment_library.SIEffect import SIEffect
from plugins.E import E
from plugins.standard_environment_library._standard_behaviour_mixins.Movable import Movable
from plugins.standard_environment_library._standard_behaviour_mixins.Deletable import Deletable

class Lasso(Deletable, Movable, SIEffect):
	regiontype = PySI.EffectType.SI_CUSTOM
	regionname = "__LASSO__"
	region_display_name = "Lasso"

	def __init__(self, shape=PySI.PointVector(), uuid="", kwargs={}):
		super(Lasso, self).__init__(shape, uuid, E.id.lasso_texture, Lasso.regiontype, Lasso.regionname, kwargs)
		self.set_QML_path("Lasso.qml")
		self.color = E.id.lasso_color

	@SIEffect.on_enter(E.id.lasso_capabiliy, SIEffect.EMISSION)
	def on_lasso_enter_emit(self, other):
		return self._uuid

	@SIEffect.on_leave(E.id.lasso_capabiliy, SIEffect.EMISSION)
	def on_lasso_leave_emit(self, other):
		return self._uuid

	@SIEffect.on_link(SIEffect.EMISSION, PySI.LinkingCapability.POSITION)
	def position(self):
		#SIEffect.debug('LASSO.position self.x,y={},{}  last={},{}'.format(self.x,self.y, self.last_x, self.last_y))
		#SIEffect.debug('LASSO.position aabb[0]={},{},{}'.format(self.aabb[0].x,self.aabb[0].y, self.aabb[0].z))
		x = self.x - self.last_x
		y = self.y - self.last_y
		self.last_x = self.x
		self.last_y = self.y
		#SIEffect.debug('LASSO.position x,y={},{}  self.x,y={},{}'.format(x,y, self.x, self.y))
		return x, y, self.x, self.y

	def get_link_sender(self):
		result = self.get_all_lnk_sender()
		for sender in result:
			SIEffect.debug("Lasso.get_link_receiver : sender {}".format(SIEffect.short_uuid(sender)))
		return result

 # @SIEffect.on_enter('__bubble_loeschen__', SIEffect.RECEPTION)
 # def bubble_loeschen(self, lasso_old_uuid, lasso_new_uuid):
 # 	SIEffect.debug('LASSO: __bubble_loeschen__ received self={} old_lasso={} new_lasso={}'.format(SIEffect.short_uuid(self._uuid), SIEffect.short_uuid(lasso_old_uuid), SIEffect.short_uuid(lasso_new_uuid)))
 # 	if lasso_old_uuid == self._uuid:
 # 		self.delete()
