import os
import re
import json
import streamlit as st

# To help construct our Chat Messages
from langchain.schema import HumanMessage
from langchain.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate

# We will be using ChatGPT model (gpt-3.5-turbo)
from langchain.chat_models import ChatOpenAI

# To parse outputs and get structured data back
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

# use your OpenAI API secret key
os.environ["OPENAI_API_KEY"] = "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"

 # The schema I want out
response_schemas = [
    ResponseSchema(name="question", description="A question generated from input text snippet."),
    ResponseSchema(name="options", description="Possible choices of the multiple choice question."),
    ResponseSchema(name="answer", description="Correct answer for question.")
]

# The parser that will look for the LLM output in my schema and return it back to me
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

# The format instructions that LangChain makes. Let's look at them
format_instructions = output_parser.get_format_instructions()

print(format_instructions)

# create ChatGPT object
chat_model = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo')

# The prompt template that brings it all together
prompt = ChatPromptTemplate(
    messages=[
        HumanMessagePromptTemplate.from_template("""Given a text input from the user, generate multiple choice questions 
        from it along with the correct answer. 
        \n{format_instructions}\n{user_prompt}""")  
    ],
    input_variables=["user_prompt"],
    partial_variables={"format_instructions": format_instructions}
)

st.title("AnshitaAI Quiz Generator")
user_prompt = st.text_input("Enter a quiz topic.")
button = st.button("Generate")
score=0
if user_prompt and button:
 with st.spinner("Generating..."):

    

  text = 'Generate a general knowledge quiz with 3 multiple choice questions with 4 options each. The options should be labelled 1, 2, 3, 4. The topic is ' + user_prompt 
  user_query = prompt.format_prompt(user_prompt = text)

  user_query_output = chat_model(user_query.to_messages())

# Given plain string containing multiple queries
  queries_string = user_query_output.content
  print(queries_string)


# Split the string into individual queries

# List to store information for each question
  questions_info = []

  json_strings = []
  start_pos = 0

  while True:
    start_pos = queries_string.find('{', start_pos)
    if start_pos == -1:
        break
    end_pos = queries_string.find('}', start_pos) + 1
    json_strings.append(queries_string[start_pos:end_pos])
    start_pos = end_pos

# Convert each substring to a JSON object
  json_objects = [json.loads(json_str) for json_str in json_strings]

# Print the resulting JSON objects
  print(json.dumps(json_objects, indent=2))

  quiz_data = []

  for obj in json_objects:
    question_data = {
        "question": obj.get("question", ""),
        "options": [option.strip() for option in obj.get("options", "").split('\n')],
        "answer": obj.get("answer", "")
    }
    quiz_data.append(question_data)

  for question_data in quiz_data:
    print("Question:", question_data["question"])
    print("Options:")
    for i, option in enumerate(question_data["options"], start=1):
        print(f"{i}. {option}")
    print("Correct Answer:", question_data["answer"])
    print()
    
  for i in range(2):
    st.write(quiz_data[i]['question'])  #this prints the question
    q=st.radio(quiz_data[i]['question'],[
      quiz_data[i]['options'][0],quiz_data[i]['options'][1],quiz_data[i]['options'][2],quiz_data[i]['options'][3]],
      key=i,index=None)
    if q==quiz_data[i]['answer']:
      score = score+1
      st.write('Correct') 
    else:
     st.write('Incorrect, correct answer was '+ quiz_data[i]['answer'])
     
st.write(score) 
    

