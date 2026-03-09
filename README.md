# Vendor Notes Mini Web App

## Overview

This is a Django-based web application for managing vendors and their associated notes. It includes an ETL workflow for exporting data to Excel and importing from CSV files, with local file storage capabilities.

## Project Structure

- `vendor_notes/`: Main Django project directory
- `vendors/`: Django app containing models, views, and templates
- `templates/`: HTML templates
- `db.sqlite3`: SQLite database
- `manage.py`: Django management script

## Features

- **Vendor Management**: Create, read, update, and delete vendors
- **Notes**: Attach notes to vendors with title, content, and timestamp
- **ETL Export**: Export vendors and notes to Excel file
- **ETL Import**: Import vendors and notes from CSV with validation
- **File Storage**: Dynamic folder creation for uploaded files

## Setup Instructions

1. Install dependencies: `pip install -r requirements.txt`
2. Start server: `python manage.py runserver`

## ETL Workflow

- **Export**: Navigate to `/export/` to download an Excel file with vendors and notes
- **Import**: Go to `/import/` to upload a CSV file. Specify a folder path for storage.

## Libraries Used

- Django: Web framework
- Pandas: Data manipulation for CSV handling
- OpenPyXL: Excel file operations

## Challenges and Solutions

- Handling file uploads with dynamic paths: Used os.makedirs to create folders dynamically
- CSV validation: Implemented try-except blocks for error handling during import

## Improvements

- Add user authentication
- Add search and filtering capabilities
- Improve UI
