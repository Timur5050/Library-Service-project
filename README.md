# Library-Service-project


This Library Service project allows users to borrow books for a fee, with additional charges for overdue returns. It integrates a Telegram bot that automatically sends notifications to a Telegram group when books are borrowed or returned, streamlining communication and library management.

# Features
- JWT authentication
- Admin panel
- Comfortable documentation
- Managing payments and books
- Creating borrows
- Docker and docker-compose
- PostgreSQL
- Permissions
- Celery
- Celery-beat
- Periodic tasks
- Telegram api
- Stripe
- Payment system
- Tests

# Run program using GitHub
To run Celery with both a worker and beat scheduler in separate terminals, you can follow these instructions. This will ensure your Celery tasks are processed and scheduled correctly. Below is a step-by-step guide for setting up and starting the Celery worker and Celery beat scheduler.
### You need to have docker installed

```sh
# Clone the repository
git clone https://github.com/Timur5050/Library-Service-project.git
# Change to the project directory
cd Library-Service-project
# Create a virtual environment
python -m venv venv
# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
# Install required packages
pip install -r requirements.txt
# Create new Postgres DB & User
# Copy sample.env -> .env and populate with all required data 
# Apply migrations
python manage.py migrate

# Run Redis Server
docker run -d -p 6379:6379 redis

# Terminal 1: Start Celery Worker
- celery -A library_service worker --loglevel=INFO --without-gossip --without-mingle --without-heartbeat -Ofair --pool=solo

# Terminal 2: Start Celery Beat Scheduler
- celery -A library_service beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler

# Create schedule for running sync in DB
run app: python manage.py runserver
```

# Run with Docker
### You need to have docker
```sh
# Clone the repository
git clone https://github.com/Timur5050/rick-and-morty.git
# Change to the project directory
cd rick-and-morty
# Copy sample.env -> .env and populate with all required data 
# Build and run docker-compose
docker-compose up --build
Create admin user & Create schedule for running sync in DB
```

some demo photos:

