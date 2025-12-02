# Mini-App Documentation

This directory contains the source code for the admin mini-app, which is a React application built with Vite. The mini-app provides a user interface for administrators and game administrators to manage the Field Game.

## Core Functionalities

The mini-app has the following features:

*   **Point Updates:** Admins and game admins can use the mini-app to update the points of any group in the game. The app provides a form where they can enter the group name, the game number, and the number of points to add.
*   **Group Ownership Transfer:** Super admins can transfer ownership of a group from one user to another. This is useful if the original owner of a group is no longer able to participate in the game.
*   **Role-Based Access Control:** The mini-app's functionality is restricted based on the user's role. The user's role is passed as a URL parameter, and the app's UI is adjusted accordingly. For example, only super admins can see the "Transfer Group Ownership" button.

## File Breakdown

*   `index.html`: The main HTML file for the mini-app.
*   `src/main.jsx`: The entry point for the React application.
*   `src/App.jsx`: The main application component. It handles the routing between the different views of the app and manages the app's state.
*   `src/components/TransferGroupOwnershipForm.jsx`: A component that provides a form for transferring group ownership.

## How to Run

To run the mini-app in development mode, you can use the following commands:

```bash
npm install
npm run dev
```

To build the mini-app for production, you can use the following command:

```bash
npm run build
```