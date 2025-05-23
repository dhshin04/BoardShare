# BoardShare #
This is a CS 3240 Project: Board Game CMS built using Django. 

## Tools Used ##
This application was built using Django and deployed using GitHub Actions and Heroku. 

## Build ##
To run this application, first create a new `.env` file with:
```
DATABASE_NAME=your_db_name
DATABASE_USER=your_db_user
DATABASE_PASSWORD=your_db_password
GOOGLE_CLIENT_ID=your_google_oauth_client_id
GOOGLE_SECRET=your_google_secret
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_STORAGE_BUCKET_NAME=your_aws_bucket_name
AWS_S3_REGION_NAME=your_aws_region_name
```

If PostgreSQL is not configured, run:
```bash
createdb your_db_name
pg_restore -U your_db_user -d your_db_name latest.dump
```

To run the application on localhost, run:
```bash
python manage.py runserver
```

You can access the application by accessing `localhost:8000` or `127.0.0.1:8000`.

## Contributions ##
Anushka
- Scrum Master

Natalia
- Testing Manager

Andrew
- Requirements Manager

Donghwa
- DevOps Manager

All members contributed equally to the development of our web application. 
