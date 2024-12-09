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

    addPatron("Test", "User", 9001)
    addSnack("TestSnack", 42, "TestImage", 10)

    await asyncio.sleep(DELAY)
    app.sm.export_to_png(PATH + app.sm.current + ".png")
    app.sm.current_screen.OnScreenTouch()
    await asyncio.sleep(DELAY)
    assert app.sm.current == "loginScreen"

    await asyncio.sleep(DELAY)
    app.sm.export_to_png(PATH + app.sm.current + ".png")
    app.sm.current_screen.ids["LoginScreenUserGridLayout"].children[1].Clicked()
    await asyncio.sleep(DELAY)
    assert app.sm.current == "mainUserPage"

    await asyncio.sleep(DELAY)
    app.sm.export_to_png(PATH + app.sm.current + ".png")
    app.sm.current_screen.ids["screenLayout"].children[1].ids["rightContent"].children[
        0
    ].onPressed()
    await asyncio.sleep(DELAY)
    assert app.sm.current == "adminScreen"

    await asyncio.sleep(DELAY)
    app.sm.export_to_png(PATH + app.sm.current + ".png")
    app.sm.current_screen.ids["screenLayout"].children[0].children[
        0
    ].onEditSnacksButtonPressed()
    await asyncio.sleep(DELAY)
    assert app.sm.current == "editSnacksScreen"


async def runAppCoroutine():
    await app.async_run()


async def task1():
    print("Task1")


async def task2():
    print("Task2")


async def main():

    loop = asyncio.get_event_loop()
    loop.create_task(runAppCoroutine())
    navigateScreenTask = loop.create_task(navigateScreensCoroutine())

    await navigateScreenTask
    # print(f"Both tasks have completed now: {task11.result()}, {task22.result()}")


asyncio.run(main())
