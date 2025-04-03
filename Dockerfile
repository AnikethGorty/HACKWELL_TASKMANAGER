# Use official Dart image
FROM dart:stable

# Set working directory
WORKDIR /app

# Copy the pubspec files and get dependencies
COPY app/pubspec.yaml app/pubspec.lock ./

RUN dart pub get

# Copy the rest of the application files
COPY app/ .

# Compile the Dart app
RUN dart compile exe frontend.dart -o /app/frontend

# Set the entry point
CMD ["/app/frontend"]
