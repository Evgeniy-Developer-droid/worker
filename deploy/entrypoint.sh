#!/bin/sh



if [ "$DATABASE" = "postgres" ]
then
	SQL_EXISTS=$(printf '\dt "%s"' "job_stack")
    if [[ $(PGPASSWORD="$DB_PASS" psql -h "db" -U $DB_USER -d $DB_NAME -c "$SQL_EXISTS") ]]
	then
	    echo "Table exists ..."

	else
	    echo "Table not exists ..., init database"
	    flask db init
	    flask db migrate
	    flask db upgrade
	fi
fi
# python manage.py flush --no-input
# python manage.py migrate
exec "$@"