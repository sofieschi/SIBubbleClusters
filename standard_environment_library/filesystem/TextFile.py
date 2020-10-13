from libPySI import PySI
from plugins.standard_environment_library.filesystem import Entry
from plugins.E import E


class TextFile(Entry.Entry):
    regiontype = PySI.EffectType.SI_TEXT_FILE
    regionname = PySI.EffectName.SI_STD_NAME_TEXTFILE

    def __init__(self, shape=PySI.PointVector(), uuid="", kwargs={}):
        super(TextFile, self).__init__(shape, uuid, TextFile.regiontype, TextFile.regionname, kwargs)
        self.name = PySI.EffectName.SI_STD_NAME_TEXTFILE
        self.region_type = PySI.EffectType.SI_TEXT_FILE
        self.qml_path = self.set_QML_path("TextFile.qml")

        self.set_QML_data("text_height", self.text_height, PySI.DataType.INT)
        self.set_QML_data("img_path", "res/file_icon.png", PySI.DataType.STRING)

        self.enable_effect(E.id.tag_capability_tagging, self.RECEPTION, self. on_tag_enter_recv, None, None)

    def on_tag_enter_recv(self, is_tagged):
        self.set_QML_data("visible", is_tagged, PySI.DataType.BOOL)
