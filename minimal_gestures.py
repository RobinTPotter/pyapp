
"""
minimal_gestures.py

Minimal gesture support:
- on_touch_down/up/move works normally (Android & Windows)
- Right-drag on Windows is converted to two-finger pan
- Small Windows patch prevents right-click being treated as touch
"""

from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.utils import platform

# Windows patch: prevent right-click producing phantom touch
if platform == "win":
    try:
        _orig_on_mouse_down = getattr(Window, "on_mouse_down", None)
        def _patched_on_mouse_down(self, x, y, button, modifiers):
            if button == "right":
                return True  # swallow touch event
            if _orig_on_mouse_down:
                return _orig_on_mouse_down(self, x, y, button, modifiers)
            return False
        Window.on_mouse_down = _patched_on_mouse_down
    except Exception:
        pass

class MinimalGestures(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._right_drag_active = False
        self._prev_pos = None
        Window.bind(on_mouse_down=self._on_mouse_down,
                    on_mouse_up=self._on_mouse_up,
                    on_mouse_move=self._on_mouse_move)

    def _on_mouse_down(self, window, x, y, button, modifiers):
        if button == "right":
            self._right_drag_active = True
            self._prev_pos = (x, y)
        return True

    def _on_mouse_up(self, window, x, y, button, modifiers):
        if button == "right":
            self._right_drag_active = False
            self._prev_pos = None
        return True

    def _on_mouse_move(self, window, x, y, modifiers):
        if self._right_drag_active and self._prev_pos:
            dx = x - self._prev_pos[0]
            dy = y - self._prev_pos[1]
            self.on_two_finger_pan(dx, dy)
            self._prev_pos = (x, y)
        return True

    # Override in your app
    def on_two_finger_pan(self, dx, dy):
        print("Two-finger pan:", dx, dy)
