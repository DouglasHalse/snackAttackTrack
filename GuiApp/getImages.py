import os
import asyncio

from main import snackAttackTrackApp
from database import addPatron, addSnack


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

    for screen in app.sm.screens:
        await asyncio.sleep(DELAY)
        app.sm.export_to_png(PATH + app.sm.current + ".png")
        app.sm.current = screen.name
        await asyncio.sleep(DELAY)
        assert app.sm.current == screen.name


async def runAppCoroutine():
    await app.async_run()


async def main():

    loop = asyncio.get_event_loop()
    loop.create_task(runAppCoroutine())
    navigateScreenTask = loop.create_task(navigateScreensCoroutine())

    await navigateScreenTask
    # print(f"Both tasks have completed now: {task11.result()}, {task22.result()}")


asyncio.run(main())
