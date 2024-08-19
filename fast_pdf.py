import random

from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Resampling
import math
import re
import warnings


class MyImageModifier:

    color_dict = {'r': (229, 0, 0), 'g': (21, 176, 26), 'b': (3, 67, 223)}
    default_background_color = (255, 255, 255, 255)
    default_font = 'arial.ttf'

    def __init__(self, font='arial.ttf', fontsize=30):
        self.font_name = font
        self.fontsize = fontsize
        pass

    @staticmethod
    def text_to_image(text: str, color: tuple, font='arial.ttf', fontsize=30,
                      bg_color=(255, 255, 255, 255)) -> Image.Image:
        img_font = ImageFont.truetype(font, size=fontsize)
        left, top, width, height = img_font.getbbox(text)
        tmp_image = Image.new("RGBA", (width, height), bg_color)
        drawer = ImageDraw.Draw(tmp_image)
        drawer.text((0, 0), text, font=img_font, fill=color)
        return tmp_image

    @staticmethod
    def add_text_to_image(text: str, img: Image.Image,
                          position: int = 7, gap: int = 5, font='arial.ttf', fontsize=30,
                          bg_color=(255, 255, 255, 255)) -> Image.Image:
        if text is None:
            return img
        parsed_text_list = MyImageModifier.text_color_parser(text)
        first_segment_text, first_segment_color = parsed_text_list.pop(0)
        full_text_image = MyImageModifier.text_to_image(first_segment_text, first_segment_color,
                                                        font, fontsize, bg_color)
        for segment_text, segment_color in parsed_text_list:
            full_text_image = MyImageModifier.append(MyImageModifier.text_to_image(segment_text, segment_color,
                                                                                   font, fontsize, bg_color),
                                                     full_text_image, position=5)
        return MyImageModifier.append(full_text_image, img, position, gap)

    @staticmethod
    def _color_format_converter(hex_format: str) -> (int, int, int):
        r = hex_format[1:3]
        g = hex_format[3:5]
        b = hex_format[5:7]
        return int(r, 16), int(g, 16), int(b, 16)

    @staticmethod
    def text_color_parser(text: str, default_color: (int, int, int) = (0, 0, 0)) -> [(str, (int, int, int)), ]:
        output_segment_list = []

        color_begin_regex = re.compile("<.?>")
        color_end_regex = re.compile("</.?>")
        color_begin_idx = color_begin_regex.finditer(text)
        color_end_idx = color_end_regex.finditer(text)
        color_begin_idx_list = [i.span() for i in color_begin_idx]
        color_end_idx_list = [i.span() for i in color_end_idx]

        if len(color_begin_idx_list) != len(color_end_idx_list):
            raise Exception(f'\"{text}\" has unequal pair of begin and end symbols')

        if len(color_begin_idx_list) == 0:
            return [(text, default_color)]

        for i, bg_idx_tuple in enumerate(color_begin_idx_list):
            now_color = MyImageModifier.color_dict[text[bg_idx_tuple[0] + 1]]
            if i == 0:
                output_segment_list.append((text[0:bg_idx_tuple[0]], default_color))
                output_segment_list.append((text[bg_idx_tuple[1]:color_end_idx_list[i][0]], now_color))
            else:
                output_segment_list.append((text[color_end_idx_list[i - 1][1]:bg_idx_tuple[0]], default_color))
                output_segment_list.append((text[bg_idx_tuple[1]:color_end_idx_list[i][0]], now_color))

        output_segment_list.append((text[color_end_idx_list[-1][1]:], default_color))
        return output_segment_list

    @staticmethod
    def append(imgA: Image.Image, imgB: Image.Image, position: int = 7, gap: int = 0) -> Image.Image:
        """
        Append imgA to imgB.
        :param imgA: The image to be appended
        :param imgB: Obviously
        :param position: int, 0-8, imgA's relative position to imgB
            0 |     1     | 2
            ------------------
            3 | 4 (imgB)  | 5
            ------------------
            6 |     7     | 8
        :param gap: int, the gap between imgA and imgB (pixels)
        :return: Image after appending
        """
        abs_cor = (position % 3, position // 3)
        vector = (abs_cor[0] - 1, abs_cor[1] - 1)  # Vector from center to target
        new_frame = (abs(vector[0]) + 1, abs(vector[1]) + 1)  # Frame for new img
        imgB_frame_cor = tuple(map(lambda x: abs(min(0, x)), vector))  # New frame coordinate for origin img
        imgA_frame_cor = (imgB_frame_cor[0] + vector[0], imgB_frame_cor[1] + vector[1])
        tmp_Frame = Frame(gap=gap, frame=new_frame)
        tmp_Frame.add_element(imgB, position=imgB_frame_cor)  # Image B goes first and under.
        tmp_Frame.add_element(imgA, position=imgA_frame_cor)
        return tmp_Frame.render()

    @staticmethod
    def box_smaller(box1, box2) -> bool:
        if box1[0] <= box2[0] and box1[1] <= box2[1]:
            return True
        else:
            return False

    @staticmethod
    def box2fontsize(target_box: (int, int), text: str, font: str) -> int:
        tmp_font = ImageFont.truetype(font=font, size=9)
        last_fontsize = 9
        now_fontsize = 10
        l, t, w, h = tmp_font.getbbox(text)
        last_box = (w, h)
        step = 1

        while True:
            tmp_font = ImageFont.truetype(font=font, size=now_fontsize)
            l, t, width, height = tmp_font.getbbox(text)
            now_box = (width, height)
            # print(f"{now_box} | {last_box} | {now_fontsize} | {step} | {target_box}")
            if MyImageModifier.box_smaller(now_box,target_box) ^ MyImageModifier.box_smaller(last_box,target_box):
                if abs(step) <= 2:
                    if MyImageModifier.box_smaller(now_box,target_box):
                        return now_fontsize
                    else:
                        return last_fontsize

            if MyImageModifier.box_smaller(now_box,target_box):
                step = abs(step*2)
            else:
                step = -math.ceil(abs(now_fontsize - last_fontsize)/2)

            last_fontsize = now_fontsize
            last_box = now_box

            now_fontsize += step


class ImagePlaceHolder:
    def __init__(self, size: (int,int)):
        self.size = size

    def render(self) -> Image.Image:
        return Image.new('RGBA', size=self.size, color=(255,255,255,0))


class Frame(object):
    def __init__(self, gap: int, frame: (int, int) = (2, 2)):
        """
        :param gap: int, the gap between each element in the frame (in pixels)
        :param frame: tuple(int, int), the size of the frame (columns, rows)
        """
        self.gap = gap
        self.default_gap = gap
        self.horizontal_gap = gap
        self.vertical_gap = gap
        self.frame = frame
        self.__element_list = []
        self.max_height_in_rows = {i: 0 for i in range(frame[1])}
        self.max_width_in_columns = {i: 0 for i in range(frame[0])}
        self.max_element_id = 0

        self.parent_id = 0
        self.id = 0

        self.bg_color = (255, 255, 255, 0)

        self.if_compact = False

    def add_element(self, element, position: (int, int), alignment: int = 4) -> None:
        """
        Add an element to the frame.
        :param element: Image.Image or Frame.
        :param position: tuple(int, int), The position of the element in this frame.
        :param alignment: int, from 0 to 8, alignment way of the element in its block. See Frame.print_position_table()
        :return: None
        """
        if position[0] >= self.frame[0] or position[1] >= self.frame[1]:
            raise ValueError(f"Out of frame: ({position[0]+1},{position[1]+1}) out of {self.frame}")
        #if not (isinstance(element, Image.Image) or isinstance(element, Frame)):
        #    raise TypeError(f"{type(element)} is not an Image.Image or Frame")

        if isinstance(element, Frame) or isinstance(element, Plot):
            element.parent_id = f"{self.parent_id}-{self.id}"
            element.id = self.max_element_id
        self.max_element_id += 1

        self.__element_list.append((element, position, alignment))

    def _get_coordinate(self, position: (int, int), size: (int, int), alignment: int = 4,
                        horizontal_gap: int = None, vertical_gap: int = None) -> (int, int):
        """
        Returns the coordinates of the specified position on the image
        :param position: tuple(int, int), the position of the element in the Frame.
        :param size: tuple(width: int, height: int), size of the element. (in pixels)
        :param alignment: int, from 0 to 8. The alignment of img in its own block.
        :return: the coordinates of the element should be paste into the FINAL Image
        """
        now_x = 0
        now_y = 0
        if horizontal_gap is None:
            horizontal_gap = self.horizontal_gap
        if vertical_gap is None:
            vertical_gap = self.vertical_gap
        if self.if_compact:
            horizontal_gap = min(horizontal_gap, self.gap)
            vertical_gap = min(vertical_gap, self.gap)

        for i in range(position[0]):
            now_x += self.max_width_in_columns[i] + horizontal_gap
        for i in range(position[1]):
            now_y += self.max_height_in_rows[i] + vertical_gap
        half_of_block_width = (self.max_width_in_columns[position[0]] - size[0]) / 2
        half_of_block_height = (self.max_height_in_rows[position[1]] - size[1]) / 2

        paste_coordinate = (int(now_x + half_of_block_width * (alignment % 3)),
                            int(now_y + half_of_block_height * (alignment // 3))
                            )
        return paste_coordinate

    def _update_size(self):
        self.max_height_in_rows = {i: 0 for i in range(self.frame[1])}
        self.max_width_in_columns = {i: 0 for i in range(self.frame[0])}
        for (element, position, alignment) in self.__element_list:
            if isinstance(element, Image.Image):
                size = element.size
            else:
                size = element.get_size()
            self.max_width_in_columns[position[0]] = max(self.max_width_in_columns[position[0]],size[0])
            self.max_height_in_rows[position[1]] = max(self.max_height_in_rows[position[1]], size[1])

    def get_size(self) -> (int, int):
        """
        Returns the size of the Frame.
        :return: tuple(width: int, height: int), the size of the Frame (in pixels). (width, height)
        """
        width = 0 - self.horizontal_gap
        height = 0 - self.vertical_gap
        self._update_size()

        for i in self.max_width_in_columns:
            width += self.max_width_in_columns[i] + self.horizontal_gap
        for i in self.max_height_in_rows:
            height += self.max_height_in_rows[i] + self.vertical_gap

        return width, height

    def __print_debug_data(self):
        print(f'{self.parent_id}-{self.id}: | {type(self)} | {self.gap} | {self.horizontal_gap} | {self.vertical_gap}')

    def render(self) -> Image.Image:
        """
        Renders the Frame after rendering the image.
        :return: Image.Image, the image after rendering all elements of the Frame.
        """
        if len(self.__element_list) == 0:
            warnings.warn(f"No element in the Frame's list. Please add an element first. Frame: {self.parent_id}-{self.id}")
            return Image.new('RGBA', (1, 1), color=self.bg_color)
        new_image_size = self.get_size()
        new_image = Image.new('RGBA', new_image_size, self.bg_color)
        for (element, position, alignment) in self.__element_list:
            if isinstance(element, Image.Image):
                tmp_segment_img = element
            else:
                tmp_segment_img = element.render()

            # self.__print_debug_data()
            paste_cor = self._get_coordinate(position, tmp_segment_img.size, alignment)

            try:
                r, g, b, a = tmp_segment_img.split()
                new_image.paste(tmp_segment_img, paste_cor, mask=a)
            except ValueError:
                new_image.paste(tmp_segment_img, paste_cor)
        return new_image

    def _arrange_gap(self, target_size: (int, int)):
        rows_number = self.frame[1]
        columns_number = self.frame[0]
        if columns_number != 1 and rows_number != 1:
            self._update_size()
            width_of_elements = sum(self.max_width_in_columns.values())
            height_of_elements = sum(self.max_height_in_rows.values())
            # print(target_size, width_of_elements, height_of_elements)
            #print(f"widths: {self.max_width_in_columns} heights: {self.max_height_in_rows}")
            # Just modify the gap to fit the target size
            self.horizontal_gap = int((target_size[0] - width_of_elements) / (columns_number - 1))
            self.vertical_gap = int((target_size[1] - height_of_elements) / (rows_number - 1))
        else:
            if columns_number == 1:
                self.horizontal_gap = 0
            if rows_number == 1:
                self.vertical_gap = 0

        # print(f"After arrange{self.horizontal_gap, self.vertical_gap}")

    def resize(self, size: (int, int), min_horizontal_gap: int = None, min_vertical_gap: int = None) -> (int, int):
        target_size = size
        columns_number, rows_number = self.frame
        if min_horizontal_gap is None:
            min_horizontal_gap = self.horizontal_gap
        if min_vertical_gap is None:
            min_vertical_gap = self.vertical_gap
        minium_width = min_horizontal_gap*(columns_number-1)
        minium_height = min_vertical_gap*(rows_number-1)
        minium_size = (minium_width, minium_height)  # keep gap between elements
        if MyImageModifier.box_smaller(size, minium_size):
            raise ValueError(f"The target box {target_size} is smaller than the minium box {minium_size}.")

        now_size = self.get_size()
        if MyImageModifier.box_smaller(now_size, target_size):
            # print(f"The target box {target_size} is bigger than now box {now_size}.")
            self._arrange_gap(target_size)
            return self.get_size()

        target_width, target_height = target_size
        target_width -= min_horizontal_gap * (columns_number - 1)
        target_height -= min_vertical_gap * (rows_number - 1)
        single_box_width = int(target_width / columns_number)
        single_box_height = int(target_height / rows_number)
        single_box_size = (single_box_width, single_box_height)

        for i, (element, position, alignment) in enumerate(self.__element_list):
            if isinstance(element, Image.Image):
                if MyImageModifier.box_smaller(element.size, single_box_size):
                    continue
                tmp_ratio = element.size[1] / element.size[0]
                if single_box_width * tmp_ratio >= single_box_height:
                    element_new_size = (int(single_box_height / tmp_ratio), int(single_box_height))
                else:
                    element_new_size = (int(single_box_width), int(single_box_width * tmp_ratio))
                element = element.resize(element_new_size, resample=Resampling.LANCZOS)
                self.__element_list[i] = (element, position, alignment)
            else:
                element.resize((single_box_width, single_box_height))
                #print(f"element: {element}, position: {position}, size: {element.get_size()}")
        self._update_size()
        self._arrange_gap(target_size)

    @staticmethod
    def print_position_table() -> None:
        print('''
        position_table:
            0 | 1 | 2
            ---------
            3 | 4 | 5
            ---------
            6 | 7 | 8
        ''')

    def visualize_relation_tree(self) -> None:
        """
        TODO: Visualize the relationship in image. Each block colors different and with its Node_id on it.
        :return:
        """
        image_numbers = 0
        frame_numbers = 0
        for element, position, alignment in self.__element_list:
            if isinstance(element, Image.Image):
                image_numbers += 1
            else:
                frame_numbers += 1
                element.visualize_relation_tree()
        print(f"Node: {self.parent_id}-{self.id} | {frame_numbers} Frames | {image_numbers} Images")


class _ArgsDictParser:

    default_page_args = {'horizontal_margin': 64, 'vertical_margin': 55, 'default_gap': 0, 'bg_color': (255, 255, 255, 255)}
    default_font_args = {'name': 'arial.ttf', 'fontsize': 90, 'color': (0, 0, 0, 255)}  # Black

    def __init__(self):
        pass

    @staticmethod
    def return_font_args(font_args_dict: dict) -> tuple:
        try:
            color = font_args_dict['color']
            font = font_args_dict['name']
            fontsize = font_args_dict['fontsize']
        except KeyError:
            raise KeyError(f'Invalid font argument dict input: {font_args_dict}\n'
                           f'Should contain the following keys: {_ArgsDictParser.default_font_args.keys()}')
        return font, fontsize, color

    @staticmethod
    def return_page_args(page_args_dict: dict) -> tuple:
        try:
            page_horizontal_margin = page_args_dict['horizontal_margin']
            page_vertical_margin = page_args_dict['vertical_margin']
            default_gap = page_args_dict['default_gap']
            bg_color = page_args_dict['bg_color']
        except KeyError:
            raise ValueError(f'Invalid page argument dict input: {page_args_dict}\n'
                             f'Should contain the following keys: {_ArgsDictParser.default_page_args.keys()}')
        return page_horizontal_margin, page_vertical_margin, default_gap, bg_color


class Plot(Frame):

    default_page_args = {'horizontal_margin': 64, 'vertical_margin': 55, 'default_gap': 0, 'bg_color': (255, 255, 255, 255)}

    default_title_font_args = {'name': 'arial.ttf', 'fontsize': 60, 'color': (0, 0, 0, 255)}  # Black
    default_description_font_args = {'name': 'arial.ttf', 'fontsize': 30, 'color': (0, 0, 0, 255)}  # Black

    def __init__(self, im: Image.Image = None, title: str = None, description: str = None):
        super().__init__(gap=0, frame=(1, 1))
        self.__im = im
        self.__title = title
        self.__description = description

        self.add_element(self.__im, position=(0,0), alignment=4)

        self.title_font_args = self.default_title_font_args
        self.description_font_args = self.default_description_font_args
        self.font_bg_color = (255, 255, 255, 255)  # White

        width = self.__im.size[0]
        self.max_width_in_rows = [width]
        self.title_box = (width, 16)
        self.description_box = (width, 16)
        # print(self.title_box, self.description_box)

    @classmethod
    def generate_plot(cls, im: Image.Image, title: str = None, description: str = None, **kwargs):
        """
        Generates a plot. DO NOT USE __init__ to generate a plot.
        :param im: the image of the plot
        :param title: the title of the plot
        :param description: the description of the plot
        :param kwargs: description_font_args: the font arguments for the description,
        title_font_args: the font arguments for the title

        :return: Plot
        """
        tmp = cls(im=im, title=title, description=description)
        if 'title_font_args' in kwargs:
            tmp.title_font_args = kwargs['title_font_args']
        if 'description_font_args' in kwargs:
            tmp.description_font_args = kwargs['description_font_args']
        tmp.__fill_title()
        return tmp

    def __fill_title(self):
        title_font, title_fontsize, title_color = _ArgsDictParser.return_font_args(self.title_font_args)
        description_font, description_fontsize, description_color = _ArgsDictParser.return_font_args(self.description_font_args)
        tmp_title_font = ImageFont.truetype(title_font, title_fontsize)
        tmp_description_font = ImageFont.truetype(description_font, description_fontsize)
        l, u, w, self.title_height = tmp_title_font.getbbox("Title")
        l, u, w, self.description_height = tmp_description_font.getbbox("Description")
        width = self.__im.size[0]
        self.title_box = (width, self.title_height)
        self.description_box = (width, self.description_height)
        self.vertical_gap = int(self.title_height * 0.3)

    def __text_render(self, img: Image.Image, text: str, font_args_dict: dict, textbox: (int, int)) -> Image.Image:
        color_parsed_list = MyImageModifier.text_color_parser(text)
        fontname, fontsize, color = _ArgsDictParser.return_font_args(font_args_dict)
        plain_text = ''.join([i[0] for i in color_parsed_list])
        fit_fontsize = MyImageModifier.box2fontsize(textbox, text=plain_text, font=fontname)
        if fit_fontsize > fontsize:
            fit_fontsize = fontsize
        new_image = MyImageModifier.add_text_to_image(text, img, gap=self.vertical_gap,font=fontname,
                                                      fontsize=fit_fontsize, bg_color=self.font_bg_color)
        return new_image

    def render(self) -> Image.Image:
        render_img = self.__im
        if self.__title is not None:
            render_img = self.__text_render(render_img, self.__title, self.title_font_args, self.title_box)
        if self.__description is not None:
            render_img = self.__text_render(render_img, self.__description, self.description_font_args, self.description_box)
        return render_img

    def get_size(self) -> (int, int):
        width = self.__im.size[0]
        height = self.__im.size[1]+self.title_height+self.description_height+self.vertical_gap*3
        self.max_height_in_rows = [max(self.__im.size[1], self.title_height, self.description_height)]
        self.max_width_in_rows = [self.__im.size[0]]
        #  One more
        return width, height

    def resize(self, size: (int, int), min_horizontal_gap: int = 0, min_vertical_gap: int = 5, *args) -> None:
        target_width, target_height = size
        __im_width, __im_height = self.__im.size
        __im_ratio = __im_height / __im_width
        if target_width < __im_width:
            self.__im = self.__im.resize((target_width, int(target_width*__im_ratio)), Resampling.LANCZOS)
            self.title_box = (self.__im.size[0], self.title_height)
            self.description_box = (self.__im.size[0], self.description_height)

        minium_height_of_text_boxes = self.title_height+self.description_height+self.vertical_gap*3
        now_height = self.get_size()[1]
        if target_height < now_height:
            __im_2nd_height = target_height - minium_height_of_text_boxes
            self.__im = self.__im.resize((int(__im_2nd_height/__im_ratio), __im_2nd_height), Resampling.LANCZOS)
            self.title_box = (self.__im.size[0], self.title_height)
            self.description_box = (self.__im.size[0], self.description_height)


class Page(Frame):

    default_page_args = {'horizontal_margin': 140, 'vertical_margin': 100, 'default_gap': 10, 'bg_color': (255, 255, 255)}

    default_title_font = {'name': 'arial.ttf', 'fontsize': 120, 'color': (0, 0, 0, 255)}  # Black
    default_description_font = {'name': 'arial.ttf', 'fontsize': 100, 'color': (0, 0, 0, 255)}  # Black
    default_page_number_font = {'name': 'arial.ttf', 'fontsize': 50, 'color': (0, 0, 0, 255)}  # Black

    default_page_size_list = [(2480, 3508),  # A4 300 dpi
                              (3307, 4677),  # A4 400 dpi
                              (4134, 5846)]  # A4 500 dpi

    def __init__(self):
        super().__init__(gap=10, frame=(3, 3))

        self.page_horizontal_margin = Page.default_page_args['horizontal_margin']
        self.page_vertical_margin = Page.default_page_args['vertical_margin']
        self.bg_color = (255, 255, 255)  # White

        self.title_font_args = self.default_title_font
        self.description_font_args = self.default_description_font
        self.page_number_font_args = self.default_page_number_font

        self.title = None
        self.description = None
        self.title_frame = Frame(gap=self.default_gap, frame=(1, 3))
        # Title frame initialize here.

        self.main_frame = Frame(gap=self.default_gap, frame=(1, 2))
        self.main_frame.add_element(self.title_frame, position=(0,1), alignment=3)
        self.add_element(self.main_frame, position=(1, 1))
        # Main frame initialize here.

        self.specify_page_size = True
        self.page_size = Page.default_page_size_list[0]
        # Default using A4 300dpi as page size.

        self.vertical_gap = 0
        self.horizontal_gap = 0

        self.title_alignment = 3
        self.description_alignment = 3

    def __fill_margins(self):
        margin_placeholder = ImagePlaceHolder(size=(self.page_horizontal_margin, self.page_vertical_margin))
        self.add_element(margin_placeholder.render(), position=(0, 0))
        self.add_element(margin_placeholder.render(), position=(2, 2))
        # Add margin to page edges

    def __fill_titles(self):
        if self.title is not None:
            title_font, title_font_size, title_color= _ArgsDictParser.return_font_args(self.title_font_args)
            self.title_frame.add_element(MyImageModifier.text_to_image(self.title,
                                                                       color=title_color, font=title_font,
                                                                       fontsize=title_font_size), position=(0, 1),
                                         alignment=self.title_alignment)
        if self.description is not None:
            description_font, description_font_size,description_color = _ArgsDictParser.return_font_args(self.description_font_args)
            self.title_frame.add_element(MyImageModifier.text_to_image(self.description,
                                                                       color=description_color, font=description_font,
                                                                       fontsize=description_font_size), position=(0, 2),
                                         alignment=self.description_alignment)
        # Add title to title frame if there has title.

        self.title_frame.add_element(ImagePlaceHolder(size=(self.page_size[0]-2*self.page_horizontal_margin, 1)).render(),
                                     position=(0,0))
        # Add a placeholder (width, 1px)to make alignment settings run properly

    def set_page_font_args(self, name:str, font_args_dict: dict):
        if name == 'title_font':
            self.title_font_args = font_args_dict
        elif name == 'description_font':
            self.description_font_args = font_args_dict
        elif name == 'page_number_font':
            self.page_number_font_args = font_args_dict
        else:
            raise ValueError('No such type of font in class page.')

    def set_page_bg_args(self, page_args_dict: dict):
        (self.page_horizontal_margin, self.page_vertical_margin,
         self.default_gap, self.bg_color) = _ArgsDictParser.return_page_args(page_args_dict)
        self.__fill_margins()

    def set_page_size(self, page_size: (int, int) = None):
        if page_size is not None:
            self.page_size = page_size
            self.specify_page_size = True
        else:
            self.specify_page_size = False

    @classmethod
    def generate_page(cls, main_frame: Frame, title: str = None, description: str = None):
        tmp_page = cls()
        tmp_page.main_frame.add_element(main_frame, position=(0, 0))
        tmp_page.title = title
        tmp_page.description = description
        return tmp_page

    def __arrange_main_frame(self):
        if self.specify_page_size:
            page_width, page_height = self.page_size
            main_frame_avail_width = page_width - 2*self.page_horizontal_margin
            main_frame_avail_height = page_height - 2*self.page_vertical_margin
            # print(f"main_frame_avail_height {main_frame_avail_height}")
            main_frame_avail_size = (main_frame_avail_width,
                                     2*(main_frame_avail_height-self.title_frame.get_size()[1])-self.main_frame.vertical_gap)
        else:
            main_frame_avail_size = self.main_frame.get_size()
        # print(f"main_frame_avail_size {main_frame_avail_size}")
        self.main_frame.resize(main_frame_avail_size,
                               min_vertical_gap=self.default_gap, min_horizontal_gap=self.default_gap)
        # print(f"gaps {self.main_frame.vertical_gap, self.main_frame.horizontal_gap}")

    def render(self, page_number: int = 1) -> Image.Image:
        self.__fill_margins()
        self.__fill_titles()
        self.__arrange_main_frame()
        render_page_size = self.get_size()
        # print(f"blank_page_size {blank_page_size}")
        if len(self.bg_color) > 3:
            render_page = Image.new("RGBA", render_page_size, color=self.bg_color)
        else:
            render_page = Image.new("RGB", render_page_size, color=self.bg_color)
        render_page.paste(self.main_frame.render(),
                          self._get_coordinate((1,1), self.main_frame.get_size()))
        # Create a blank page

        page_number_fontname, page_number_fontsize, page_number_color = _ArgsDictParser.return_font_args(self.page_number_font_args)
        page_number_font = ImageFont.truetype(page_number_fontname, page_number_fontsize)
        l, u, page_number_width, page_number_height = page_number_font.getbbox(str(page_number))
        page_number_cor = ((render_page_size[0]-page_number_width)/2,
                           render_page_size[1]-(self.page_vertical_margin+page_number_height)/2)
        draw = ImageDraw.Draw(render_page)
        draw.text(xy=page_number_cor, text=str(page_number), fill=page_number_color, font=page_number_font)
        # Print page number on page.

        return render_page


class PDFFormatSaver:

    font_args_list = ['name', 'fontsize', 'color']
    page_args_list = ['horizontal_margin', 'vertical_margin', 'default_gap', 'bg_color']

    def __init__(self):
        self.plot_title_font_args = None
        self.plot_description_font_args = None
        self.page_number_font_args = None
        self.page_title_font_args = None
        self.page_description_font_args = None

        self.page_args = None
        self.page_size = None

        self.page_title_alignment = 3
        self.page_description_alignment = 3

    @classmethod
    def get_default_format(cls, fontname):
        tmp_format = cls()
        tmp_format.plot_title_font_args = {'name': fontname, 'fontsize': 100, 'color': (0, 0, 0, 255)}
        tmp_format.plot_description_font_args = {'name': fontname, 'fontsize': 80, 'color': (0, 0, 0, 255)}
        tmp_format.page_number_font_args = {'name': fontname, 'fontsize': 70, 'color': (0, 0, 0, 255)}
        tmp_format.page_title_font_args = {'name': fontname, 'fontsize': 120, 'color': (0, 0, 0, 255)}
        tmp_format.page_description_font_args = {'name': fontname, 'fontsize': 100, 'color': (0, 0, 0, 255)}

        tmp_format.page_args = {'horizontal_margin': 140, 'vertical_margin': 100, 'default_gap': 10, 'bg_color': (255, 255, 255)}
        tmp_format.page_size = Page.default_page_size_list[0]

        return tmp_format

    def set_target_type_font(self, typename: str, font_args: dict):
        if hasattr(self, typename):
            if PDFFormatSaver.font_args_list.sort() == list(font_args.keys()).sort():
                setattr(self, typename, font_args)
            else:
                raise KeyError(f"Arguments incomplete in: {font_args}\n"
                               f"Should be {PDFFormatSaver.font_args_list}")
        else:
            raise Exception(f'No such type of font in PDFFormatSaver: {typename}')

    def set_page_args(self, page_args: dict):
        if PDFFormatSaver.page_args_list.sort() == list(page_args.keys()).sort():
            self.page_args = page_args
        else:
            raise KeyError(f"Arguments incomplete in: {page_args}\n"
                           f"Should be {PDFFormatSaver.page_args_list}")


class PDFGenerator:
    def __init__(self):
        self._pages_dict = {}
        self._pdf_format = PDFFormatSaver.get_default_format('arial.ttf')

        self.pages_number = 0

    def add_page(self, page: Page):
        self.pages_number += 1
        self._pages_dict[self.pages_number] = page

    def fast_build_page(self, element_list, title: str = None, description: str = None,
                        specify_format: PDFFormatSaver = None) -> Page:
        """
        :param element_list: a list of tuples, list[(Image.Image or path_to_image, title, description), ...]
        :param title: the title of the page
        :param description: the description of the page
        :param specify_format: the format of the page. Type: PDFFormatSaver
        :return: Page
        """
        if specify_format is None:
            specify_format = self._pdf_format
        element_number = len(element_list)

        layout_frame = (1, 1)
        for i in range(1, math.ceil(element_number ** 0.5)+1):
            j = element_number // i
            if element_number % i == 0:
                size = (i, j)
            else:
                size = (i, j+1)
            if size[0]+1 == size[1] or size[0] == size[1]:
                layout_frame = size

        tmp_main_frame = Frame(gap=specify_format.page_args['default_gap'],frame=layout_frame)
        if element_number < 5:
            tmp_main_frame.if_compact = True

        for i, package in enumerate(element_list):
            im, ti, desc = package
            if isinstance(im, str):
                im = Image.open(im)
            elif isinstance(im, Image.Image):
                pass
            else:
                raise TypeError('Image must be PIL.Image or str')
            tmp_plot = Plot.generate_plot(im=im, title=ti, description=desc,
                                          description_font_args=specify_format.plot_description_font_args,
                                          title_font_args=specify_format.plot_title_font_args)
            tmp_position = (i % layout_frame[0], i // layout_frame[0])
            # print(layout_frame, i,tmp_position)
            tmp_main_frame.add_element(tmp_plot, position=tmp_position, alignment=1)
        tmp_page = Page.generate_page(tmp_main_frame, title, description)

        tmp_page.title_alignment = specify_format.page_title_alignment
        tmp_page.description_alignment = specify_format.page_description_alignment

        tmp_page.set_page_bg_args(specify_format.page_args)

        tmp_page.set_page_font_args('title_font',specify_format.page_title_font_args)
        tmp_page.set_page_font_args('description_font', specify_format.page_description_font_args)
        tmp_page.set_page_font_args('page_number_font', specify_format.page_number_font_args)

        tmp_page.set_page_size(specify_format.page_size)

        return tmp_page

    def generate_pdf(self, filename: str):
        pdf_img_list = []
        for page_number in self._pages_dict.keys():
            pdf_img_list.append(self._pages_dict[page_number].render(page_number))
        first_page = pdf_img_list.pop(0)
        first_page.save(filename, format='pdf', save_all=True, append_images=pdf_img_list)

    @classmethod
    def setup_from_FormatSaver(cls, format_saver: PDFFormatSaver):
        tmp_pdf_generator = cls()
        tmp_pdf_generator._pdf_format = format_saver
        return tmp_pdf_generator


if __name__ == '__main__':
    pass
