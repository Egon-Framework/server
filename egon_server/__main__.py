"""The ``__main__`` module acts as the primary entrypoint for running
the parent application from the command line.
"""

from .cli import Application


def main():
    """Launch the commandline application"""

    app = Application()
    app.execute()


if __name__ == '__main__':
    main()
