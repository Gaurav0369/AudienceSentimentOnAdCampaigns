
# 1. Base Image: Use an official Python runtime as a parent image

FROM python:3.9-slim

# 2. Set Environment Variables 
ENV PYTHONDONTWRITEBYTECODE 1 
ENV PYTHONUNBUFFERED 1    

# 3. Set Working Directory: Create and set the working directory in the container
WORKDIR /app

# 4. Install Dependencies:

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt --index-url https://download.pytorch.org/whl/cpu

# 5. Copy Application Code: Copy the rest of your application files

COPY . .


# 6. Download the model during the build process.
RUN python -c "from transformers import AutoModelForSequenceClassification, AutoTokenizer; \
               print('Downloading model...'); \
               MODEL = 'cardiffnlp/twitter-roberta-base-sentiment-latest'; \
               AutoTokenizer.from_pretrained(MODEL); \
               AutoModelForSequenceClassification.from_pretrained(MODEL); \
               print('Model download complete.')"
# --- End Model Pre-downloading ---

# 7. Expose Port: Make port 5000 available to the host machine
EXPOSE 5000

# 8. Run Application: Command to run the application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]