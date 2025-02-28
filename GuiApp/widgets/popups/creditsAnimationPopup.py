from time import time

from kivy.uix.modalview import ModalView
from kivy.animation import AnimationTransition
from kivy.clock import Clock


class CreditsAnimationPopup(ModalView):
    def __init__(self, title: str, creditsBefore: float, creditsAfter: float, **kwargs):
        super().__init__(**kwargs)
        self.creditsBefore = creditsBefore
        self.creditsAfter = creditsAfter
        self.animationStartDelay = 1.0
        self.animationTime = 2.0
        self.postAnimationTime = 1.0
        self.timeOfStart = time() + self.animationStartDelay
        self.ids["creditsLabel"].text = f"Your credits: \n{creditsBefore:.2f}"
        self.ids["titleLabel"].text = title
        # 60 FPS update
        Clock.schedule_interval(self.updateCredits, 0.01666)

    def updateCredits(self, dt):
        timeElapsed = time() - self.timeOfStart
        if timeElapsed < 0:
            return
        if timeElapsed < self.animationTime:
            animationTimeProgress = timeElapsed / self.animationTime
            animationState = AnimationTransition.in_out_circ(animationTimeProgress)
            creditsAnimation = self.creditsBefore + (
                self.creditsAfter - self.creditsBefore
            ) * (animationState)
            self.ids["creditsLabel"].text = f"Your credits: \n{creditsAnimation:.2f}"
        else:
            self.ids["creditsLabel"].text = f"Your credits: \n{self.creditsAfter:.2f}"
            Clock.unschedule(self.updateCredits)
            Clock.schedule_once(self.dismiss, self.postAnimationTime)
