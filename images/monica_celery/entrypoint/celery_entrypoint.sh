#!/bin/sh

# wait for RabbitMQ server to start
echo "ENTERED IN CELERY WORKER ENTRYPOINT v1.9"

echo "CHECK PosgreSQL Server Availability"

until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$DB_PORT_5432_TCP_ADDR" -p "${DB_PORT_5432_TCP_PORT}" -d "${DB_NAME}" -U "${DB_USER}" -W "$POSTGRES_PASSWORD" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "PosgreSQL Active"

echo "CREATE MIGRATION FOLDER AND BEAT SCHEDULE IF NOT EXISTS"

[ ! -d "./jobs/migrations" ] && mkdir "./jobs/migrations"
[ ! -f "./jobs/migrations" ] && touch "./jobs/migrations/__init__.py"
[ ! -f "/var/run/celery/beat-schedule" ] && touch "/var/run/celery/beat-schedule"

echo "CHANGE OWNERSHIP FILES and FOLDERS"

chown myuser:myuser -R .
chown myuser:myuser ./jobs
chown myuser:myuser ./manage.py
chown myuser:myuser ./shared/settings/appglobalconf.py
chown myuser:myuser ./jobs/models.py
chown myuser:myuser /var/run/celery/beat-schedule
chown myuser:myuser ./jobs/migrations
chown myuser:myuser ./jobs/migrations/__init__.py
chown myuser:myuser /logs/

echo "CREATE MIGRATIONS RESOURCES"
# FIXME: Retrieved from web container (DB Migration)
# prepare init migration
# su -m myuser -c "python3 manage.py makemigrations --name worker users jobs shared --settings=shared.settings.appglobalconf"
su -m myuser -c "python3 manage.py makemigrations --name worker jobs --settings=shared.settings.appglobalconf"
# migrate db, so we have the latest db schema

echo "SHOW MIGRATION RESOURCES"

su -m myuser -c "python3 manage.py showmigrations"

echo "PERFORM REAL MIGRATION"
su -m myuser -c "python3 manage.py migrate jobs"

# su -m myuser -c "python3 manage.py migrate jobs --settings=shared.settings.appglobalconf"
# FIXME: Retrieved from web (DB Migration)
echo "END MIGRATION. WAIT FOR START RabbitMQ"

until nc -zvw3 "${RABBITMQ_HOSTNAME}" "${RABBITMQ_PORT}"; do
  >&2 echo "RabbitMQ is unavailable - sleeping"
  sleep 1
done

# su -m root -c "apt-get autoremove -y netcat"

echo "RabbitMQ Available. LAUNCHING CELERY"
# run Celery worker for our project monica with Celery configuration stored in Celeryconf
su -m myuser -c "celery -A jobs.tasks worker -Q priority_queue,crowd_queue_elaboration,crowd_queue_provisioning,queue_sw_update_info,queue_task_alive -l INFO -s /var/run/celery/beat-schedule --without-mingle --loglevel=warning -c 10 -B"

echo "ERROR CELERY Launch"