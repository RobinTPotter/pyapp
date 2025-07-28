from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.camera import Camera
from kivy.uix.button import Button
from kivy.uix.image import Image
import os
import time

class CameraApp(App):
    def build(self):
        layout = FloatLayout()

        # Camera widget (may be limited on Android)
        self.camera = Camera(play=True, resolution=(1920, 1080))
        self.camera.size_hint = (1, 1)
        self.camera.pos_hint = {'x':0, 'y':0}
        layout.add_widget(self.camera)

        # Semi-transparent overlay image
        overlay_img = Image(source='overlay.png', size_hint=(1.0,1.0),
                            pos_hint={'center_x':0.5, 'center_y':0.5},
                            opacity=0.5)
        layout.add_widget(overlay_img)

        # Button on top
        btn = Button(text='Capture', size_hint=(0.2, 0.1),
                     pos_hint={'right':1, 'y':0})
        btn.bind(on_press=self.capture_image)
        layout.add_widget(btn)

        return layout

    def on_start(self):
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.CAMERA,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
            ])
        except:
            print("possibly not android")
        self.image_folder = self.get_image_folder()

    def get_image_folder(self):
        try:
            from jnius import autoclass
            Environment = autoclass('android.os.Environment')
            pictures_dir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_PICTURES).getAbsolutePath()
        except:
            print("possibly not android")
            pictures_dir = "./"

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
