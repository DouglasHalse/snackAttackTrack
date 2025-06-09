from kivy.animation import Animation
from kivy.uix.modalview import ModalView


class WinPopup(ModalView):
    def __init__(self, won_item, size=(400, 200), **kwargs):
        super().__init__(**kwargs)
        self.ids.won_item_label.text = f"You won: \n{won_item}"
        self.appearAnimation = Animation(size=size, duration=0.2, t="out_back")
        self.appearAnimation.bind(on_complete=self.on_animation_complete)

    def open(self, *largs, **kwargs):
        super().open(*largs, **kwargs)
        self.appearAnimation.start(self)

    def on_animation_complete(self, *args):
        self.ids.particle_emitter.emit_burst(
            particle_count=800,
            colors=[
                (8 / 255, 127 / 255, 140 / 255),
                (255 / 255, 169 / 255, 194 / 255),
                (165 / 255, 231 / 255, 234 / 255),
            ],
            particle_size=self.width / 80,
        )
