from time import time

from kivy.uix.modalview import ModalView
from kivy.animation import AnimationTransition
from kivy.clock import Clock


class PurchaseCompletedPopup(ModalView):
    def __init__(
        self, creditsBeforePurchase: float, creditsAfterPurchase: float, **kwargs
    ):
        super().__init__(**kwargs)
        self.creditsBeforePurchase = creditsBeforePurchase
        self.creditsAfterPurchase = creditsAfterPurchase
        self.animationStartDelay = 1.0
        self.animationTime = 2.0
        self.postAnimationTime = 2.0
        self.timeOfStart = time() + self.animationStartDelay
        self.ids["creditsLabel"].text = f"Your credits: \n{creditsBeforePurchase:.2f}"
        # 60 FPS update
        Clock.schedule_interval(self.updateCredits, 0.01666)

    def updateCredits(self, dt):
        timeElapsed = time() - self.timeOfStart
        if timeElapsed < 0:
            return
        if timeElapsed < self.animationTime:
            animationTimeProgress = timeElapsed / self.animationTime
            animationState = AnimationTransition.in_out_circ(animationTimeProgress)
            creditsAnimation = self.creditsBeforePurchase + (
                self.creditsAfterPurchase - self.creditsBeforePurchase
            ) * (animationState)
            self.ids["creditsLabel"].text = f"Your credits: \n{creditsAnimation:.2f}"
        else:
            self.ids[
                "creditsLabel"
            ].text = f"Your credits: \n{self.creditsAfterPurchase:.2f}"
            Clock.unschedule(self.updateCredits)
            Clock.schedule_once(self.dismiss, self.postAnimationTime)
