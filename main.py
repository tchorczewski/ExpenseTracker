from app import create_app, config
from app.tasks import budget_tasks

app, celery = create_app(config.Config)

if __name__ == "__main__":

    app.run(debug=True)
