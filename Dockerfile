# Use the official Dart image
FROM dart:stable

# Set the working directory in the container
WORKDIR /app

# Copy pubspec files first (to take advantage of Docker's layer caching)
COPY pubspec.* ./

# Get dependencies (this speeds up builds when dependencies don’t change)
RUN dart pub get

# Copy the rest of the application code
COPY . .

# Expose the port (if your Dart app runs a server)
EXPOSE 8080

# Run the Dart application
CMD ["dart", "run", "bin/server.dart"]
