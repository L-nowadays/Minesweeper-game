import pygame

pygame.init()
BLUE = (0, 0, 255)


class Label:
    def __init__(self, rect, text, font_size, text_color, background_color, multilines=True):
        self.rect = pygame.Rect(rect)
        self.bgcolor = background_color
        self.font_color = text_color
        self.font = pygame.font.Font(None, font_size)
        self.multilines = multilines
        self.rendered_text = None
        self.text = None
        self.change_text(text)

    def render(self, surface):
        if self.bgcolor is not None:
            surface.fill(self.bgcolor, self.rect)

        # Print text
        for x, y, text in self.rendered_text:
            surface.blit(text, (x, y))

    def change_text(self, text):
        if text:
            self.text = text
            text = ''
            self.rendered_text = []
            # Breaking text into lines if self.MULTILINE is True
            if self.multilines:
                lines = []
                line_y_sizes = []
                x_size = 0
                for i in range(len(self.text)):
                    if self.text[i].isprintable():
                        text += self.text[i]
                    x_size, y_size = self.font.size(text)
                    if x_size > self.rect.width - 10 or i == len(self.text) - 1 or self.text[i] == '\n':
                        line_y_sizes.append(y_size)
                        lines.append(text)
                        text = ''
                    if y_size > self.rect.height - 6:
                        break
                x = self.rect.centerx - self.font.size(lines[0])[0] / 2
                y0 = self.rect.centery - sum(line_y_sizes) / 2
                summ = 0
                for i in range(len(lines)):
                    y = y0 + summ
                    rendered_text = self.font.render(lines[i], 10, self.font_color)
                    self.rendered_text.append([x, y, rendered_text])
                    summ += line_y_sizes[i]
            else:
                for i in range(len(self.text)):
                    text += self.text[i]
                    x_size, y_size = self.font.size(text)
                    if x_size > self.rect.width - 5 or text == self.text:
                        rendered_text = self.font.render(text, 10, self.font_color)
                        x = self.rect.centerx - x_size / 2
                        y = self.rect.centery - y_size / 2
                        self.rendered_text.append([x, y, rendered_text])
                        break


class GUI:
    def __init__(self):
        self.pages = {}
        self.active_page = None

    def add_element(self, page, element):
        self.pages[page].append(element)

    def add_page(self, name, elements_list=[]):  # add_page('name', [button,...]) creates page with [button,...]
        self.pages[name] = elements_list.copy()

    def render(self, surface):
        if self.is_active():
            for element in self.pages[self.active_page]:
                render = getattr(element, "render", None)
                if callable(render):
                    element.render(surface)

    def update(self):
        if self.is_active():
            for element in self.pages[self.active_page]:
                update = getattr(element, "update", None)
                if callable(update):
                    element.update()

    def get_event(self, event):
        if self.is_active():
            for element in self.pages[self.active_page]:
                get_event = getattr(element, "get_event", None)
                if callable(get_event):
                    element.get_event(event)

    def open_page(self, page):
        self.active_page = page

    def close(self):
        self.active_page = None

    def is_active(self):
        return self.active_page is not None


class Button(Label):
    def __init__(self, rect, text, font_size, text_color, light_text_color, light_color=None, multilines=True,
                 action=lambda: None):
        self.rendered_light_text = []
        self.light = False
        self.light_text_color = light_text_color
        self.light_color = light_color
        self.action = action
        super().__init__(rect, text, font_size, text_color, -1, multilines)

    def change_text(self, text):
        if text:
            self.text = text
            text = ''
            self.rendered_text = []
            self.rendered_light_text = []
            # Breaking text into lines if self.MULTILINE is True
            if self.multilines:
                lines = []
                line_y_sizes = []
                for i in range(len(self.text)):
                    if self.text[i].isprintable():
                        text += self.text[i]
                    x_size, y_size = self.font.size(text)
                    if x_size > self.rect.width - 10 or i == len(self.text) - 1 or self.text[i] == '\n':
                        line_y_sizes.append(y_size)
                        lines.append(text)
                        text = ''
                    if y_size > self.rect.height - 6:
                        break
                x = self.rect.centerx - self.font.size(lines[0])[0] / 2
                y0 = self.rect.centery - sum(line_y_sizes) / 2
                summ = 0
                for i in range(len(lines)):
                    y = y0 + summ
                    rendered_text = self.font.render(lines[i], 10, self.font_color)
                    rendered_light_text = self.font.render(lines[i], 10, self.light_text_color)
                    self.rendered_text.append([x, y, rendered_text])
                    self.rendered_light_text.append([x, y, rendered_light_text])
                    summ += line_y_sizes[i]
            else:
                for i in range(len(self.text)):
                    text += self.text[i]
                    x_size, y_size = self.font.size(text)
                    if x_size > self.rect.width - 10:
                        rendered_text = self.font.render(text, 10, self.font_color)
                        rendered_light_text = self.font.render(text, 10, self.light_text_color)
                        x = self.rect.centerx - x_size / 2
                        y = self.rect.centery - y_size / 2
                        self.rendered_text.append([x, y, rendered_text])
                        self.rendered_light_text.append([x, y, rendered_light_text])
                        break

    def render(self, surface):
        # Print text
        if self.light:
            if self.light_color:
                surface.fill(self.light_color, self.rect)
            for x, y, text in self.rendered_light_text:
                surface.blit(text, (x, y))
        else:
            for x, y, text in self.rendered_text:
                surface.blit(text, (x, y))

    def get_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.light = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.light:
            self.action()


class Clock(Label):
    def __init__(self, rect, font_size, text_color, background_color, tick_event_id):
        super().__init__(rect, '00:00', font_size, text_color, background_color, multilines=False)
        self.minutes = 0
        self.seconds = 0
        self.tick_event_id = tick_event_id
        self.font = pygame.font.SysFont('Monospace', font_size, bold=True)
        self.change_text(self.text)
        pygame.time.set_timer(tick_event_id, 1000)

    # Increases time
    def tick(self):
        if self.seconds + 1 == 60:
            self.minutes += 1
            self.seconds = 0
        else:
            self.seconds += 1
        # Update time
        self.change_text(self.format_time())

    # Returns formated time
    def format_time(self):
        mins = str(self.minutes)
        secs = str(self.seconds)
        return '{}:{}'.format(mins.zfill(2), secs.zfill(2))

    # Reacts only on special tick event
    def get_event(self, event):
        if event.type == self.tick_event_id:
            self.tick()

    # Stops clock
    def stop(self):
        pygame.time.set_timer(self.tick_event_id, 0)
