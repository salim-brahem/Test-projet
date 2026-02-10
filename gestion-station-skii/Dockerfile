# Use an official OpenJDK runtime as a parent image
FROM eclipse-temurin:17-jdk-jammy
#modified
# Set working directory inside container
WORKDIR /app

# Copy the built JAR file from target directory into the container
COPY target/gestion-station-skii-0.0.1-SNAPSHOT.jar app.jar

# Expose your Spring Boot app port (change if different)
EXPOSE 8083

# Run the JAR file
ENTRYPOINT ["java", "-jar", "app.jar"]
