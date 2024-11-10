# -*- coding: utf-8 -*-
"""Multi_Agent_System.py

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1p8fZOXF-CY_NdA7_BbR6JvZs6ro4D6i-
"""

# pip install transformers langchain crewai pydantic
import subprocess
import sys

def install_dependencies():
    # List of dependencies
    dependencies = [
        "transformers",
        "langchain",
        "crewai",
        "pydantic"
    ]
    
    for _ in dependencies:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "protobuf==3.20.*"])

# Call the function to install dependencies
if __name__ == "__main__":
    install_dependencies()


import os
from transformers import pipeline
from crewai import Agent, Task, Crew
from crewai_tools import DirectoryReadTool, FileReadTool, SerperDevTool


# Define a custom Hugging Face agent
class HuggingFaceAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create_prompt(self, task_description):
        return f"Task: {task_description}\n"

    def run(self, task_description, model_name="gpt2"):
        # Initialize the pipeline locally within this method
        generator = pipeline("text-generation", model=model_name)
        prompt = self.create_prompt(task_description)
        result = generator(prompt, max_length=150, num_return_sequences=1)
        return result[0]['generated_text']

    @property
    def llm_prefix(self):
        return "LLM Prefix"

    @property
    def observation_prefix(self):
        return "Observation Prefix"

# Define tools for the agents
docs_tool = DirectoryReadTool(directory='./research-summaries')
file_tool = FileReadTool()
search_tool = SerperDevTool()  # Example tool for web search

# Define agent setup function with a parameter for the company name
def setup_agents(company_name):
    # Create agents with dynamic goals and descriptions based on the specified company name

    # 1. Industry Research Analyst
    industry_research_agent = HuggingFaceAgent(
        role='Industry Research Analyst',
        goal=f'Research the industry and segment in which {company_name} operates. Identify {company_name}’s key offerings and strategic focus.',
        backstory='An experienced analyst specializing in researching industry segments and corporate strategies.',
        tools=[search_tool]
    )

    # 2. Market Use Case Generator
    market_usecase_generator = HuggingFaceAgent(
        role='Market Use Case Generator',
        goal=f'Analyze industry trends and propose relevant AI/ML use cases for {company_name}.',
        backstory='A market analyst identifying relevant AI and ML use cases for the specified company.',
        tools=[search_tool]
    )

    # 3. Resource Collector
    resource_collector = HuggingFaceAgent(
        role='Resource Collector',
        goal=f'Collect datasets and resources relevant to {company_name}’s use cases, such as those from Kaggle, Hugging Face, and GitHub.',
        backstory='A resource expert sourcing datasets and reports for AI/ML use cases.',
        tools=[search_tool, docs_tool, file_tool]
    )

    # Return a dictionary of agents
    return {
        "industry_research_agent": industry_research_agent,
        "market_usecase_generator": market_usecase_generator,
        "resource_collector": resource_collector
    }

# Define tasks for each agent
def create_tasks(company_name, agents):
    # Industry Research Task
    industry_analysis_task = Task(
        description=f'Research the industry, {company_name}’s key offerings, and areas of strategic focus.',
        expected_output=f'Summary of the industry, {company_name}’s key offerings, and strategic areas of focus.',
        agent=agents["industry_research_agent"]
    )

    # Market Use Case Generation Task
    use_case_task = Task(
        description=f'Identify relevant AI/ML use cases for {company_name} in its industry sector.',
        expected_output=f'List of relevant AI/ML use cases that align with {company_name}’s goals and operations.',
        agent=agents["market_usecase_generator"]
    )

    # Resource Collection Task
    resource_collection_task = Task(
        description=f'Gather datasets and resources to support AI/ML use cases for {company_name}. Provide clickable links to resources.',
        expected_output=f'Clickable links to datasets and reports relevant to {company_name}’s AI/ML initiatives.',
        agent=agents["resource_collector"]
    )

    # Return a list of tasks
    return [industry_analysis_task, use_case_task, resource_collection_task]

# Generalized function to run tasks for any specified company
def run_company_analysis(company_name):
    # Setup agents for the specified company
    agents = setup_agents(company_name)

    # Create tasks for the specified company
    tasks = create_tasks(company_name, agents)

    # Create a crew and add tasks
    crew = Crew(tasks=tasks)

    # Run the tasks for each agent and print outputs
    print(f"\n--- Multi-Agent Analysis for {company_name} ---\n")
    for task in crew.tasks:
        print(f"Running task: {task.description}")
        output = task.agent.run(task.description, model_name="gpt2")  # Specify model_name for text generation
        print("Output:\n", output)
        print("\n" + "-"*300 + "\n")

# # Run analysis for a specific company, 
# run_company_analysis("Google")

# # Run analysis for a specific company,
# run_company_analysis("Microsoft")

# # Run analysis for a specific company, 
# run_company_analysis("Amazon")

import streamlit as st
from transformers import pipeline

def run_company_analysis(company_name):
    st.write(f"## Multi-Agent Analysis for {company_name}")
    agents = setup_agents(company_name)
    tasks = create_tasks(company_name, agents)
    crew = Crew(tasks=tasks)
    
    for task in crew.tasks:
        st.write(f"### Task: {task.description}")
        output = task.agent.run(task.description, model_name="gpt2")
        st.write("Output:\n", output)
        st.write("---")

# Streamlit user input to specify the company name
st.title("Multi-Agent Industry Analysis System")
company_name = st.text_input("Enter a company name for analysis:", "Amazon")

if st.button("Run Analysis"):
    run_company_analysis(company_name)
