from libPySI import PySI
from plugins.standard_environment_library.SIEffect import SIEffect
from plugins.standard_environment_library.lasso.Lasso import Lasso
from plugins.standard_environment_library._standard_behaviour_mixins.Lassoable import Lassoable
import subprocess
from threading import Thread
import time

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
        
        self._middle_mouse_blocked_lasso = None
        self.abs_pos_x_at_middle_mouse_click_begin = None
        self.abs_pos_y_at_middle_mouse_click_begin = None
        
        self.selected_lassoable = None # lassoable is selected on right click
        self.selected_lasso = None # lasso is selected on right click
        self.debug = True
        self.start_test_thread()

    #def mouse_wheel_angle_px(self, px):
    #    SIEffect.debug("mouse_wheel_angle_px {}".format(px))
        
    #def mouse_wheel_angle_degrees(self, degrees):
    #    SIEffect.debug("mouse_wheel_angle_degrees {}".format(degrees))
    
    def start_test_thread(self):
        try:
            t = Thread(target=self.test_thread, args=(2,))
            t.start()
        except:
            if SIEffect.is_logging():
                SIEffect.debug("Start Test Thread failed")
    
    # Define a function for the thread
    def test_thread(self, delay):
        time.sleep(delay)
        proc = subprocess.Popen(["xmessage","Bitte Textdateien in einen eigenen Ordner geben und alle Bilddateien in einen eigenen Ordner geben!"])
        proc.wait(1000)
        SIEffect.debug("finished")

    def on_middle_mouse_click(self, is_active):
        if SIEffect.is_logging():
            SIEffect.debug("Cursor: on_middle_mouse_click {}".format(is_active))
        if is_active:
            lassos = SIEffect.get_all_objects_extending_class(Lasso)
            for lasso in lassos:
                if lasso.contains_point(self.absolute_x_pos(), self.absolute_y_pos()):
                    #lasso.collapse_bubble()
                    self._middle_mouse_blocked_lasso = lasso
                    lasso.set_block_remove_link(True) # workaround for the remove_link bug
                    self.abs_pos_x_at_middle_mouse_click_begin = self.absolute_x_pos()
                    self.abs_pos_y_at_middle_mouse_click_begin = self.absolute_x_pos()
                    self.morph_bubble(lasso, True)
                    break
        else:
            # workaround for the remove_link bug
            if self._middle_mouse_blocked_lasso != None:
                self._middle_mouse_blocked_lasso.set_block_remove_link(False)
                self.morph_bubble(self._middle_mouse_blocked_lasso, False)
                self._middle_mouse_blocked_lasso = None

    def morph_bubble(self, lasso, is_active):
        if is_active:
            lasso.collapse_or_expand_bubble()
            
        else:
            pass

    # This is for the spread tool and should be used instead of morp_bubble
    def morph_bubble2(self, lasso, is_active):
        if is_active:
            if PySI.CollisionCapability.MOVE not in self.cap_emit.keys():
                if SIEffect.is_logging():
                    SIEffect.debug("Cursor: on_middle_mouse_click2 {}".format(is_active))
                self.enable_effect(PySI.CollisionCapability.MOVE, True, self.on_middle_mouse_move_enter_emit, self.on_middle_mouse_move_continuous_emit, self.on_middle_mouse_move_leave_emit)
                #spreading is done by on_middle_mouse_move_continuous_emit
                lasso.spread_bubble_init()
        else:
            if PySI.CollisionCapability.MOVE in self.cap_emit.keys():
                self.disable_effect(PySI.CollisionCapability.MOVE, True)

    def on_middle_mouse_move_enter_emit(self, other):
        if SIEffect.is_logging():
            SIEffect.debug("Cursor: on_middle_mouse_move_enter_emit other={}".format(other))
        return "", ""

    def on_middle_mouse_move_continuous_emit(self, other):
        factor = (self.absolute_x_pos() - self.abs_pos_x_at_middle_mouse_click_begin) / 300.0; # 300 pixel is factor 1.0
        if SIEffect.is_logging():
            SIEffect.debug("Cursor: on_middle_mouse_move_continuous_emit {}".format(factor))
        self._middle_mouse_blocked_lasso.spread_bubble(factor)
    
    def on_middle_mouse_move_leave_emit(self, other):
        return "", ""
    
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
        if self.debug or SIEffect.is_logging():
            SIEffect.debug("Cursor: on_move_enter_emit other={}".format(other))
        if self.move_target is None:
            if self.selected_lassoable != None:
                self.move_target = self.selected_lassoable
            else:
                self.move_target = other
        
        if self.move_target is other:
            return self._uuid, PySI.LinkingCapability.POSITION
        
        return "", ""

    def on_move_continuous_emit(self, other):
        #if self.debug or SIEffect.is_logging():
        #    SIEffect.debug("Cursor: on_move_continuous_emit other={}".format(other))
        pass
        #if self.selected_lassoable != None:
        #    self.selected_lassoable.move(self.x, self.y)
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
        Cursor.set_workaround_active(False)

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
        if self.debug or SIEffect.is_logging():
            SIEffect.debug("Cursor: move cursor2 active={} {},{} {},{}".format(is_active, self.absolute_x_pos(), self.absolute_y_pos(), self.get_region_width(), self.get_region_height()))
            #SIEffect.debug("Cursor: 1 {},{} {},{}".format(self.absolute_x_pos(), self.absolute_y_pos(), self.get_region_width(), self.get_region_height()))
        #l = SIEffect.get_all_objects_extending_class(Lasso)
        #if self.debug or SIEffect.is_logging():
            #SIEffect.debug("Cursor: 2 {}".format(len(l)))
            #for ls in l:
            #    SIEffect.debug("Cursor: 3 {}".format(ls.get_uuid()))
            #    SIEffect.debug("Cursor: 4 {},{} {},{}".format(ls.absolute_x_pos(), ls.absolute_y_pos(), ls.get_region_width(), ls.get_region_height()))

        self.right_mouse_active = is_active
        #if self.debug or SIEffect.is_logging():
        #    SIEffect.debug("Cursor: move cursor22 {}".format(is_active))

        Cursor.set_workaround_active(True)
        if is_active:
            self.selected_lassoable, sel_lassoable_lasso = self.cursor_tip_selects_lassoable() # to move lassoables out of bubbles
            if self.selected_lassoable == None:
                self.selected_lasso = self.cursor_tip_selects_lasso()
                if self.selected_lasso != None and self.move_target is None:
                    self.move_target = self.selected_lasso
                    SIEffect.debug("Cursor: move cursor inlasso")
                    for l in self.selected_lasso.get_linked_lassoables():
                        SIEffect.debug("Cursor: move cursor inlasso linked lassoables {}".format(l.get_uuid()))
                    #self.start_collision_bug_workaround()
                    self.selected_lasso.link_position_to_cursor(self.get_uuid())
            #if sel_lassoable_lasso != None:
            #    #sel_lassoable_lasso.self.is_under_user_control = False
            #    sel_lassoable_lasso.set_position_redirection(self.selected_lassoable)
            
            #if self.debug or SIEffect.is_logging():
            #    SIEffect.debug("Cursor: move cursor23 {}".format(PySI.CollisionCapability.MOVE not in self.cap_emit.keys()))
            if PySI.CollisionCapability.MOVE not in self.cap_emit.keys():
                SIEffect.debug("Cursor: move cursor enable effect")
                self.enable_effect(PySI.CollisionCapability.MOVE, True, self.on_move_enter_emit, self.on_move_continuous_emit, self.on_move_leave_emit)
            else:
                SIEffect.debug("Cursor: move cursor not enable effect")
            self.block_lassoable_events(True)
        elif PySI.CollisionCapability.MOVE in self.cap_emit.keys():
            self.disable_effect(PySI.CollisionCapability.MOVE, True)
            mt = self.move_target
            if self.move_target is not None:
                SIEffect.debug("Cursor: move target={}".format(self.move_target))
                self.move_target.on_move_leave_recv(*self.on_move_leave_emit(self.move_target))
            self.block_lassoable_events(False)
            #all_lassos = SIEffect.get_all_objects_extending_class(Lasso)
            #for l in all_lassos:
            #    l.set_position_redirection(None)
            if self.selected_lasso != None:
                self.selected_lasso.unlink_position_to_cursor(self.get_uuid())
            self.selected_lassoable = None
            self.selected_lasso = None
            SIEffect.debug("Cursor: move target2={}".format(mt))
            if mt is not None:
                mt.process_collision() # workaround for the collision detection bug
            self.move_target = None
        else:
            self.block_lassoable_events(False)
            self.move_target = None

    @staticmethod
    def set_workaround_active(is_active):
        all_lassoable = SIEffect.get_all_objects_extending_class(Lassoable);
        for l in all_lassoable:
            l.set_workaround_active(is_active)
    
    # Check if a lassoable is selected by the tip of the cursor.
    # If that is the case, the lassoable will be unlinked from a bubble
    # Only the first found lassoable will be returned
    def cursor_tip_selects_lassoable(self):
        cx,cy = self.absolute_x_pos(), self.absolute_y_pos()
        all_lassoables = SIEffect.get_all_objects_extending_class(Lassoable)
        for l in all_lassoables:
            if l.contains_point(cx,cy):
                linked_bubbles = l.get_all_lnk_sender_extending_class(Lasso)
                if len(linked_bubbles) > 0:
                    # the cursor selected a lassoable, which is linked to ab bubble.
                    # Since the lassoable should move, the lassoable be unlinked from the bubble
                    l.relink_to_new_bubble(linked_bubbles[0].get_uuid(), None)
                    return l, linked_bubbles[0]
        return None, None
                 
    # Check if a lasso is selected by the tip of the cursor.
    def cursor_tip_selects_lasso(self):
        cx,cy = self.absolute_x_pos(), self.absolute_y_pos()
        all_lasso = SIEffect.get_all_objects_extending_class(Lasso)
        for l in all_lasso:
            if l.contains_point(cx,cy): # fast check bounding box
                return l
                #if l.polygon_contains_point(cx,cy): # slow check exact boundary
                #    return l
        return None
           
    def block_lassoable_events(self, is_active):
        all_lassoables = SIEffect.get_all_objects_extending_class(Lassoable)
        for l in all_lassoables:
            l.set_ignore_lasso_capability(is_active)
    
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