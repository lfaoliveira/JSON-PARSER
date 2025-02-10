class DataManipulator:
    def __init__(self, dict_data):
        self.dict_data = dict_data
        for k, v in dict_data.items():
            setattr(self, k, v)
