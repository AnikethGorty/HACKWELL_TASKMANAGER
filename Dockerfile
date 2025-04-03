# Use Dart as the base image
FROM dart:stable AS build

# Set the working directory inside the container
WORKDIR /app

# Copy only pubspec files first (for dependency caching)
COPY app/pubspec.yaml app/pubspec.lock ./

# Ensure `pubspec.lock` is generated properly
RUN dart pub get

# Copy the rest of the application
COPY app/ .  

# Compile the Dart app (optional)
RUN dart compile exe frontend.dart -o /app/frontend

CMD ["/app/frontend"]
