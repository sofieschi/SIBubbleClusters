from libPySI import PySI
from plugins.standard_environment_library.SIEffect import SIEffect
from plugins.E import E
from plugins.standard_environment_library._standard_behaviour_mixins.Movable import Movable
from plugins.standard_environment_library._standard_behaviour_mixins.Deletable import Deletable
from plugins.standard_environment_library._standard_behaviour_mixins.Mergeable import Mergeable
from plugins.standard_environment_library._standard_behaviour_mixins.Lassoable import Lassoable

class Split(Deletable, Movable, SIEffect):
    regiontype = PySI.EffectType.SI_CUSTOM
    regionname = "__SPLIT__"
    region_display_name = "Split"

    def __init__(self, shape=PySI.PointVector(), uuid="", kwargs={}):
        super(Split, self).__init__(Split.prepare_shape(shape), uuid, E.id.split_texture, Split.regiontype, Split.regionname, kwargs)
        self.set_QML_path("Split.qml")
        self.color = E.id.split_color

    # the curved shape will be changed to a straight line
    @staticmethod 
    def prepare_shape(points):
        new_shape = PySI.PointVector()
        new_shape.append(points[0])
        new_shape.append(points[len(points)-1])
        return new_shape
