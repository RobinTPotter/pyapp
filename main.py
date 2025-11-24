from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.window import Window


class CenterWidget(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.label = Label(text="Center widget: touch me", font_size=24)
        self.add_widget(self.label)
        self._last_touch = None

    def on_touch_down(self, touch):
        # Accept right mouse OR multitouch OR single touch
        if self.collide_point(*touch.pos):
            if "button" in touch.profile and touch.button == "right":
                touch.grab(self)
                self._last_touch = touch.pos
                return True
            elif len(touch.device.touches) > 1:
                touch.grab(self)
                self._last_touch = touch.pos
                return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            if self._last_touch:
                x, y = touch.pos
                self.label.text = f"Center drag: x={x:.1f}, y={y:.1f}"
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self._last_touch = None
            return True
        return super().on_touch_up(touch)


class RightWidget(BoxLayout):
    def __init__(self, center_widget, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.center_widget = center_widget
        self.label = Label(text="Right widget\nDrag me", font_size=20)
        self.add_widget(self.label)
        self._last_pos = None

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            self._last_pos = touch.pos
            return True
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            if self._last_pos:
                dx = touch.pos[0] - self._last_pos[0]
                dy = touch.pos[1] - self._last_pos[1]
                self.center_widget.label.text = f"Right drag: dx={dx:.1f}, dy={dy:.1f}"
                self._last_pos = touch.pos
            return True
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            self._last_pos = None
            return True
        return super().on_touch_up(touch)


class MainLayout(AnchorLayout):
    pass


class TestApp(App):
    def build(self):
        root = MainLayout()

        # Central widget
        center = CenterWidget(size_hint=(0.9, 1))

        # Right widget (10% width)
        right = RightWidget(center_widget=center, size_hint=(0.1, 1))

        # Add widgets positioned correctly
        root.add_widget(center)
        root.add_widget(right)

        return root


if __name__ == "__main__":
    TestApp().run()


