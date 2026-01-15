from app import create_app, config

app, celery = create_app(config.Config)

if __name__ == "__main__":

    app.run(debug=True)
