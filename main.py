from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.button import Button
from kivy.uix.image import Image
from android.permissions import request_permissions, Permission
from jnius import autoclass
import os
import time

class CameraApp(App):
    def build(self):
        layout = FloatLayout()

        # Camera widget (may be limited on Android)
        cam = Camera(play=True, resolution=(1920, 1080))
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

    def on_start(self):
        request_permissions([
            Permission.CAMERA,
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
        ])
        self.image_folder = self.get_image_folder()

    def get_image_folder(self):
        Environment = autoclass('android.os.Environment')
        pictures_dir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES).getAbsolutePath()
        app_folder = os.path.join(pictures_dir, 'MyKivyApp')
        os.makedirs(app_folder, exist_ok=True)
        return app_folder

    def capture_image(self, instance):
        filename = f"photo_{int(time.time())}.jpg"
        path = os.path.join(self.image_folder, filename)
        self.camera.export_to_png(path)
        print(f"Image saved to: {path}")

if __name__ == '__main__':
    CameraApp().run()
