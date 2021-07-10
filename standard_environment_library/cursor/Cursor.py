from libPySI import PySI
from plugins.standard_environment_library.SIEffect import SIEffect
from plugins.standard_environment_library.lasso.Lasso import Lasso


class Cursor(SIEffect):
    regiontype = PySI.EffectType.SI_MOUSE_CURSOR
    regionname = PySI.EffectName.SI_STD_NAME_MOUSE_CURSOR
    region_width = 18
    region_height = 24

    def __init__(self, shape=PySI.PointVector(), uuid="", kwargs={}):
        super(Cursor, self).__init__(shape, uuid, "", Cursor.regiontype, Cursor.regionname, kwargs)

        self.qml_path = self.set_QML_path("Cursor.qml")
        self.color = PySI.Color(255, 0, 0, 0)
        self.assigned_effect = ""
        self.is_drawing_blocked = False
        self.width = Cursor.region_width
        self.height = Cursor.region_height
        self.with_border = False

        self.clicks = 0

        self.set_QML_data("width", self.width, PySI.DataType.INT)
        self.set_QML_data("height", self.height, PySI.DataType.INT)

        self.parent_canvas = None
        self.move_target = None
        self.btn_target = None
        self.image_editor_tool = []
        self.image_editor_tooltype = None

        self.left_mouse_active = False
        self.right_mouse_active = False

    def mouse_wheel_angle_px(self, px):
        SIEffect.debug("mouse_wheel_angle_px {}".format(px))
        
    def mouse_wheel_angle_degrees(self, degrees):
        SIEffect.debug("mouse_wheel_angle_degrees {}".format(degrees))
        
    def on_middle_mouse_click(self, is_active):
        SIEffect.debug("on_middle_mouse_click {}".format(is_active))
        if is_active:
            lassos = SIEffect.get_all_objects_extending_class(Lasso)
            for lasso in lassos:
                lasso.spread_bubble(0.2)
        
    @SIEffect.on_link(SIEffect.EMISSION, PySI.LinkingCapability.POSITION)
    def position(self):
        return self.x - self.last_x, self.y - self.last_y, self.x, self.y

    @SIEffect.on_link(SIEffect.RECEPTION, PySI.LinkingCapability.POSITION, PySI.LinkingCapability.POSITION)
    def set_position_from_position(self, rel_x, rel_y, abs_x, abs_y):
        self.last_x = self.x
        self.last_y = self.y

        self.move(abs_x, abs_y)

    def self_on_sketch_enter_emit(self, other):
        self.parent_canvas = other

        return 0, 0, self._uuid

    def on_sketch_continuous_emit(self, other):
        return self.x, self.y, self._uuid

    def on_sketch_leave_emit(self, other):
        self.parent_canvas = None

        return 0, 0, self._uuid

    def on_move_enter_emit(self, other):
        SIEffect.debug("on_move_enter_emit other={}".format(other))
        if self.move_target is None:
            self.move_target = other

        if self.move_target is other:
            return self._uuid, PySI.LinkingCapability.POSITION

        return "", ""

    def on_move_continuous_emit(self, other):
        pass
        #SIEffect.debug("move cursor {},{} {},{}".format(self.absolute_x_pos(), self.absolute_y_pos(), self.get_region_width(), self.get_region_height()))
        #l = SIEffect.get_all_objects_extending_class(Lasso)
        #SIEffect.debug("move {}".format(len(l)))
        #for ls in l:
        #    SIEffect.debug("move lasso {}".format(ls.get_uuid()))
        #    SIEffect.debug("move lasso {},{} {},{}".format(ls.absolute_x_pos(), ls.absolute_y_pos(), ls.get_region_width(), ls.get_region_height()))

    def on_move_leave_emit(self, other):
        if self.move_target is other:
            self.move_target = None
            return self._uuid, PySI.LinkingCapability.POSITION

        return "", ""

    def on_btn_press_enter_emit(self, other):
        if self.btn_target is None:
            self.btn_target = other

        return self._uuid

    def on_btn_press_continuous_emit(self, other):
        return self._uuid

    def on_btn_press_leave_emit(self, other):
        if self.btn_target is other:
            self.btn_target = None

        return self._uuid

    def on_left_mouse_click(self, is_active):
        self.left_mouse_active = is_active

        if is_active:
            if PySI.CollisionCapability.CLICK not in self.cap_emit.keys():
                self.enable_effect(PySI.CollisionCapability.CLICK, True, self.on_btn_press_enter_emit, self.on_btn_press_continuous_emit, self.on_btn_press_leave_emit)

            if self.assigned_effect != "":
                if not self.is_drawing_blocked and PySI.CollisionCapability.SKETCH not in self.cap_emit.keys():
                    self.enable_effect(PySI.CollisionCapability.SKETCH, True, self.self_on_sketch_enter_emit, self.on_sketch_continuous_emit, self.on_sketch_leave_emit)
        else:
            if PySI.CollisionCapability.SKETCH in self.cap_emit.keys():
                self.disable_effect(PySI.CollisionCapability.SKETCH, True)

                if self.parent_canvas is not None:
                    self.parent_canvas.on_sketch_leave_recv(*self.on_sketch_leave_emit(self.parent_canvas))
                self.parent_canvas = None

            if PySI.CollisionCapability.CLICK in self.cap_emit.keys():
                self.disable_effect(PySI.CollisionCapability.CLICK, True)
                if self.btn_target is not None:
                    self.btn_target.on_click_leave_recv(self._uuid)

    def on_right_mouse_click(self, is_active):
        SIEffect.debug("move cursor2 {},{} {},{}".format(self.absolute_x_pos(), self.absolute_y_pos(), self.get_region_width(), self.get_region_height()))
        SIEffect.debug("1 {},{} {},{}".format(self.absolute_x_pos(), self.absolute_y_pos(), self.get_region_width(), self.get_region_height()))
        l = SIEffect.get_all_objects_extending_class(Lasso)
        SIEffect.debug("2 {}".format(len(l)))
        for ls in l:
            SIEffect.debug("3 {}".format(ls.get_uuid()))
            SIEffect.debug("4 {},{} {},{}".format(ls.absolute_x_pos(), ls.absolute_y_pos(), ls.get_region_width(), ls.get_region_height()))

        self.right_mouse_active = is_active
        SIEffect.debug("move cursor22 {}".format(is_active))
        if is_active:
            SIEffect.debug("move cursor23 {}".format(PySI.CollisionCapability.MOVE not in self.cap_emit.keys()))
            if PySI.CollisionCapability.MOVE not in self.cap_emit.keys():
                self.enable_effect(PySI.CollisionCapability.MOVE, True, self.on_move_enter_emit, self.on_move_continuous_emit, self.on_move_leave_emit)
        elif PySI.CollisionCapability.MOVE in self.cap_emit.keys():
            self.disable_effect(PySI.CollisionCapability.MOVE, True)
            if self.move_target is not None:
                self.move_target.on_move_leave_recv(*self.on_move_leave_emit(self.move_target))

    @SIEffect.on_continuous(PySI.CollisionCapability.ASSIGN, SIEffect.RECEPTION)
    def on_assign_continuous_recv(self, effect_to_assign, effect_display_name, kwargs):
        if self.left_mouse_active:
            if self.assigned_effect != effect_to_assign:
                self.assigned_effect = effect_to_assign
                self.assign_effect(self.assigned_effect, effect_display_name, kwargs)

    @SIEffect.on_continuous("ImageEditorAssign", SIEffect.RECEPTION)
    def on_image_editor_assign_continuous_recv(self):
        pass

    @SIEffect.on_enter(PySI.CollisionCapability.HOVER, SIEffect.EMISSION)
    def on_hover_enter_emit(self, other):
        pass

    @SIEffect.on_leave(PySI.CollisionCapability.HOVER, SIEffect.EMISSION)
    def on_hover_leave_emit(self, other):
        pass

    @SIEffect.on_continuous("ToolActivation", SIEffect.EMISSION)
    def on_tool_activation_continuous_emit(self, other):
        if self.left_mouse_active:
            self.disable_effect(PySI.CollisionCapability.SKETCH, True)
            self.is_drawing_blocked = True
            return True
        else:
            self.is_drawing_blocked = False

        return False

    @SIEffect.on_leave("HIDE_TOOL", SIEffect.RECEPTION)
    def on_hide_tool_leave_recv(self):
        for tool in self.image_editor_tool:
            tool.delete()