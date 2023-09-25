# Use an official Node runtime as base image
FROM node:18-alpine

# Set working directory
WORKDIR /usr/src/app

# Copy package.json and package-lock.json for installing dependencies
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the source code into the container
COPY . .

# Build the Next.js app
RUN npm run build

# Expose the running port
EXPOSE 3000

# Command to run the application
CMD ["npm", "start"]
