# Use Dart as the base image
FROM dart:stable AS build

# Set the working directory inside the container
WORKDIR /app

# Copy only pubspec.yaml (skip pubspec.lock for now)
COPY ./app/pubspec.yaml ./

# Let Docker run pub get and generate pubspec.lock inside the container
RUN dart pub get

# Copy the rest of the application
COPY ./app/ .  

# Compile the Dart app (optional)
RUN dart compile exe frontend.dart -o /app/frontend

CMD ["/app/frontend"]
