import os
import asyncio

from main import snackAttackTrackApp
from kivy.core.window import Window

DELAY = 0.5
PATH = "imagesOutput/"
os.mkdir(PATH)

if os.path.exists("database.db"):
    os.remove("database.db")

Window.size = (800, 480)

app = snackAttackTrackApp()


async def navigateScreensCoroutine():

    await asyncio.sleep(DELAY)

    app.screenManager.database.add_patron("FirstName1", "LastName1", 9001)
    app.screenManager.database.add_patron("FirstName2", "LastName2", 9002)
    app.screenManager.database.add_patron("FirstName3", "LastName3", 9003)
    app.screenManager.database.add_snack("Snack1", 42, "TestImage1", 10)
    app.screenManager.database.add_snack("Snack2", 5, "TestImage2", 12)
    app.screenManager.database.add_snack("Snack3", 16, "TestImage3", 15)

    await asyncio.sleep(DELAY)

    patrons = app.screenManager.database.get_all_patrons()
    snacks = app.screenManager.database.get_all_snacks()

    app.screenManager.login(patrons[0].patronId)
    app.screenManager.setPatronToEdit(patrons[1])
    app.screenManager.setSnackToEdit(snacks[0])

    for screen in app.screenManager.screens:
        app.screenManager.export_to_png(PATH + app.screenManager.current + ".png")
        await asyncio.sleep(DELAY)
        app.screenManager.transitionToScreen(screen.name)
        await asyncio.sleep(DELAY)
        assert app.screenManager.current == screen.name


async def runAppCoroutine():
    await app.async_run()


async def main():

    loop = asyncio.get_event_loop()
    loop.create_task(runAppCoroutine())
    navigateScreenTask = loop.create_task(navigateScreensCoroutine())

    await navigateScreenTask


asyncio.run(main())
