#!/bin/bash

# Activate virtual environment if needed
# source venv/bin/activate

# Run the Streamlit frontend
echo "Starting Streamlit frontend..."
streamlit run frontend.py &

# Run the Streamlit app
echo "Starting Streamlit app..."
streamlit run app.py &

# Run the FastAPI backend with uvicorn
echo "Starting FastAPI backend..."
uvicorn api:app --reload &

# Wait for all background processes to finish
wait