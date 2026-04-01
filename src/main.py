"""Project entrypoint for Background Remover Studio."""

from background_remover import App
from updater import check_and_update


def main() -> None:
    # Verifica atualizações no GitHub antes de abrir o app.
    # Silencioso se não houver internet ou se já estiver atualizado.
    check_and_update()

    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
