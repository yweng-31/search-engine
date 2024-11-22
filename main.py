from langchain.tools import Tool
from langchain.llms import OpenAI
from langchain.agents import initialize_agent
import os
import requests
from dotenv import load_dotenv
import streamlit as st
from langchain.prompts import PromptTemplate

load_dotenv()

# functions
def get_recipe_details(recipe_id, api_key):
    url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        recipe_data = response.json()
        steps = []
        if 'analyzedInstructions' in recipe_data and recipe_data['analyzedInstructions']:
            # Extract steps from the analyzedInstructions field
            for step in recipe_data['analyzedInstructions'][0]['steps']:
                steps.append(step['step'])
        return steps
    else:
        return f"Error: Unable to fetch details for recipe ID {recipe_id}"
    
def get_recipe_from_spoonacular(ingredients):
    api_key = spoonacular_api_key  # Replace with your Spoonacular API key
    url = f"https://api.spoonacular.com/recipes/findByIngredients?ingredients={ingredients}&number=3&apiKey={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        recipes = response.json()
        recipe_summaries = []
        for recipe in recipes:
            recipe_name = recipe['title']
            recipe_id = recipe['id']
            steps = get_recipe_details(recipe_id, api_key)
            # Combine recipe name and step-by-step instructions
            recipe_summary = f"Recipe: {recipe_name}\nSteps: {' '.join(steps)}"
            recipe_summaries.append(recipe_summary)
        return recipe_summaries
    else:
        return f"Error: {response.status_code}"
spoonacular_tool = Tool(
    name="Spoonacular Recipe Finder",
    func=lambda ingredients: get_recipe_from_spoonacular(ingredients),
    description="Get recipes based on ingredients using Spoonacular API."
)
    


prompt_template_name = PromptTemplate(
    input_variables =['ingredients','diet'],
    template = "please find recipes with {ingredients}. Adapt the recipe if there's someone {diet}."
)


open_api_key = os.getenv("OPENAI_API_KEY")
spoonacular_api_key = os.getenv("RECIPE_API")
st.title('Find your perfect recipe based on what you have and your dietery restrictions')
ingredients = st.text_input('What ingredients do you want to include in the dish?', 'Whatever you wanna get rid of in the fridge!')
diet = st.multiselect('What are your dietary restrictions',['Vegan','Vegetarian','Gluten-free','Lactose-intolerant'],[])

llm = OpenAI(temperature=0.7)

# Initialize an agent with your Spoonacular tool
tools = [spoonacular_tool]
agent = initialize_agent(tools, llm, agent_type="zero-shot-react-description", verbose=True)

p = prompt_template_name.format(ingredients=ingredients,diet = diet)
if st.button('Confirm'):
    with st.spinner("Running agent..."):
        result = agent.run(p)
    st.success("Agent response:")
    st.write(result)

