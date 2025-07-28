# BoardShare #
This is a clone of [https://github.com/original/OriginalProjectName](https://github.com/uva-cs3240-s25/project-a-09), a CS 3240 Project at UVA. Since the original project was private, I created a public clone with my contributions below:

## My Contributions
1. Collectively developed board game lending CMS with 3 other developers.
2. Added support for image uploads, user reviews, and in-app notifications after integrating PostgreSQL (local and Heroku Postgres) and AWS S3.
3. Set up CI/CD pipeline via GitHub Actions CI and Heroku.
4. Set up GitHub Secrets and `.gitignore` to prevent secret env variables from leaking onto commits.

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
