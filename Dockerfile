# Use a Python base image
FROM python:3.13-alpine

# Set the working directory
WORKDIR /app

# Copy the bot's code to the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the bot
CMD ["python3", "app/bot.py"]