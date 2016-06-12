from kivy.app import App
from kivy.graphics import Color, Line
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.logger import Logger
from kivy.properties import ObjectProperty, ListProperty
from kivy.clock import Clock

from thick_goban import go
from mcts import move_search


class GoFamiliarApp(App):
    def build(self):
        return GoFamiliar()


class GoFamiliar(BoxLayout):
    pass


class PlayPanel(BoxLayout):
    pass


class AnalysisPanel(BoxLayout):
    pass


class Board(FloatLayout):
    background = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class AnalysisBoard(FloatLayout):
    background = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class ButtonGrid(GridLayout):
    gamestate = ListProperty([])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for i in range(19*19):
            self.add_cell(i)
        self.state = go.Position()
        self.intersectionlist = []

    def on_gamestate(self, instance, value):

        def circle_values(stone_image):
            x_pos = stone_image.x + stone_image.width / 2
            y_pos = stone_image.y + stone_image.height / 2
            radius = 0.3 * stone_image.height

            return x_pos, y_pos, radius

        def _update_marker(instance, value):
            instance.lastmove.circle = circle_values(instance)
            instance.lastmove.width = instance.width * 0.05

        Logger.info('Board state: ' + str(value))
        for inter in self.intersectionlist:
            inter_colour = self.gamestate[inter.intersection_id]

            if inter_colour == go.BLACK:
                alpha = 1
                move_marker_colour = (1, 1, 1, 1)
                inter.stone_image.source = inter.stone_image.sourceblack
            elif inter_colour == go.WHITE:
                alpha = 1
                move_marker_colour = (0, 0, 0, 1)
                inter.stone_image.source = inter.stone_image.sourcewhite
            elif inter_colour == go.OPEN:
                alpha = 0

            inter.stone_image.color = (1, 1, 1, alpha)

            if inter.intersection_id == self.state.lastmove:
                with inter.stone_image.canvas.after:
                    Color(*move_marker_colour)
                    inter.stone_image.lastmove = Line(
                        circle=circle_values(inter.stone_image),
                        width=inter.stone_image.width * 0.05
                    )
                    inter.stone_image.bind(pos=_update_marker, size=_update_marker)
            else:
                inter.stone_image.canvas.after.clear()

    def add_cell(self, index):
        def make_move(instance):
            info_label = App.get_running_app().root.ids._play_panel.ids._move_info_label
            try:
                self.state.move(move_pt=instance.intersection_id)
            except go.MoveError as e:
                info_label.text = str(e)
            else:
                info_label.text = ''
            self.gamestate = self.state.board._board_colour

        def _update_loc(inst, value):
            '''Move a child to a new new size/pos. Used by add_cell'''
            inst.cover.size = inst.size
            inst.cover.pos = inst.pos

        intersection = Intersection(intersection_id=index)
        intersection.bind(on_press=make_move)
        self.add_widget(intersection)
        try:
            self.intersectionlist.append(intersection)
        except AttributeError:
            Clock.schedule_once(lambda dt: self.intersectionlist.append(intersection))


class AnalysisButtonGrid(GridLayout):
    gamestate = ListProperty([])
    root_node = ObjectProperty(None)
    current_node = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for i in range(19*19):
            self.add_cell(i)
        move_search_gen = move_search(state=Position(), sim_limit=500)
        self.root_node = next(move_search_gen)
        self.current_node = self.root_node
        self.state = current_node.state
        self.intersectionlist = []

    def on_gamestate(self, instance, value):

        def circle_values(stone_image):
            x_pos = stone_image.x + stone_image.width / 2
            y_pos = stone_image.y + stone_image.height / 2
            radius = 0.3 * stone_image.height

            return x_pos, y_pos, radius

        def _update_marker(instance, value):
            instance.lastmove.circle = circle_values(instance)
            instance.lastmove.width = instance.width * 0.05

        Logger.info('Board state: ' + str(value))
        for inter in self.intersectionlist:
            inter_colour = self.gamestate[inter.intersection_id]

            if inter_colour == go.BLACK:
                alpha = 1
                move_marker_colour = (1, 1, 1, 1)
                inter.stone_image.source = inter.stone_image.sourceblack
            elif inter_colour == go.WHITE:
                alpha = 1
                move_marker_colour = (0, 0, 0, 1)
                inter.stone_image.source = inter.stone_image.sourcewhite
            elif inter_colour == go.OPEN:
                alpha = 0

            inter.stone_image.color = (1, 1, 1, alpha)

            if inter.intersection_id == self.state.lastmove:
                with inter.stone_image.canvas.after:
                    Color(*move_marker_colour)
                    inter.stone_image.lastmove = Line(
                        circle=circle_values(inter.stone_image),
                        width=inter.stone_image.width * 0.05
                    )
                    inter.stone_image.bind(pos=_update_marker, size=_update_marker)
            else:
                inter.stone_image.canvas.after.clear()

    def add_cell(self, index):
        def make_move(instance):
            info_label = App.get_running_app().root.ids._play_panel.ids._move_info_label
            try:
                self.state.move(move_pt=instance.intersection_id)
            except go.MoveError as e:
                info_label.text = str(e)
            else:
                info_label.text = ''
            self.gamestate = self.state.board._board_colour

        def _update_loc(inst, value):
            '''Move a child to a new new size/pos. Used by add_cell'''
            inst.cover.size = inst.size
            inst.cover.pos = inst.pos

        intersection = Intersection(intersection_id=index)
        intersection.bind(on_press=make_move)
        self.add_widget(intersection)
        try:
            self.intersectionlist.append(intersection)
        except AttributeError:
            Clock.schedule_once(lambda dt: self.intersectionlist.append(intersection))


class Intersection(Button):
    stone_image = ObjectProperty(None)

    def __init__(self, intersection_id, **kwargs):
        super().__init__(**kwargs)
        self.intersection_id = intersection_id


class StoneImage(Image):
    pass

        
class BoardImage(Image):
    pass


if __name__ == '__main__':
    GoFamiliarApp().run()