from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.button import Button
from kivy.utils import platform
import time
import os

if platform == 'android':
    from android.permissions import request_permissions, Permission
    from jnius import autoclass, PythonJavaClass, java_method

    class PictureCallback(PythonJavaClass):
        __javainterfaces__ = ['android/hardware/Camera$PictureCallback']
        __javacontext__ = 'app'

        def __init__(self, path, app):
            super().__init__()
            self.path = path
            self.app = app

        @java_method('([BLandroid/hardware/Camera;)V')
        def onPictureTaken(self, data, camera):
            FileOutputStream = autoclass('java.io.FileOutputStream')
            fos = FileOutputStream(self.path)
            fos.write(data)
            fos.close()
            print(f"Saved photo to: {self.path}")
            camera.release()
            self.app.restore_kivy_preview()

class HybridCameraApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical')
        self.camera = Camera(resolution=(640, 480), play=True)
        self.layout.add_widget(self.camera)

        btn = Button(text="Take Picture")
        btn.bind(on_press=self.capture_image)
        self.layout.add_widget(btn)

        return self.layout

    def on_start(self):
        if platform == 'android':
            request_permissions([
                Permission.CAMERA,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE,
            ])

    def restore_kivy_preview(self):
        self.camera = Camera(resolution=(640, 480), play=True)
        self.layout.add_widget(self.camera, index=1)

    def capture_image(self, instance):
        if platform != 'android':
            filename = f"photo_{int(time.time())}.png"
            self.camera.export_to_png(filename)
            print(f"Saved screenshot to {filename}")
        else:
            # Android-specific high-res capture
            self.layout.remove_widget(self.camera)
            self.camera.play = False

            Camera = autoclass('android.hardware.Camera')
            Environment = autoclass('android.os.Environment')
            pictures_dir = Environment.getExternalStoragePublicDirectory(
                Environment.DIRECTORY_PICTURES).getAbsolutePath()
            folder = os.path.join(pictures_dir, "MyKivyPyjniusPhotos")
            os.makedirs(folder, exist_ok=True)

            filename = f"photo_{int(time.time())}.jpg"
            full_path = os.path.join(folder, filename)

            cam = Camera.open(0)
            callback = PictureCallback(full_path, self)
            cam.takePicture(None, None, callback)

if __name__ == '__main__':
    HybridCameraApp().run()
