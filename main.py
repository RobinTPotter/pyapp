from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.camera import Camera
from kivy.uix.button import Button
from kivy.uix.image import Image

class CameraOverlayApp(App):
    def build(self):
        layout = FloatLayout()

        # Camera widget (may be limited on Android)
        cam = Camera(play=True, resolution=(640, 480))
        cam.size_hint = (1, 1)
        cam.pos_hint = {'x':0, 'y':0}
        layout.add_widget(cam)

        # Semi-transparent overlay image
        overlay_img = Image(source='overlay.png', size_hint=(0.5, 0.5),
                            pos_hint={'center_x':0.5, 'center_y':0.5},
                            opacity=0.5)
        layout.add_widget(overlay_img)

        # Button on top
        btn = Button(text='Capture', size_hint=(0.2, 0.1),
                     pos_hint={'right':1, 'y':0})
        layout.add_widget(btn)

        return layout

if __name__ == '__main__':
    CameraOverlayApp().run()


