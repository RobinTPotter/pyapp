from kivy.config import Config
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import *
from kivy.core.window import Window

Config.set('kivy','pause_on_minimize', 1)
Window.clearcolor = (1, 1, 1, 1)

class ScaleWidget(Widget):
    update_callback = None
    name = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self.color = Color(1, 0, 0, 1) 
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size
        print(instance, instance.rect.pos, instance.rect.size)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            touch.grab(self)
            self._last_pos = touch.pos
            return True
        #return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.grab_current is self:
            dx = touch.pos[0] - self._last_pos[0]
            dy = touch.pos[1] - self._last_pos[1]
            self._last_pos = touch.pos

            if self.update_callback:
                self.update_callback(dx, dy)

            return True
        #return super().on_touch_move(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            touch.ungrab(self)
            return True
        self.update_callback(0,0,True)
        #return super().on_touch_up(touch)


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
        self.scale = 0.75
        self.base_grid = []
        # Track pinch zoom
        self.start = None
        self.end = None
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
        
        # Clear base_grid so only current visible points are used
        self.base_grid = []
        
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
        
        # Add only new points to base_grid
        for point in new_points:
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
                # Apply origin offset and scale to line coordinates when drawing
                start_x = line[0][0] * self.scale + self.origin[0]
                start_y = line[0][1] * self.scale + self.origin[1]
                end_x = line[1][0] * self.scale + self.origin[0]
                end_y = line[1][1] * self.scale + self.origin[1]
                Line(points=[start_x, start_y, end_x, end_y])




    def on_touch_down(self, touch):
        # Only handle touch if it's within this widget's bounds
        if not self.collide_point(*touch.pos):
            return False
        
        if touch.is_double_tap:
            print("double tap - clearing last")
            if len(self.lines)>0: self.lines.pop()
            self.update_canvas()
            return True
        
        # Left-click to draw
        self.start = self.find_nearest_point(touch.pos[0], touch.pos[1])
        self.drawing = True
        return True

    def on_touch_up(self, touch):
        if not self.drawing:
            return False
            
        print(f"up {touch}")
        
        # Finalize line drawing
        self.end = self.find_nearest_point(touch.pos[0], touch.pos[1])
        if self.drawing and self.start != self.end:
            # Store lines in base coordinates (without origin offset and scale)
            start_base = [(self.start[0] - self.origin[0]) / self.scale, (self.start[1] - self.origin[1]) / self.scale]
            end_base = [(self.end[0] - self.origin[0]) / self.scale, (self.end[1] - self.origin[1]) / self.scale]
            self.lines.append((start_base, end_base))
            print(f"number of lines {len(self.lines)}")
            self.update_canvas()
        
        print(f"{self.start} to {self.end}")
        
        self.canvas.remove_group('temp_line')
        self.drawing = False
        return True

    def on_touch_move(self, touch):
        if not self.drawing:
            return False
        
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
        return True

class IsoDraw(App):
    def build(self):
        root = AnchorLayout()
        layout = FloatLayout()
        root.add_widget(layout)

        # ---------------------------------------------------------------------
        # Center area - Spots widget with transparent red background
        # ---------------------------------------------------------------------
        # Background container (90% of screen width)
        center_anchor = AnchorLayout(
            size_hint=(0.9, 1),
            pos_hint={"x": 0, "y": 0}
        )
        
        # Transparent red background widget (fills the 90% area)
        red_background = ScaleWidget(
            size_hint=(1, 1),
            pos_hint={"x": 0, "y": 0}
        )
        red_background.color.rgba = (0.9, 0.9, 0.9, 0.8)  # Light gray, semi-transparent



        def red_update_callback(dx, dy, update=True):
            print(f"red callback (pan) dx={dx} dy={dy}")
            # Pan the drawing canvas
            spots_widget.origin[0] += dx
            spots_widget.origin[1] += dy
            if update:
                spots_widget.update_canvas()
            

        red_background.update_callback = red_update_callback



        # Spots widget (90% of the background area, so 5% edges show)
        spots_widget = Spots(
            size_hint=(0.9, 0.9)
        )
        

        with spots_widget.canvas.before:
            Color(1, 1, 1, 1)  # White, fully opaque
            spots_widget.rect = Rectangle(size=spots_widget.size, pos=spots_widget.pos)

        spots_widget.bind(
            pos=lambda instance, value: setattr(instance.rect, 'pos', value),
            size=lambda instance, value: setattr(instance.rect, 'size', value)
        )


        center_anchor.add_widget(red_background)
        center_anchor.add_widget(spots_widget)

        # ---------------------------------------------------------------------
        # Right widget
        # ---------------------------------------------------------------------
        right = ScaleWidget(
            size_hint=(0.1, 1),
            pos_hint={"right": 1, "y": 0}
        )
        right.name = "right"
        # Update the color to semi-transparent (or customize as needed)
        right.color.rgba = (0.9, 0.9, 0.9, 0.8)  # Light gray, semi-transparent

        def right_update_callback(dx, dy, update=True):
            old_scale = spots_widget.scale
            new_scale = max(min(2, old_scale + dy/10), 0.25)
            # Calculate the center of the widget
            center_x = spots_widget.pos[0] + spots_widget.size[0] / 2
            center_y = spots_widget.pos[1] + spots_widget.size[1] / 2
            # Adjust origin so the center stays fixed
            spots_widget.origin[0] = center_x - (center_x - spots_widget.origin[0]) * (new_scale / old_scale)
            spots_widget.origin[1] = center_y - (center_y - spots_widget.origin[1]) * (new_scale / old_scale)
            spots_widget.scale = new_scale
            print(spots_widget.scale)
            if update:
                spots_widget.update_canvas()
            

        right.update_callback = right_update_callback


        # Add widgets to layout
        layout.add_widget(center_anchor)
        layout.add_widget(right)


        return root
 
    def on_pause(self):
        print("pausing")

if __name__=="__main__":
    IsoDraw().run()
