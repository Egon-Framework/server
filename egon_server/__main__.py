"""The primary entrypoint for running the parent application."""

from .cli import Application


def main():
    """Launch the commandline application"""

    app = Application()
    app.execute()


if __name__ == '__main__':
    main()
