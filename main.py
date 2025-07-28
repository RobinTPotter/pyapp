from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from android.permissions import request_permissions, Permission
from jnius import autoclass, PythonJavaClass, java_method
import time
import os

class PictureCallback(PythonJavaClass):
    __javainterfaces__ = ['android/hardware/Camera$PictureCallback']
    __javacontext__ = 'app'

    def __init__(self, save_path):
        super().__init__()
        self.save_path = save_path

    @java_method('([BLandroid/hardware/Camera;)V')
    def onPictureTaken(self, data, camera):
        FileOutputStream = autoclass('java.io.FileOutputStream')
        fos = FileOutputStream(self.save_path)
        fos.write(data)
        fos.close()
        print(f"Saved photo to: {self.save_path}")
        camera.startPreview()

class AndroidCameraApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')
        self.capture_btn = Button(text='Take Picture')
        self.capture_btn.bind(on_press=self.take_picture)
        layout.add_widget(self.capture_btn)
        return layout

    def on_start(self):
        request_permissions([
            Permission.CAMERA,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.READ_EXTERNAL_STORAGE,
        ])
        self.setup_camera()

    def setup_camera(self):
        Camera = autoclass('android.hardware.Camera')
        self.Camera = Camera
        self.camera = Camera.open(0)
        self.camera.startPreview()

    def take_picture(self, instance):
        Environment = autoclass('android.os.Environment')
        File = autoclass('java.io.File')
        pictures_dir = Environment.getExternalStoragePublicDirectory(
            Environment.DIRECTORY_PICTURES).getAbsolutePath()
        app_folder = os.path.join(pictures_dir, "MyKivyPyjniusPhotos")
        os.makedirs(app_folder, exist_ok=True)

        filename = f"photo_{int(time.time())}.jpg"
        full_path = os.path.join(app_folder, filename)

        callback = PictureCallback(full_path)
        self.camera.takePicture(None, None, callback)

    def on_stop(self):
        if self.camera:
            self.camera.stopPreview()
            self.camera.release()

if __name__ == '__main__':
    AndroidCameraApp().run()
