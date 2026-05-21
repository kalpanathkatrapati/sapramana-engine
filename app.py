"""Application entrypoint - minimal launcher for the refactored package."""
from horolens import create_app

app = create_app()


if __name__=="__main__":
    app.run(debug=True)
