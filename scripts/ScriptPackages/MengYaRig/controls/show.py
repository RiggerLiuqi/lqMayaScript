import ui

window = None


def show():
    global window
    if window is None:
        window = ui.CurveMain()
    window.show()
