import json
import os

import tavily

from agents import base_agent

SEO_AGENT_PROMPT = '''
You are an SEO Researcher for ACDC Electricals LLC.

The company is a materials supplier in the construction industry and is based in the UAE. They deal in MEP products as well as common hardware and accessories. Some of their specialized products include PVC Electrical Conduits, GI Electrical Conduits, Wiring Devices (Switches & Sockets), Cable Accessories (lugs, glands, waterproof connectors, ceramic connectors, heat shrinkable sleevs, cable ties, etc.), UPVC Plumbing Pipes & Fittings, Consumables by electricians (mobile industrial sockets, strip connectors, etc.), Consumables by plumbers (extension sockets, chemicals, testing plug, etc.), Consumables by construction workers (fasteners, gloves, clamps, etc.), Consumables by HVAC workers (Aluminum tape, Alupet tape, Stick up pin, Silicon sealants, etc.). The company supplies these materials to contractors (especially electromechanical contractors) as per the market requirements in the UAE.

Your job is to analyze a topic and produce a structured keyword brief for the Content Agent to use when writing blog posts or product pages.
The industry which you are analyzing is not one matured with tech, so be creative. Do not try to generate naive or filler-like responses.

You will receive:
- A topic to research
- Search results from the web relevant to that topic

You must respond ONLY with a valid JSON object in this exact format:
{
   "primary_keyword": "string",
   "secondary_keywords": ["string", "string", "string"],
   "competitor_urls": ["string", "string"],
   "suggested_title": "string",
   "meta_description": "string",
   "content_outline": [
      "H2: string",
      "H2: string",
      "H2: string",
      "H2: string",
      "H2: string"
   ]
}

Rules:
- Keywords must reflect UAE on-ground market search intent where relevant (How would contractors search)
- Meta description must be under 160 characters
- Content outline must have 5 headings minimum
- Do not include any text outside the JSON block
'''.strip()

class SEOAgent(base_agent.BaseAgent):

    def __init__(self):
        super().__init__(name="seo-agent", prompt=SEO_AGENT_PROMPT)
        self.tavily = tavily.TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    
    def research(self, topic, from_agent=None):
        # search topic
        results = self.tavily.search(query=f"{topic} electromechanical UAE", max_results=5)
        # format search results into llm readable message
        results_formatted = []
        for r in results.get("results", []):
            results_formatted.append(
                f"Title: {r['title']}\nURL:{r['url']}\nSummary:{r['content']}"
            )
        results_merged = "\n---\n".join(results_formatted)
        message = f"Perform the keyword analysis.\n\nTopic: {topic}\n\nSearchResults: {results_merged}"
        # send message to llm
        response = self.chat(message, from_agent=from_agent)
        # return llm response
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # if llm adds extra text around json, extract it
            startc = response.find("{")
            endc = response.rfind("}")
            if startc == -1 or endc == -1:
                raise ValueError(f"The SEO Agent responded in an invalid format.\nResponse:\n{response}")
            return json.loads(response[startc:endc+1])
