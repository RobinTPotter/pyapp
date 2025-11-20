from kivy.config import Config
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import *
from kivy.core.window import Window
from kivy.utils import platform

Config.set('kivy','pause_on_minimize', 1)
Window.clearcolor = (1, 1, 1, 1)

class Spots(Widget):
    def __init__(self, **kwargs):
        super(Spots, self).__init__(**kwargs)
        print(self.size)
        self.bind(size=self.update_canvas)
        self.bind(pos=self.update_canvas)
        self.py = 0.28
        self.spacex = 100
        self.lines = []
        self.origin = [0, 0]
        self.scale = 1.0
        self.base_grid = []
        
        # State machine for actions
        self.can_pan = False
        self.is_pan = False
        self.pan_start_pos = None
        self.pan_end_pos = None
        
        self.can_zoom = False
        self.is_zoom = False
        self.zoom_start_distance = None
        self.zoom_start_scale = None
        
        self.can_draw = False
        self.is_draw = False
        self.draw_start_pos = None
        self.draw_end_pos = None
        
        # Track pinch zoom and pan
        self.active_touches = {}
        # Throttle grid updates
        self.last_grid_bounds = None
        # Detect platform
        self.is_mobile = platform in ('android', 'ios')
        print(f"Platform: {platform}, Mobile: {self.is_mobile}")
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
    
    def get_two_touch_geometry(self, touches_list):
        """Calculate distance and midpoint between two touches"""
        from math import sqrt
        t1, t2 = touches_list[0], touches_list[1]
        dx = t2.pos[0] - t1.pos[0]
        dy = t2.pos[1] - t1.pos[1]
        distance = sqrt(dx*dx + dy*dy)
        midpoint = ((t1.pos[0] + t2.pos[0]) / 2, (t1.pos[1] + t2.pos[1]) / 2)
        return distance, midpoint
    
    def start_pan(self, x, y):
        """Start panning operation"""
        self.pan_start_pos = (x, y)
        self.is_pan = True
        # Cancel any drawing
        self.is_draw = False
        self.can_draw = False
        self.canvas.remove_group('temp_line')
    
    def do_pan(self, x, y):
        """Execute pan movement"""
        if self.pan_start_pos is not None:
            dx = x - self.pan_start_pos[0]
            dy = y - self.pan_start_pos[1]
            self.origin[0] += dx
            self.origin[1] += dy
            self.update_canvas(force_grid_update=False)
            self.pan_start_pos = (x, y)
        self.pan_end_pos = (x, y)
    
    def end_pan(self):
        """End panning operation"""
        self.is_pan = False
        self.can_pan = False
        self.pan_start_pos = None
        self.pan_end_pos = None
    
    def start_zoom(self, distance, scale):
        """Start zoom operation"""
        self.zoom_start_distance = distance
        self.zoom_start_scale = scale
        self.is_zoom = True
    
    def do_zoom(self, scale_factor):
        """Execute zoom"""
        self.scale = max(0.5, min(3.0, scale_factor))
        self.update_canvas(force_grid_update=False)
    
    def end_zoom(self):
        """End zoom operation"""
        self.is_zoom = False
        self.can_zoom = False
        self.zoom_start_distance = None
        self.zoom_start_scale = None
    
    def start_draw(self, x, y):
        """Start drawing a line"""
        if self.can_draw and not self.is_pan and not self.is_zoom:
            self.draw_start_pos = self.find_nearest_point(x, y)
            self.is_draw = True
    
    def update_draw(self, x, y):
        """Update temporary drawing line"""
        if self.is_draw and not self.is_pan and not self.is_zoom:
            self.draw_end_pos = self.find_nearest_point(x, y)
            self.canvas.remove_group('temp_line')
            with self.canvas:
                Color(0,0,0,1)
                with self.canvas:
                    Color(0,1,0,0.5, group='temp_line')
                    Line(points=self.draw_start_pos+self.draw_end_pos, width=2, group='temp_line')
    
    def finish_draw(self, x, y):
        """Finalize drawing a line"""
        if self.is_draw and self.draw_start_pos and not self.is_pan and not self.is_zoom:
            self.draw_end_pos = self.find_nearest_point(x, y)
            if self.draw_start_pos != self.draw_end_pos:
                start_base = [self.draw_start_pos[0] - self.origin[0], self.draw_start_pos[1] - self.origin[1]]
                end_base = [self.draw_end_pos[0] - self.origin[0], self.draw_end_pos[1] - self.origin[1]]
                self.lines.append((start_base, end_base))
                self.update_canvas()
        self.canvas.remove_group('temp_line')
        self.is_draw = False
        self.can_draw = False
        self.draw_start_pos = None
        self.draw_end_pos = None

    def update_canvas(self, *args, force_grid_update=True):
        # Always clear canvas first
        self.canvas.clear()
        
        # Calculate the visible area considering pan and scale
        margin = 200  # Extra margin to pre-generate dots
        scaled_spacex = self.spacex * self.scale
        scaled_spacey = int(scaled_spacex * self.py)
        
        # Calculate grid bounds based on current viewport
        min_x = int((-self.origin[0] - margin) / scaled_spacex) * int(scaled_spacex)
        max_x = int((-self.origin[0] + self.size[0] + margin) / scaled_spacex + 1) * int(scaled_spacex)
        min_y = int((-self.origin[1] - margin) / scaled_spacey) * scaled_spacey
        max_y = int((-self.origin[1] + self.size[1] + margin) / scaled_spacey + 1) * scaled_spacey
        
        current_bounds = (min_x, max_x, min_y, max_y, scaled_spacex, scaled_spacey)
        
        # Only regenerate grid if bounds changed significantly
        if force_grid_update or self.last_grid_bounds != current_bounds:
            self.last_grid_bounds = current_bounds
            
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
            existing_points = {(p[0], p[1]) for p in self.base_grid}
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
        print(f"on_touch_down: button={getattr(touch, 'button', 'none')}, pos={touch.pos}")
        
        # Track touches
        self.active_touches[touch.uid] = touch
        touch_count = len(self.active_touches)
        
        # Handle double-tap undo (works on all platforms)
        if touch.is_double_tap:
            if len(self.lines)>0: self.lines.pop()
            self.update_canvas()
            return True
        
        if self.is_mobile:
            # Mobile: Two fingers = pan and zoom
            if touch_count == 2:
                touches_list = list(self.active_touches.values())
                distance, midpoint = self.get_two_touch_geometry(touches_list)
                
                self.can_zoom = True
                self.can_pan = True
                self.start_zoom(distance, self.scale)
                self.start_pan(midpoint[0], midpoint[1])
                return True
            elif touch_count == 1:
                # Single finger = draw
                self.can_draw = True
                self.start_draw(touch.pos[0], touch.pos[1])
        else:
            # Desktop: Right-click = pan, Left-click = draw
            button = getattr(touch, 'button', 'left')
            if button == 'right':
                self.can_pan = True
                self.start_pan(touch.pos[0], touch.pos[1])
                return True
            elif button == 'left':
                self.can_draw = True
                self.start_draw(touch.pos[0], touch.pos[1])

    def on_motion(self, etype, motionevent):
        """Handle motion events - workaround for Windows right-click bug"""
        print(f"on_motion: etype={etype}, button={getattr(motionevent, 'button', 'none')}, is_pan={self.is_pan}, is_draw={self.is_draw}")
        if etype == 'end':
            # Button released
            button = getattr(motionevent, 'button', 'none')
            print(f"on_motion end: button={button}, is_pan={self.is_pan}, is_draw={self.is_draw}")
            
            # Handle right button release for pan
            if button == 'right' and self.is_pan:
                print(f"Ending pan via on_motion")
                self.end_pan()
                # Remove from active touches
                if motionevent.uid in self.active_touches:
                    del self.active_touches[motionevent.uid]
                return True
        
        return super().on_motion(etype, motionevent)

    def on_touch_up(self, touch):
        # Debug: Print what triggered this
        button = getattr(touch, 'button', 'none')
        print(f"on_touch_up triggered: button={button}, is_pan={self.is_pan}, is_draw={self.is_draw}")
        
        # Remove touch from tracking
        if touch.uid in self.active_touches:
            del self.active_touches[touch.uid]
        
        touch_count = len(self.active_touches)
        
        if self.is_mobile:
            # Mobile: End multitouch when dropping below 2 fingers
            if touch_count < 2:
                if self.is_zoom:
                    self.end_zoom()
                if self.is_pan:
                    self.end_pan()
            
            # Finalize drawing if we were drawing
            if self.is_draw:
                self.finish_draw(touch.pos[0], touch.pos[1])
        else:
            # Desktop: Handle left button (right button handled in on_motion)
            self.is_pan = False
            self.is_zoom = False
            if button == 'left' and self.is_draw:
                print(f"Ending draw - Active Touches: {self.active_touches}")
                self.finish_draw(touch.pos[0], touch.pos[1])
                print(f"After finish_draw - is_pan={self.is_pan}, is_draw={self.is_draw}")
                return True


    def on_touch_move(self, touch):
        # Handle mouse wheel zoom (desktop only)
        if touch.is_mouse_scrolling:
            if touch.button == 'scrolldown':
                self.can_zoom = True
                self.do_zoom(self.scale * 1.1)
                self.can_zoom = False
            elif touch.button == 'scrollup':
                self.can_zoom = True
                self.do_zoom(self.scale * 0.9)
                self.can_zoom = False
            self.update_canvas()
            return True
        
        touch_count = len(self.active_touches)
        
        if self.is_mobile:
            # Mobile: Handle two-finger pan and zoom
            if touch_count >= 2 and (self.is_pan or self.is_zoom):
                touches_list = list(self.active_touches.values())[:2]
                current_distance, current_midpoint = self.get_two_touch_geometry(touches_list)
                
                # Zoom
                if self.is_zoom and self.zoom_start_distance and self.zoom_start_distance > 0:
                    scale_factor = current_distance / self.zoom_start_distance
                    self.do_zoom(self.zoom_start_scale * scale_factor)
                
                # Pan
                if self.is_pan:
                    self.do_pan(current_midpoint[0], current_midpoint[1])
                
                return True
            elif self.is_draw:
                # Single finger drawing
                self.update_draw(touch.pos[0], touch.pos[1])
        else:
            # Desktop: Handle pan or draw based on state
            if self.is_pan:
                self.do_pan(touch.pos[0], touch.pos[1])
                return True
            elif self.is_draw:
                self.update_draw(touch.pos[0], touch.pos[1])

class IsoDraw(App):
    def build(self):
        return Spots()
 
    def on_pause(self):
        print("pausing")

if __name__=="__main__":
    IsoDraw().run()
