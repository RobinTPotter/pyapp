from kivy.config import Config
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import *
from kivy.core.window import Window

Config.set('kivy','pause_on_minimize', 1)
Window.clearcolor = (1, 1, 1, 1)

class Spots(Widget):
    def __init__(self, **kwargs):
        super(Spots, self).__init__(**kwargs)
        print(self.size)
        self.bind(size=self.update_canvas)
        self.bind(pos=self.update_canvas)
        self.py = 0.2828
        self.spacex = 100
        self.drawing = False
        self.lines = []
        self.origin = [0, 0]
        self.scale = 1.0
        self.base_grid = []
        # Track pinch zoom
        self.pinch_start_distance = None
        self.pinch_start_scale = None
        self.update_canvas()

    def find_nearest_point(self, x, y):
        from math import sqrt
        nearest_point = None
        min_distance = float('inf')
        for px, py in self.grid:
            distance = sqrt((px - x)**2 + (py - y)**2)
            if distance < min_distance:
                min_distance = distance
                nearest_point = [px, py]

        return nearest_point

    def update_canvas(self, *args):
        # Calculate the visible area considering pan and scale
        margin = 200  # Extra margin to pre-generate dots
        scaled_spacex = self.spacex * self.scale
        scaled_spacey = int(scaled_spacex * self.py)
        
        self.canvas.clear()
        
        # Calculate grid bounds based on current viewport
        min_x = int((-self.origin[0] - margin) / scaled_spacex) * int(scaled_spacex)
        max_x = int((-self.origin[0] + self.size[0] + margin) / scaled_spacex + 1) * int(scaled_spacex)
        min_y = int((-self.origin[1] - margin) / scaled_spacey) * scaled_spacey
        max_y = int((-self.origin[1] + self.size[1] + margin) / scaled_spacey + 1) * scaled_spacey
        
        # Generate base grid for visible area (avoid duplicates using a set)
        new_points = set()
        row_index = int(min_y / scaled_spacey)
        for y in range(min_y, max_y, scaled_spacey):
            row_index += 1
            for x in range(min_x, max_x, int(scaled_spacex)):
                grid_x = x + (int(scaled_spacex/2) if row_index%2==0 else 0)
                grid_y = y
                new_points.add((grid_x, grid_y))
        
        # Update base_grid, adding only new points
        existing_points = set((p[0], p[1]) for p in self.base_grid)
        for point in new_points:
            if point not in existing_points:
                self.base_grid.append([point[0], point[1]])
        
        # Create transformed grid for display and hit testing
        self.grid = [[p[0] + self.origin[0], p[1] + self.origin[1]] for p in self.base_grid]
        
        with self.canvas:
            Color(0.3,0.3,0.3)
            for p in self.grid:
                p = (p[0]-1, p[1]-1)
                Ellipse(pos = p, size=[2,2])
            
            Color(0,0,0,1)
            for line in self.lines:
                Color(0,0,0,1)
                # Apply origin offset to line coordinates when drawing
                start_x = line[0][0] + self.origin[0]
                start_y = line[0][1] + self.origin[1]
                end_x = line[1][0] + self.origin[0]
                end_y = line[1][1] + self.origin[1]
                Line(points=[start_x, start_y, end_x, end_y])




    def on_touch_down(self, touch):
        # Track touches for multitouch gestures
        if not hasattr(self, 'active_touches'):
            self.active_touches = {}
        self.active_touches[touch.uid] = touch
        
        # Check for pinch zoom (two non-mouse touches)
        non_mouse_touches = [t for t in self.active_touches.values() if getattr(t, 'device', 'mouse') != 'mouse']
        if len(non_mouse_touches) >= 2:
            # Start pinch zoom
            from math import sqrt
            t1, t2 = list(non_mouse_touches)[:2]
            dx = t2.pos[0] - t1.pos[0]
            dy = t2.pos[1] - t1.pos[1]
            self.pinch_start_distance = sqrt(dx*dx + dy*dy)
            self.pinch_start_scale = self.scale
            return True
        
        # Right mouse button = pan, Left mouse button = draw, Double-tap = undo
        button = getattr(touch, 'button', 'left')
        
        if button == 'right':
            # Right-click to pan
            self.pan_start = (touch.pos[0], touch.pos[1])
            return True
        
        if touch.is_double_tap:
            print("double tap - clearing last")
            if len(self.lines)>0: self.lines.pop()
            self.update_canvas()
            return
        
        # Left-click to draw
        self.start = self.find_nearest_point(touch.pos[0], touch.pos[1])
        self.drawing = True

    def on_touch_up(self, touch):
        # Remove touch from tracking
        if hasattr(self, 'active_touches') and touch.uid in self.active_touches:
            del self.active_touches[touch.uid]
        
        # Check if we should end pinch zoom
        if hasattr(self, 'active_touches'):
            non_mouse_touches = [t for t in self.active_touches.values() if getattr(t, 'device', 'mouse') != 'mouse']
            if len(non_mouse_touches) < 2:
                self.pinch_start_distance = None
                self.pinch_start_scale = None
        
        button = getattr(touch, 'button', 'left')
        
        if button == 'right':
            # End panning
            self.pan_start = None
            return True
        
        print(f"up {touch}")
        
        # Finalize line drawing
        self.end = self.find_nearest_point(touch.pos[0], touch.pos[1])
        if self.drawing and self.start != self.end:
            # Store lines in base coordinates (without origin offset)
            start_base = [self.start[0] - self.origin[0], self.start[1] - self.origin[1]]
            end_base = [self.end[0] - self.origin[0], self.end[1] - self.origin[1]]
            self.lines.append((start_base, end_base))
            print(f"number of lines {len(self.lines)}")
            self.update_canvas()
        
        print(f"{self.start} to {self.end}")
        
        self.canvas.remove_group('temp_line')
        self.drawing = False

    def on_touch_move(self, touch):
        # Handle mouse wheel zoom (or trackpad two-finger scroll)
        if touch.is_mouse_scrolling:
            zoom_factor = 1.1 if touch.button == 'scrolldown' else 0.9 if touch.button == 'scrollup' else 1.0
            if zoom_factor != 1.0:
                self.scale = max(0.5, min(3.0, self.scale * zoom_factor))
                self.update_canvas()
                return True
        
        # Handle pinch zoom
        if hasattr(self, 'active_touches'):
            non_mouse_touches = [t for t in self.active_touches.values() if getattr(t, 'device', 'mouse') != 'mouse']
            if len(non_mouse_touches) >= 2 and self.pinch_start_distance is not None:
                from math import sqrt
                t1, t2 = list(non_mouse_touches)[:2]
                dx = t2.pos[0] - t1.pos[0]
                dy = t2.pos[1] - t1.pos[1]
                current_distance = sqrt(dx*dx + dy*dy)
                
                # Calculate new scale
                scale_factor = current_distance / self.pinch_start_distance
                self.scale = max(0.5, min(3.0, self.pinch_start_scale * scale_factor))  # Limit scale between 0.5x and 3x
                
                self.update_canvas()
                return True
        
        button = getattr(touch, 'button', 'left')
        
        # Handle right-click panning
        if button == 'right' and self.pan_start is not None:
            # Calculate the delta movement
            dx = touch.pos[0] - self.pan_start[0]
            dy = touch.pos[1] - self.pan_start[1]
            
            # Update origin
            self.origin[0] += dx
            self.origin[1] += dy
            
            # Update canvas with new origin
            self.update_canvas()
            
            # Update pan start for next move
            self.pan_start = (touch.pos[0], touch.pos[1])
            return True
        
        # Handle left-click drawing
        self.end = self.find_nearest_point(touch.pos[0], touch.pos[1])
        if self.drawing:
            self.canvas.remove_group('temp_line')
            with self.canvas:
                Color(0,0,0,1)
                with self.canvas:
                    Color(0,1,0,0.5, group='temp_line')
                    Line(points=self.start+self.end, width=2, group='temp_line')
                print(f"{self.start} to {self.end}")

class IsoDraw(App):
    def build(self):
        return Spots()
 
    def on_pause(self):
        print("pausing")

if __name__=="__main__":
    IsoDraw().run()
