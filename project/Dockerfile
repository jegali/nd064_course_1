# Step 2
# Students will be able to use Docker to create
# container images and push them to a public
# container registry

# base image: python in version 2.7
# ok... but... why??? completely deprecated
FROM python:2.7

WORKDIR /usr/src/app

# copy the requirements file
# and install packages defined in the requirements.txt file
COPY ./techtrends/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy the app source code
COPY ./techtrends ./

# Ensure that the databse is initialized with the
# predefined posts in th einit_db.py file
RUN python init_db.py

# expose the application port 3111
EXPOSE 3111

# The Application should execute on the container start
CMD [ "python", "app.py" ]