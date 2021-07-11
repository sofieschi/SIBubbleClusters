from libPySI import PySI
from plugins.standard_environment_library.SIEffect import SIEffect
from plugins.E import E

# A Mergeable is used as baseclass for a bubble (lasso).
# It was introduced to avoid a circular import (Lassoable imports Lasso and Lasso imports Lassoable)
class Mergeable(SIEffect):
    regiontype = PySI.EffectType.SI_CUSTOM_NON_DRAWABLE
    regionname = "__MERGEABLE__"
    
    def __init__(self, shape=PySI.PointVector(), uuid="", r="", t="", s="", kwargs={}):
        super(Mergeable, self).__init__(shape, uuid, r, t, s, kwargs)
        self.source = "libStdSI" # transpiler error, if this is not present