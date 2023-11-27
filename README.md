# Foodgram: Recipe Sharing and Shopping List Application

## Overview

Foodgram is a single-page SPA (Single Page Application) web platform created using React and Django. It enables users to share their favorite recipes, bookmark recipes from other users, and follow their favorite authors to stay updated on new culinary creations. One of its standout features is a convenient "Shopping List" service that empowers users to generate and download ingredient lists for their chosen dishes, simplifying the grocery shopping experience.

### Main Pages

- **Homepage**: Displays the first six recipes, sorted by publication date. Implements pagination.
- **Recipe Page**: Complete recipe description with options for authorized users to add to favorites, shopping lists, and follow the author.
- **User Page**: Displays the user's name, their published recipes, and the option to follow them.
- **Subscriptions Page**: For account owners to view their subscriptions. Subscription options are available for registered users.

### User Interaction Scenarios

- **Favorites**: Users can add recipes to favorites and view or modify their favorites list.
- **Shopping List**: Only accessible to registered users. Users can add recipes to the list and download a consolidated list of ingredients in a user-friendly format.
- **Creating and Editing Recipes**: Available to logged-in users. All fields are mandatory.
- **Tag Filtering**: Recipes can be filtered by tags for easy searching.
- **Registration and Authentication System**: Incorporates user registration and authentication with various user roles (guest, registered user, administrator).

## Workflow Description

This project uses GitHub Actions for continuous integration and deployment. The workflow is defined in `.github/workflows/main.yml` and consists of the following jobs:

1. **Tests**: Runs automated tests using different versions of Python (3.9, 3.10, 3.11). It includes setting up a PostgreSQL database for testing purposes.

2. **Build Backend and Push to Docker Hub**: After successful tests, the backend Docker image is built and pushed to Docker Hub.

3. **Build Frontend and Push to Docker Hub**: Similar to the backend, the frontend Docker image is built and pushed to Docker Hub.

4. **Deploy**: This job is responsible for deploying the application. It includes copying necessary files to the server via SSH, creating a `.env` file with secrets, and executing Docker commands to start the application.

5. **Send Message**: Sends a notification message upon successful deployment.

## Environment Setup and Application Import

### `.env` File

The `.env` file is essential for configuring the Foodgram application. It contains environment variables critical for the application's operation, such as database credentials, secret keys, and other sensitive configurations. Create this file in the root directory of your project with the following structure:

```env
POSTGRES_DB=<your_database_name>
POSTGRES_USER=<your_database_user>
POSTGRES_PASSWORD=<your_database_password>
DB_NAME=<your_database_name>
DB_HOST=<your_database_host>
DB_PORT=<your_database_port>
DJANGO_SUPERUSER_PASSWORD=<your_django_admin_password>
SECRET_KEY=<your_django_secret_key>
DEBUG='False'
CSRF_TRUSTED_ORIGINS=<your_csrf_trusted_origins>
```

## Important Security Consideration

For the `.env` file:

- **Do not commit the `.env` file to version control**. This file contains sensitive information that should remain confidential. Always keep it out of public repositories to prevent exposing secrets like database credentials and Django's secret key.

## Application Import Process

The Foodgram application has an automated setup and launch process managed by the `run_app.sh` script. This script ensures a smooth operation of the application by handling the following tasks:

1. **Wait for Database Connection**: Ensures that the script waits until the database is ready to accept connections, preventing any connection-related errors during the startup.

2. **Database Migrations**: Performs Django migrations for 'users' and 'recipes' apps to ensure the database schema is correctly set up.

3. **Data Loading**: Data Loading: Imports initial data into the database, including ingredients from `transformed_ingredients.json` and tag fixtures from `tag_fixtures.json`.

4. **Superuser Creation**: Creates a Django superuser account using the credentials provided in the `.env` file. This account is essential for accessing the Django admin panel.

5. **Collect Static Files**: Gathers static files (CSS, JavaScript, images) in a single location, facilitating their access and serving.

6. **Start Gunicorn Server**: Launches the application using Gunicorn, a Python WSGI HTTP server, with a specified number of workers and binds it to a designated port. This step is crucial for the application to start receiving and responding to HTTP requests.

## Feedback and contact

If you have suggestions, inquiries, or just wish to discuss any aspect of this project:

- **Name**: Michael Burka 
- **Email**: [contact@michaelburka.com](mailto:contact@michaelburka.com) 
- **GitHub**: [Michael-Burka's GitHub Profile](https://github.com/Michael-Burka/) 
- **LinkedIn**: [Michael-Burka's LinkedIn Profile](https://www.linkedin.com/in/michael-burka-485832251/) 
