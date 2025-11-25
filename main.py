from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.properties import StringProperty
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

class RightWidget(Widget):
    update_callback = None
    name = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self.color = Color(1, 0, 0, 1) 
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)


    def update_rect(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size
        print(instance, instance.rect.pos, instance.rect.size)


    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            self._last_pos = touch.pos
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            dx = touch.pos[0] - self._last_pos[0]
            dy = touch.pos[1] - self._last_pos[1]
            self._last_pos = touch.pos

            if self.update_callback:
                self.update_callback(f"{self.name} Widget Drag dx={dx:.2f} dy={dy:.2f}")

            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            return True
        return super().on_touch_up(touch)



class DemoApp(App):

    def build(self):
        root = AnchorLayout()

        layout = FloatLayout()
        root.add_widget(layout)

        # ---------------------------------------------------------------------
        # Center area
        # ---------------------------------------------------------------------

        # This AnchorLayout will correctly centre the label
        center_anchor = AnchorLayout(
            size_hint=(0.9, 1),
            pos_hint={"x": 0, "y": 0}
        )

        self.center_label = Label(
            text="Center Widget: Ready",
            font_size=24,
            text_size=(None, None),
            halign="center",
            valign="middle"
        )

        center_anchor.add_widget(self.center_label)

        # This widget handles panning but does NOT hold the label
        center_touch = RightWidget(
            size_hint=(0.9, 1),
            pos_hint={"x": 0, "y": 0}
        )
        center_touch.name = "centre"
        center_touch.update_callback = self.update_center_label
        # Update the color of the existing Color instruction
        center_touch.color.rgba = (1, 1, 1, 1)  # Semi-transparent blue

        # ---------------------------------------------------------------------
        # Right widget
        # ---------------------------------------------------------------------

        right = RightWidget(
            size_hint=(0.1, 1),
            pos_hint={"right": 1, "y": 0}
        )
        right.name = "right"
        right.update_callback = self.update_center_label
        print(dir(right))
        print(dir(right.properties))


        # Add touch areas first so AnchorLayout overlays them visually
        layout.add_widget(center_touch)
        layout.add_widget(center_anchor)
        layout.add_widget(right)

        return root



    def update_center_label(self, msg):
        self.center_label.text = msg
        self.center_label.color = (0, 0, 0, 1) # Black text


if __name__ == "__main__":
    DemoApp().run()


