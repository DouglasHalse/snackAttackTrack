import os
import asyncio

from main import snackAttackTrackApp
from database import addPatron, addSnack, getAllPatrons, getAllSnacks


DELAY = 0.5
PATH = "imagesOutput/"
os.mkdir(PATH)

if os.path.exists("database.db"):
    os.remove("database.db")

app = snackAttackTrackApp()


async def navigateScreensCoroutine():

    await asyncio.sleep(DELAY)

    addPatron("FirstName1", "LastName1", 9001)
    addPatron("FirstName2", "LastName2", 9002)
    addPatron("FirstName3", "LastName3", 9003)
    addSnack("Snack1", 42, "TestImage1", 10)
    addSnack("Snack2", 5, "TestImage2", 12)
    addSnack("Snack3", 16, "TestImage3", 15)

    await asyncio.sleep(DELAY)

    patrons = getAllPatrons()
    snacks = getAllSnacks()

    app.screenManager.login(patrons[0].patronId)
    app.screenManager.setPatronToEdit(patrons[1])
    app.screenManager.setSnackToEdit(snacks[0])

    for screen in app.screenManager.screens:
        await asyncio.sleep(DELAY)
        app.screenManager.export_to_png(PATH + app.screenManager.current + ".png")
        app.screenManager.current = screen.name
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
