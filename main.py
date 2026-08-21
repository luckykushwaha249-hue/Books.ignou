"""
Books.IGNOU
-----------
100% offline Android app (Kivy + KivyMD).
Ek baar Settings me file upload karo, uske baad koi internet nahi chahiye.

Files:
  main.py          -> yeh file (poori app logic)
  books.kv         -> UI design (Kivy auto-load karta hai kyunki App class ka naam "BooksApp" hai)
  buildozer.spec   -> Android APK build karne ki config
  README.md        -> build/run instructions
"""

import os
import mimetypes
from functools import partial

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.storage.jsonstore import JsonStore
from kivy.uix.screenmanager import Screen
from kivy.utils import platform

from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.toast import toast

SEMESTERS = [1, 2, 3, 4, 5, 6]


def get_system_theme() -> str:
    """Android ke system dark/light mode ko detect karta hai. Baaki platforms pe Light default."""
    if platform == "android":
        try:
            from jnius import autoclass

            PythonActivity = autoclass("org.kivy.android.PythonActivity")
            Configuration = autoclass("android.content.res.Configuration")
            activity = PythonActivity.mActivity
            ui_mode = activity.getResources().getConfiguration().uiMode
            night_mask = Configuration.UI_MODE_NIGHT_MASK
            night_yes = Configuration.UI_MODE_NIGHT_YES
            if (ui_mode & night_mask) == night_yes:
                return "Dark"
            return "Light"
        except Exception:
            return "Light"
    return "Light"


# ----------------------------------------------------------------------------------
# Cross platform "open this file with the default app" helper
# ----------------------------------------------------------------------------------
def open_file_external(path: str):
    """File ko uske default app (PDF reader, Word, etc.) me kholta hai. 100% offline."""
    if not path or not os.path.exists(path):
        toast("File nahi mili, dobara upload karein")
        return

    mime_type, _ = mimetypes.guess_type(path)
    mime_type = mime_type or "*/*"

    try:
        if platform == "android":
            from jnius import autoclass

            Intent = autoclass("android.content.Intent")
            Uri = autoclass("android.net.Uri")
            JFile = autoclass("java.io.File")
            FileProvider = autoclass("androidx.core.content.FileProvider")
            PythonActivity = autoclass("org.kivy.android.PythonActivity")

            activity = PythonActivity.mActivity
            java_file = JFile(path)
            authority = activity.getPackageName() + ".fileprovider"
            uri = FileProvider.getUriForFile(activity, authority, java_file)

            intent = Intent(Intent.ACTION_VIEW)
            intent.setDataAndType(uri, mime_type)
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            activity.startActivity(intent)

        elif platform == "win":
            os.startfile(path)  # noqa

        elif platform == "macosx":
            import subprocess
            subprocess.call(("open", path))

        else:  # linux, testing on desktop
            import subprocess
            subprocess.call(("xdg-open", path))

    except Exception as e:  # best-effort: kabhi kabhi koi app installed nahi hoti
        toast(f"File open nahi ho payi: {e}")


# ----------------------------------------------------------------------------------
# Local, offline data store (JSON file on device) -> theme + har semester ki file
# ----------------------------------------------------------------------------------
class AppData:
    def __init__(self, app):
        store_path = os.path.join(app.user_data_dir, "books_data.json")
        self.store = JsonStore(store_path)

    def get_theme(self) -> str:
        if self.store.exists("theme"):
            return self.store.get("theme")["mode"]
        return "Light"

    def set_theme(self, mode: str):
        self.store.put("theme", mode=mode)

    def get_file(self, semester: int):
        key = f"semester_{semester}"
        if self.store.exists(key):
            data = self.store.get(key)
            if os.path.exists(data.get("path", "")):
                return data["path"], data["name"]
        return None, None

    def set_file(self, semester: int, path: str, name: str):
        self.store.put(f"semester_{semester}", path=path, name=name)

    def clear_file(self, semester: int):
        key = f"semester_{semester}"
        if self.store.exists(key):
            self.store.delete(key)


# ----------------------------------------------------------------------------------
# Screens
# ----------------------------------------------------------------------------------
class HomeScreen(Screen):
    def on_pre_enter(self, *args):
        MDApp.get_running_app().refresh_home()


