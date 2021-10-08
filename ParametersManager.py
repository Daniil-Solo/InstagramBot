import json


class ParametersManager:
    n_modes = 4

    def __init__(self, init_mode):
        self.mode = init_mode
        self.parameters = None

    def next_mode(self):
        self.mode = (self.mode + 1) % ParametersManager.n_modes

    def check_mode(self, number):
        return self.mode == number

    def get_text_parameters(self):
        self.parameters = dict()
        if self.mode == 0:
            return self.collect_and_like_subscribers_text()
        elif self.mode == 1:
            return self.collect_subscribers_text()
        elif self.mode == 2:
            return self.like_collected_subscribers_text()
        elif self.mode == 3:
            return self.collect_post_liked_subscribers_text()
        else:
            return "Данный метод отсутствует"

    def collect_and_like_subscribers_text(self):
        return self._get_text_with_mode('collect_and_like_subscribers')

    def collect_subscribers_text(self):
        return self._get_text_with_mode('collect_subscribers')

    def like_collected_subscribers_text(self):
        return self._get_text_with_mode('like_collected_subscribers')

    def collect_post_liked_subscribers_text(self):
        return self._get_text_with_mode('collect_post_liked_subscribers')

    def _get_text_with_mode(self, mode_name):
        try:
            with open('Source/parameters.json', 'r', encoding="UTF-8") as read_file:
                mode = json.load(read_file).get(mode_name)
        except FileNotFoundError:
            return "Файл не найден"

        text = "*****" + mode.get('head') + "*****" + "\n"
        parameters = mode.get('parameters')
        for key in parameters:
            parameter = parameters.get(key)
            text += parameter.get('text') + ": "
            text += str(parameter.get('value')) + "\n"
            self.parameters[key] = parameter.get('value')

        return text


