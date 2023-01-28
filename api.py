"""TLDR Prompt app that generates summaries from input text.

Based on Steamship's Prompt App Mini template: https://replit.com/@steamship/Steamship-Prompt-App-Mini-Template
Demo here: https://app.steamship.com/packages/tldr

If you want to run this you'll need to add your Steamship API KEY as an ENV variable
"""
import os
import re
import uuid

from steamship import Steamship
from steamship.invocable import post, longstr
from prompt_service import PromptService


class TLDRPackage(PromptService):
    PROMPT_TEMPLATE = '''Act as an executive assistant and write an executive summary of a {input_type}. Write the 
    summary as paragraphs, separate each paragraph with two new lines. Focus on the key message and skip side 
    information. Keep each paragraph short and less than 40 words by removing fluffy words. Keep your output under 
    {max_n_tokens} tokens.
  
    {input_type}: {in_text}.'''

    REDUCTION_FACTOR = .10
    MIN_N_TOKENS = 400

    @post("generate")
    def generate(self, input_text: longstr) -> str:
        """Generate summaries from input text."""

        max_n_tokens = max(len(input_text.split()) * self.REDUCTION_FACTOR, self.MIN_N_TOKENS)

        prompt_text = self.PROMPT_TEMPLATE.format(in_text=input_text, max_n_tokens=max_n_tokens,
                                                  input_type="technical text")

        return re.sub(r"(\n+)-(\w)*", r"\n\n- ", self.complete_prompt(prompt_text)).strip()


if __name__ == "__main__":
    api_key = os.environ.get('STEAMSHIP_API_KEY')
    if not api_key:
        print("""You must add your Steamship API key as an env variable to run this code seamlessly. 
                 Get your free API key here: https://steamship.com/account/api - You'll get free access to 
                 OpenAI GPT, no credit card required.""")
        api_key = input("Enter API Key: ")

    client = Steamship(api_key=api_key)
    client.switch_workspace(str(uuid.uuid4()))
    package = TLDRPackage(client)

    in_text = longstr('''Choose your technologies accordingly. Orchestration Example: Airflow Throughout most of this 
    chapter, we have actively avoided discussing any particular technology too extensively. We make an exception for 
    orchestration because the space is currently dominated by one open source technology, Apache Airflow. Maxime 
    Beauchemin kicked off the Airflow project at Airbnb in 2014. Airflow was developed from the beginning as a 
    noncommercial open source project. The framework quickly grew significant mindshare outside Airbnb, becoming an 
    Apache Incubator project in 2016 and a full Apache-sponsored project in 2019. Airflow enjoys many advantages, 
    largely because of its dominant position in the open source marketplace. First, the Airflow open source project 
    is extremely active, with a high rate of commits and a quick response time for bugs and security issues, 
    and the project recently released Airflow 2, a major refactor of the codebase. Second, Airflow enjoys massive 
    mindshare.''')
    print("")
    for i in range(2):
        print(f"Summary {i + 1}\n---\n{package.generate(input_text=in_text)}\n---")

    client.get_workspace().delete()