class SettingsScreen(Screen):
    def on_pre_enter(self, *args):
        MDApp.get_running_app().refresh_settings()


class ThemeScreen(Screen):
    def on_pre_enter(self, *args):
        MDApp.get_running_app().refresh_theme_screen()


# ----------------------------------------------------------------------------------
# Main App
# ----------------------------------------------------------------------------------
class BooksApp(MDApp):

    def build(self):
        self.title = "Books.IGNOU"
        self.data = AppData(self)

        self.theme_cls.primary_palette = "Blue"
        saved_mode = self.data.get_theme()  # "Light" / "Dark" / "System"
        self.theme_cls.theme_style = (
            get_system_theme() if saved_mode == "System" else saved_mode
        )

        self.menu = None
        return Builder.load_file("books.kv")

    # ---------------- Top-bar 3-dot menu: Home / Settings / Theme ----------------
    def open_menu(self, button):
        items = [
            {"text": "Home", "on_release": lambda: self.menu_go("home")},
            {"text": "Settings", "on_release": lambda: self.menu_go("settings")},
            {"text": "Theme", "on_release": lambda: self.menu_go("theme")},
        ]
        self.menu = MDDropdownMenu(caller=button, items=items, width_mult=3)
        self.menu.open()

    def menu_go(self, screen_name):
        if self.menu:
            self.menu.dismiss()
        self.root.current = screen_name

    # ---------------------------- HOME ----------------------------
    def refresh_home(self):
        grid = self.root.get_screen("home").ids.semester_grid
        grid.clear_widgets()

        from kivy.factory import Factory

        for sem in SEMESTERS:
            path, name = self.data.get_file(sem)
            has_file = path is not None

            card = Factory.SemesterCard(semester_num=sem, has_file=has_file)
            card.bind(on_release=partial(self.on_semester_tap, sem))
            grid.add_widget(card)

    def on_semester_tap(self, semester, *args):
        path, name = self.data.get_file(semester)
        if path:
            open_file_external(path)
        else:
            toast(f"Semester {semester} ke liye pehle Settings me file upload karein")
            self.root.current = "settings"

    # ---------------------------- SETTINGS ----------------------------
    def refresh_settings(self):
        box = self.root.get_screen("settings").ids.settings_list
        box.clear_widgets()

        from kivy.factory import Factory

        for sem in SEMESTERS:
            path, name = self.data.get_file(sem)
            row = Factory.SettingsRow(
                semester_num=sem,
                has_file=path is not None,
                file_name=name or "Koi file upload nahi hui",
            )
            row.ids.upload_btn.bind(on_release=partial(self.select_file, sem))
            row.ids.remove_btn.bind(on_release=partial(self.remove_file, sem))
            box.add_widget(row)

    def select_file(self, semester, *args):
        try:
            from plyer import filechooser
            filechooser.open_file(on_selection=partial(self.on_file_chosen, semester))
        except Exception as e:
            toast(f"File chooser open nahi hua: {e}")

    def on_file_chosen(self, semester, selection):
        # plyer ka callback background thread se aa sakta hai -> main thread pe schedule karo
        def _apply(*_):
            if selection:
                path = selection[0]
                name = os.path.basename(path)
                self.data.set_file(semester, path, name)
                toast(f"Semester {semester}: {name} upload ho gayi")
                self.refresh_settings()
                if self.root.current == "home":
                    self.refresh_home()

        Clock.schedule_once(_apply, 0)

    def remove_file(self, semester, *args):
        self.data.clear_file(semester)
        toast(f"Semester {semester} ki file hata di gayi")
        self.refresh_settings()

    # ---------------------------- THEME ----------------------------
    def refresh_theme_screen(self):
        current = self.data.get_theme()
        box = self.root.get_screen("theme").ids.theme_list
        for child in box.children:
            child.selected = (child.mode_value == current)

    def set_theme(self, mode, *args):
        self.data.set_theme(mode)
        self.theme_cls.theme_style = get_system_theme() if mode == "System" else mode
        self.refresh_theme_screen()


if __name__ == "__main__":
    BooksApp().run()
