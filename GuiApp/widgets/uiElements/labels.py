from time import time

from kivy.animation import AnimationTransition
from kivy.clock import Clock
from kivy.uix.gridlayout import GridLayout


class AutoScrollingLabel(GridLayout):
    def __init__(self, text: str = None, **kwargs):
        super().__init__(**kwargs)
        if text is not None:
            self.text = text
        self.widthOverhang = 0.0
        self.startPosition = 0.0
        self.animationStartDelay = 1.0
        self.animationTime = 2.0
        self.postAnimationTime = 1.0
        self.timeOfStart = time() + self.animationStartDelay

        # Need to run this once to get the initial width of the label
        Clock.schedule_once(self.initLabelWidth, 0)

    def initLabelWidth(self, dt):
        # Reset the label position since it could have been changed by a previous animation
        self.ids.label.x = self.x
        entryLabelWidth = self.ids.label.texture_size[0]
        # if text label is wider than the entrylabel, then we need to animate the text
        if entryLabelWidth > self.width:
            self.widthOverhang = entryLabelWidth - self.width
            self.ids.label.x += self.widthOverhang / 2.0
            self.startPosition = self.ids.label.x
            Clock.schedule_interval(self.updateText, 0.01666)
        else:
            # Label scrolling might have been scheduled previously, so unschedule it
            Clock.unschedule(self.updateText)
            Clock.unschedule(self.resetAndStartAnimation)

    def updateText(self, dt):
        timeUsed = time() - self.timeOfStart

        if timeUsed < 0:
            return

        if timeUsed < self.animationTime:
            animationTimeProgress = timeUsed / self.animationTime
            animationState = AnimationTransition.linear(animationTimeProgress)
            self.ids.label.x = self.startPosition - self.widthOverhang * animationState
        else:
            Clock.unschedule(self.updateText)
            Clock.schedule_once(self.resetAndStartAnimation, self.postAnimationTime)

    def resetAndStartAnimation(self, dt):
        self.ids.label.x = self.startPosition
        self.timeOfStart = time() + self.animationStartDelay
        Clock.schedule_interval(self.updateText, 0.01666)
