from dataclasses import dataclass, field
from processmapper.lane import Lane
from processmapper.painter import Painter
from processmapper.shape import Shape


@dataclass
class ProcessMap:
    _lanes: list = field(init=False, default_factory=list)

    width: int = field(init=True, default=1200)
    height: int = field(init=True, default=800)
    colour_theme: str = field(init=True, default="DEFAULT")
    __painter: Painter = field(init=False)

    lane_y_pos: int = field(init=False, default=0)
    lane_max_width: int = field(init=False, default=0)

    ### TO DO: modify the method to support pool and lane
    def add_lane(self, lane_text: str, pool_text: str = "") -> Lane:
        lane = Lane(lane_text, pool_text)
        self._lanes.append(lane)
        return lane

    def get_surface_size(self) -> tuple:
        x, y = 0, 0
        if self._lanes:
            last_y_pos = 0
            for lane in self._lanes:
                ### Calculate the x and y position of the lane and shapes in the lane
                x, y, w, h = lane.set_draw_position(x, last_y_pos, self.__painter)
                self.width = max(self.width, x + w)
                self.height = max(self.height, y + h)
                last_y_pos = y + h + Lane.VSPACE_BETWEEN_LANES

        # self.__painter.set_surface_size(self.width, self.height)
        return self.width, self.height

    def find_start_shape(self) -> Shape:
        for lane in self._lanes:
            for shape in lane.shapes:
                ### If the shape has no connection_from, it is the start shape
                print(f"{shape.text} - {len(shape.connection_from)}")
                if len(shape.connection_from) == 0:
                    print(f"Fount start shape: {shape.text}", end="")
                    return shape
        print(f"Could not find start shape")
        return None

    def get_lane_by_id(self, id: int) -> Lane:
        for lane in self._lanes:
            if lane.id == id:
                return lane
        return None

    def set_shape_x_position(self, shape: Shape, index: int = 0, x_pos: int = 0):
        lane = self.get_lane_by_id(shape.lane_id)
        if index == 0:
            shape.x = lane.get_next_x_position()
        else:
            ### If previous shape is connecting to multiple shapes,
            ### the x position of the shape is the same as the previous shape
            # shape.x = lane.get_current_x_position()
            shape.x = x_pos
        lane.width = max(lane.width, shape.x + 100)
        print(
            f", x={shape.x}, y={shape.y}, w={shape.width}, lane_max_width: {self.lane_max_width}, lane.width: {lane.width}"
        )
        self.lane_max_width = max(self.lane_max_width, lane.width)
        shape.x_pos_traversed = True

        preserved_x_pos = 0
        for index, next_shape in enumerate(shape.connection_to):
            if next_shape.x_pos_traversed is True:
                # print(f", -Skipped-")
                # print(f"")
                continue
            print(f"({index}) - <{next_shape.text}>", end="")
            lane.shape_row_count = max(lane.shape_row_count, index + 1)
            if index == 0:
                preserved_x_pos = self.set_shape_x_position(
                    next_shape, index, preserved_x_pos
                )
            else:
                self.set_shape_x_position(next_shape, index, preserved_x_pos)

        return shape.x

    def set_shape_y_position(self, shape: Shape, index: int = 0):
        lane = self.get_lane_by_id(shape.lane_id)
        if index == 0:
            ### If previous shape is connecting to one shape,
            ### the y position of the shape is the same as the previous shape
            shape.y = lane.get_current_y_position()
        else:
            ### Otherwise, the y position of the shape is the next y position
            shape.y = lane.get_next_y_position()

        shape.set_draw_position(self.__painter)
        print(f"<{shape.text}>, x={shape.x}, y={shape.y}")

        shape.y_pos_traversed = True

        # for shape in lane.shapes:
        for index, next_shape in enumerate(shape.connection_to):
            if next_shape.y_pos_traversed is True:
                # print(f", -Skipped-")
                # print(f"")
                continue
            print(f"    <{shape.text}>, next_shape: {next_shape.text}, index: {index}")
            # print(f"({index}) - <{next_shape.text}>", end="")
            self.set_shape_y_position(next_shape, index)

    def set_draw_position(self, painter: Painter) -> tuple:
        start_shape = self.find_start_shape()
        print(f"Setting x position...")
        self.set_shape_x_position(start_shape, 0, 0)

        x, y = (
            0,
            0,
        )
        for lane in self._lanes:
            lane.painter = painter
            lane.x = x if x > 0 else lane.SURFACE_LEFT_MARGIN
            lane.y = y if y > 0 else lane.SURFACE_TOP_MARGIN
            lane.width = self.lane_max_width
            lane.height = (
                (lane.shape_row_count * 60)
                + ((lane.shape_row_count - 1) * lane.VSPACE_BETWEEN_SHAPES)
                + lane.LANE_SHAPE_TOP_MARGIN
                + lane.LANE_SHAPE_BOTTOM_MARGIN
            )
            # print(
            #     f"{lane.height} = ({lane.shape_row_count} * 60) + {lane.LANE_SHAPE_TOP_MARGIN} + {lane.LANE_SHAPE_BOTTOM_MARGIN}"
            # )
            y = lane.y + lane.height + lane.VSPACE_BETWEEN_LANES
            # print(f"{x} = {lane.y} + {lane.height} + {lane.VSPACE_BETWEEN_LANES}")

        print(f"Setting y position...")
        self.set_shape_y_position(start_shape)

        x, y = 0, 0
        for lane in self._lanes:
            print(
                f"[{lane.text}], row count: {lane.shape_row_count}, x={lane.x}, y={lane.y}, mw={self.lane_max_width}, w={self.width}, h={lane.height}"
            )
            for shape in lane.shapes:
                print(f"    <{shape.text}>: x={shape.x}, y={shape.y}")

    def draw(self) -> None:
        self.__painter = Painter(self.width, self.height)

        self.__set_colour_palette(self.colour_theme)

        ### Determine the size of the process map
        # self.width, self.height = self.get_surface_size()

        print(f"Set draw position...")
        self.set_draw_position(self.__painter)

        print(f"Start drawing...")
        if self._lanes:
            ### Draw the lanes first
            for lane in self._lanes:
                lane.draw()

            ### Then draw the shapes in the lanes
            for lane in self._lanes:
                lane.draw_shape()

            ### Finally draw the connections between the shapes
            for lane in self._lanes:
                lane.draw_connection()

    def __set_colour_palette(self, palette: str) -> None:
        """This method sets the colour palette"""
        # self.__painter.set_colour_palette(palette)

    def save(self, filename: str) -> None:
        self.__painter.save_surface(filename)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        pass

    def print(self) -> None:
        for lane in self._lanes:
            print(f"[{lane.text}, number of elements: {len(lane.shapes)}]")
            for shape in lane.shapes:
                print(f'    ("{shape.text}", type: {shape.__class__.__name__})')
                for connection in shape.connection_to:
                    print(f"        ->: {connection.text}")
                for connection in shape.connection_from:
                    print(f"        <-: {connection.text}")
