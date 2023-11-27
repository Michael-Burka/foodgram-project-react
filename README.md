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
