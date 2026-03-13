import os

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from db import message_bus


class BaseAgent:

    def __init__(self, name, prompt, temperature=0):
        self.name = name
        self.prompt = prompt

        self.messages = [SystemMessage(content=self.prompt)]
        self.model = ChatGroq(model="llama-3.1-8b-instant", temperature=temperature, api_key=os.getenv("GROQ_API_KEY"))

    def chat(self, message, from_agent=None, to_agent=None):
        # if the caller doesn't intend to redirect the response to some other agent(s), then the response is returned to the caller only
        to_agent = to_agent or from_agent
        
        # log caller message
        message_bus.insert_message(to_agent=self.name, from_agent=from_agent, content=message)

        # labelling the message to let the agent know who is sending the message
        labelled_message = f"[{from_agent if from_agent else 'user'}]: {message}"
        self.messages.append(HumanMessage(content=labelled_message))

        response = self.model.invoke(self.messages)

        self.messages.append(response)
        message_bus.insert_message(content=response.content, from_agent=self.name, to_agent=to_agent)
        return response.content
