from flask import Flask, render_template, request
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential


# Put the keys and variables here (never put your real keys in the code)
AOAI_ENDPOINT = "https://polite-ground-030dc3103.4.azurestaticapps.net/api/v1"
AOAI_KEY = "702a03df-3742-4136-bb82-c7b18b256ef5"
MODEL_NAME = "gpt-35-turbo-16k"
AZURE_SEARCH_KEY = AOAI_KEY
AZURE_SEARCH_ENDPOINT = AOAI_ENDPOINT
AZURE_SEARCH_INDEX = "margiestravel"


# Set up the client for AI Chat
client = AzureOpenAI(
    api_key=AOAI_KEY,
    azure_endpoint=AOAI_ENDPOINT,
    api_version="2024-05-01-preview",
)
search_client = SearchClient(
    endpoint=AZURE_SEARCH_ENDPOINT,
    credential=AzureKeyCredential(AZURE_SEARCH_KEY),
    index_name=AZURE_SEARCH_INDEX,
    )




# PUT YOUR IMPORTS HERE


# PUT YOUR CONSTANTS HERE



# PUT YOUR CODE FOR CREATING YOUR AI AND SEARCH CLIENTS HERE



# PUT YOUR CODE FOR GETTING YOUR AI ANSWER INSIDE THIS FUNCTION
def get_response(question):
   
  # 
  # AI CODE GOES IN HERE
  #

  SYSTEM_MESSAGE = "You are an assistant that speaks like a surfer. You can answer questions and provide information. You can also provide sources for your information."


  # What question do you want to ask?
  question = "What is the capital of France?"
  search_results = search_client.search(search_text=question)
  search_summary = " ".join(result["content"] for result in search_results)

  # Create the message history
  messages=[
      {"role": "system", "content": SYSTEM_MESSAGE},
      {"role": "user", "content": question + "\nSources: " + search_summary},
  ]

  # Get the answer using the GPT model (create 1 answer (n) and use a temperature of 0.7 to set it to be pretty creative/random)
  response = client.chat.completions.create(model=MODEL_NAME,temperature=0.7,n=1,messages=messages)
  answer = response.choices[0].message.content
  print(answer)

  return answer


############################################
######## THIS IS THE WEB APP CODE  #########
############################################
# Create a flask app
app = Flask(
  __name__,
  template_folder='templates',
  static_folder='static'
)




# create an index route
@app.get('/')
def index():
  # Return a page that links to these three pages /test-ai, /ask, /chat
  return """<a href="/test-ai">Test AI</a> <br> 
            <a href="/ask">Ask</a> <br> 
            <a href="/chat">Chat</a>"""

# This is the route that shows the form the user asks a question on
@app.get('/test-ai')
def test_ai():
    # Very basic form that sends a question to the /contextless-message endpoint
    return """
    <h1>Ask a question!</h1>
    <form method="post" action="/test-ai">
        <textarea name="question" placeholder="Ask a question"></textarea>
        <button type="submit">Ask</button>
    </form>
    """

# This is the route that the form sends the question to and sends back the response
@app.route("/test-ai", methods=["POST"])
def ask_response():
    # Get the question from the form
    question = request.form.get("question")

    # Return the response from the AI
    return get_response(question)




@app.get('/ask')
def ask():
    # return render_template('hello.html', name=request.args.get('name'))
  return render_template("ask.html")


@app.route('/contextless-message', methods=['GET', 'POST'])
def contextless_message():
    question = request.json['message']
    resp = get_response(question)
    return {"resp": resp[0]}


@app.errorhandler(404)
def handle_404(e):
    return '<h1>404</h1><p>File not found!</p><img src="https://httpcats.com/404.jpg" alt="cat in box" width=400>', 404


if __name__ == '__main__':
  # Run the Flask app
  app.run(host='0.0.0.0', debug=True, port=8080)