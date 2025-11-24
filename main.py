from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.properties import StringProperty
from kivy.core.window import Window


class CenterWidget(Widget):
    message = StringProperty("Center Widget: Ready")

    def on_touch_down(self, touch):
        # Only handle right-click or multi-touch (panning)
        if self.collide_point(*touch.pos):
            if touch.button == 'right' or len(touch.device.touches) >= 2:
                touch.grab(self)
                self._last_pos = touch.pos
                return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            dx = touch.pos[0] - self._last_pos[0]
            dy = touch.pos[1] - self._last_pos[1]
            self._last_pos = touch.pos

            self.message = f"Panning Center: pos=({int(touch.x)}, {int(touch.y)})"

            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            return True
        return super().on_touch_up(touch)


class RightWidget(Widget):
    update_callback = None

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
                self.update_callback(f"Right Widget Drag dx={dx:.2f} dy={dy:.2f}")

            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            return True
        return super().on_touch_up(touch)


class RootLayout(AnchorLayout):
    pass


class DemoApp(App):

    def build(self):
        root = AnchorLayout()

        layout = FloatLayout()
        root.add_widget(layout)

        # Center Widget
        self.center_label = Label(text="Center Widget: Ready",
                                  font_size=24,
                                  pos_hint={"center_x": .5, "center_y": .5})

        center = CenterWidget(
            size_hint=(0.9, 1),
            pos_hint={"x": 0, "y": 0}
        )
        center.add_widget(self.center_label)

        # Update label when center widget pans
        center.bind(message=lambda inst, msg: self.update_center_label(msg))

        # Right Widget (10% width)
        right = RightWidget(
            size_hint=(0.1, 1),
            pos_hint={"right": 1, "y": 0}
        )
        right.update_callback = self.update_center_label

        layout.add_widget(center)
        layout.add_widget(right)

        return root

    def update_center_label(self, msg):
        self.center_label.text = msg


if __name__ == "__main__":
    DemoApp().run()


