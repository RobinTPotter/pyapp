
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from minimal_gestures import MinimalGestures
from kivy.uix.label import Label

class Demo(MinimalGestures):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.label = Label(text="Drag right mouse or two fingers")
        self.add_widget(self.label)

    def on_touch_down(self, touch):
        self.label.text = f"Touch down at {int(touch.x)},{int(touch.y)}"
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        self.label.text = f"Touch move at {int(touch.x)},{int(touch.y)}"
        return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        self.label.text = f"Touch up at {int(touch.x)},{int(touch.y)}"
        return super().on_touch_up(touch)

    def on_two_finger_pan(self, dx, dy):
        self.label.text = f"Two-finger pan dx={int(dx)}, dy={int(dy)}"

class TestApp(App):
    def build(self):
        root = BoxLayout(orientation="vertical")
        demo = Demo()
        root.add_widget(demo)
        root.add_widget(demo.label)
        return root

if __name__ == "__main__":
    TestApp().run()
