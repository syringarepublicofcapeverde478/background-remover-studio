"""Project entrypoint for Background Remover Studio."""

from background_remover import App


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
