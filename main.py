import streamlit as st
import json
import os

from langchain.schema import HumanMessage
from langchain.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate

# We will be using ChatGPT model (gpt-3.5-turbo)
from langchain.chat_models import ChatOpenAI

# To parse outputs and get structured data back
from langchain.output_parsers import StructuredOutputParser, ResponseSchema

# use OpenAI API secret key
os.environ["OPENAI_API_KEY"] = "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"

 # The schema I want out
response_schemas = [
    ResponseSchema(name="question", description="A question generated from input text snippet."),
    ResponseSchema(name="options", description="Possible choices of the multiple choice question."),
    ResponseSchema(name="answer", description="Correct answer for question.")
]

# The parser that will look for the LLM output in my schema and return it back to me
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

# The format instructions that LangChain makes
format_instructions = output_parser.get_format_instructions()

print(format_instructions)

chat_model = ChatOpenAI(temperature=0, model_name='gpt-3.5-turbo')

# The prompt template that brings it together
prompt = ChatPromptTemplate(
    messages=[
        HumanMessagePromptTemplate.from_template("""Given a text input from the user, generate multiple choice questions 
        from it along with the correct answer. 
        \n{format_instructions}\n{user_prompt}""")  
    ],
    input_variables=["user_prompt"],
    partial_variables={"format_instructions": format_instructions}
)
 
# Function to initialize session state
def initialize_session():
    return st.session_state.get("score", 0), st.session_state.get("current_question", 0), st.session_state.get("selected_option", None)
 
# Sample quiz data
quiz_data = []
 
# Function to load quiz data from JSON strings
def load_quiz_data(queries_string):
    global quiz_data
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
 
    for obj in json_objects:
        question_data = {
            "question": obj.get("question", ""),
            "options": [option.strip() for option in obj.get("options", "").split('\n')],
            "answer": obj.get("answer", "")
        }
        quiz_data.append(question_data)
 
# Streamlit App
def main():
    st.title("AnshitaAI Quiz Generator")
 
    # Initialize session state
    score, current_question, selected_option = initialize_session()
 
    # Quiz Generation
    user_prompt = st.text_input("Enter a quiz topic.")
    button = st.button("Generate")
 
    if user_prompt and button:
        with st.spinner("Generating..."):
 
            # Construct prompt for quiz generation
            text = 'Generate a general knowledge quiz with 3 multiple choice questions with 4 options each. The options should be labelled 1, 2, 3, 4. The topic is ' + user_prompt 
            user_query = prompt.format_prompt(user_prompt = text)
            user_query_output = chat_model(user_query.to_messages())
 
            # Parse outputs and load quiz data
            queries_string = user_query_output.content
            load_quiz_data(queries_string)
 
    # Quiz App
    if quiz_data:
        # Check if the user has made a selection
        if selected_option is not None:
            # Check if the selected option is correct
            current_question_data = quiz_data[current_question]
            if selected_option == current_question_data['answer']:
                st.success("Correct!")
                score += 1
            else:
                st.error(f"Wrong! Correct answer: {current_question_data['answer']}")
 
        # Display the current question
        current_question_data = quiz_data[current_question]
        st.header(f"Question {current_question + 1}")
        st.markdown(f"**{current_question_data['question']}**")
 
        # Display radio buttons for options
        selected_option = st.radio(f"Options:", current_question_data['options'])
 
        st.write("---")  # Separator between questions
 
        # Display final score when all questions are answered
        if current_question == len(quiz_data) - 1:
            st.title("Quiz Completed")
            st.success(f"Your Final Score: {score}/{len(quiz_data)}")
        else:
            # Button to move to the next question
            if st.button("Next Question"):
                current_question += 1
                selected_option = None  # Reset selected option for the new question
 
        # Update session state
        st.session_state.score = score
        st.session_state.current_question = current_question
        st.session_state.selected_option = selected_option
 
if __name__ == "__main__":
    main()
