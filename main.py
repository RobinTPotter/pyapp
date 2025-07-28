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
        layout = BoxLayout(orientation='vertical')

        # Camera preview
        self.camera = Camera(play=True)
        self.camera.resolution = (640, 480)
        layout.add_widget(self.camera)

        # Transparent overlay image (same size as camera preview)
        self.overlay = Image(source='overlay.png', allow_stretch=True, keep_ratio=False)
        layout.add_widget(self.overlay)

        # Capture button
        capture_btn = Button(text="Capture")
        capture_btn.bind(on_press=self.capture_image)
        layout.add_widget(capture_btn)

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
