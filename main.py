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
        self.grid = [ ]
        print(self.size)
        self.canvas.clear()
        row = 0 
        for y in range(0, self.size[1],int(self.spacex*self.py)):
            row += 1
            for x in range(0, self.size[0],self.spacex):
                self.grid.append([x+(int(self.spacex/2) if row%2==0 else 0),y])
        with self.canvas:
            Color(0.3,0.3,0.3)
            for p in self.grid:
                p = (p[0]-1, p[1]-1)
                Ellipse(pos = p, size=[2,2])
            
            Color(0,0,0,1)
            for line in self.lines:
                Color(0,0,0,1)
                Line(points=line[0]+line[1])



    def on_touch_down(self, touch):
#        print(f"down {touch}")
        if touch.is_double_tap:
            print("double tap - clearing last")
            if len(self.lines)>0: self.lines.pop()
            self.update_canvas()
            return
        self.start = self.find_nearest_point(touch.pos[0], touch.pos[1])
        self.drawing = True

    def on_touch_up(self, touch):
        # each time the user lifts the finger, finalize the line, by adding it to the list of line self.lines, when update canvas is called, all lines in self.lines are drawn

        print(f"up {touch}")
        self.end = self.find_nearest_point(touch.pos[0], touch.pos[1])
        if self.drawing and self.start != self.end:
            self.lines.append((self.start, self.end))
            print(f"number of lines {len(self.lines)}")
            self.update_canvas()
        
        print(f"{self.start} to {self.end}")
        
        self.canvas.remove_group('temp_line')
        self.drawing = False

    def on_touch_move(self, touch):
#        print(f"move {touch}")
        self.end = self.find_nearest_point(touch.pos[0], touch.pos[1])
        if self.drawing:
            self.canvas.remove_group('temp_line')
            with self.canvas:
                Color(0,0,0,1)
                with self.canvas:
                    # width = 2
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
