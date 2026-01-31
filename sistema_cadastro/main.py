import flet as ft

from app.ui import build_ui

def main (page: ft.Page):
    build_ui(page)


if __name__ == "__main__":   #são 2 _ em cada
    ft.app(target=main)