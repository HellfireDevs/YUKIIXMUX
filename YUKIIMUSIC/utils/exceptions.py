import YUKIIMUSIC.yuki_guard
class AssistantErr(Exception):
    def __init__(self, errr: str):
        super().__init__(errr)
