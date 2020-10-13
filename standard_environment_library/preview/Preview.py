from libPySI import PySI

from plugins.standard_environment_library import SIEffect
from plugins.E import E


class Preview(SIEffect.SIEffect):
    regiontype = PySI.EffectType.SI_PREVIEW
    regionname = PySI.EffectName.SI_STD_NAME_PREVIEW
    region_display_name = E.id.preview_display_name

    def __init__(self, shape=PySI.PointVector(), uuid="", kwargs={}):
        super(Preview, self).__init__(shape, uuid, E.id.preview_texture, Preview.regiontype, Preview.regionname, kwargs)
        self.qml_path = self.set_QML_path(E.id.preview_qml_file_name)
        self.color = E.id.preview_color

        self.enable_effect(E.id.preview_capability_previewing, self.EMISSION, self.on_preview_enter_emit, self.on_preview_continuous_emit, self.on_preview_continuous_emit)

    def on_preview_enter_emit(self, other):
        pass

    def on_preview_continuous_emit(self, other):
        pass

    def on_preview_leave_emit(self, other):
        pass
