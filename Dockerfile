# Use Dart official image
FROM dart:stable

# Set the working directory
WORKDIR /app

# Copy Dart project files
COPY app/pubspec.yaml /app/
COPY app/pubspec.lock /app/

# Install dependencies
RUN dart pub get

# Copy the rest of the application
COPY app/ /app/

# Compile the Dart application
RUN dart compile exe frontend.dart -o /app/frontend

# Set the entry point
CMD ["/app/frontend"]
