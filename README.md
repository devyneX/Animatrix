# Animatrix

A social webapp for anime fans to share their thoughts and opinions on their favorite animes.

## Techs
- Flask
- PostgreSQL
- Flask-SQLAlchemy
- Flask-Migrate
- HTML
- CSS
- JavaScript


## Build Instructions
- Clone the repo using ```git clone https://github.com/devyneX/Animatrix.git```
- Make sure you have Python 3.9 or higher installed
- To install dependencies,
    - Create a virtual environment using ```python -m venv venv```
    - Activate the virtual environment using ```source venv/bin/activate```
    - Install the dependencies using ```pip install -r requirements.txt```
- Or if you have Anaconda installed, use
    - ```conda create -n animatrix python=3.9```
    - ```conda activate animatrix```
    - ```pip install -r requirements.txt```
- Create a PostgreSQL database named Animatrix
- Create a .env file in the root directory and add the following variables:
    - DEV_DB=`postgresql://<username>:<password>@localhost/animatrix`
    - UPLOAD_FOLDER=`path/to/your/upload/folder`
- Initialize database using 
    - ```flask db init```
    - ```flask db migrate```
    - ```flask db upgrade```
- Run the app using ```flask run```
