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


