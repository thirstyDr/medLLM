from flask import Flask, request, render_template, redirect
import openai
import time

app = Flask(__name__)

# Replace 'your_openai_api_key' with your actual API key from OpenAI
openai.api_key = "your secret key"

def read_document(file):
    """Read the first 3-4 lines of the specified document."""
    lines = file.readlines()
    return lines[:4]  # Read the first 3-4 lines

def chat_with_gpt(prompt):
    """Send the provided prompt to GPT and return the response."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message['content'].strip()
    except openai.error.RateLimitError:
        print("Rate limit exceeded. Waiting for 10 seconds before retrying.")
        time.sleep(10)  # Wait for 10 seconds before retrying
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message['content'].strip()
        except openai.error.RateLimitError:
            return "Rate limit exceeded. Try again later."

def format_prompt(lines):
    """Format the prompt by adding a specific instruction to summarize the lines."""
    content = " ".join([line.decode('utf-8', errors='ignore') for line in lines])  # Decode binary content
    return f"Imagine you are a doctor and you want to summarize these lines into language that will be easy to understand for the patients: {content}"

@app.route('/')
def upload_form():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    if file:
        # Read the first 3-4 lines from the uploaded file
        lines_to_read = read_document(file)

        # Format the prompt with additional instruction
        prompt = format_prompt(lines_to_read)

        # Send the prompt to GPT using the chat_with_gpt function and get the response
        gpt_response = chat_with_gpt(prompt)

        # Render the template with the GPT-4 response
        return render_template('upload.html', gpt_response=gpt_response)

if __name__ == "__main__":
    app.run(debug=True)
