from dotenv import load_dotenv
from genai import GenAI
import os
import json
import pandas as pd
import ast
from bs4 import BeautifulSoup
import requests
from PIL import Image


# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize AI model
jarvis = GenAI(OPENAI_API_KEY)

def is_image(file_path):
    try:
        with Image.open(file_path) as img:
            img.verify()  # Check if it's an actual image
        return True
    except Exception:
        return False
    

def get_personality_string(df):
    """
    Generate a personality profile based on the user's tweets.

    Parameters:
        df (pd.DataFrame): DataFrame containing the user's tweets.

    Returns:
        dict: Dictionary with personality traits.
    """
    # Extract tweets and clean them
    tweets = df['text'].astype(str).fillna("").tolist()
    cleaned_tweets = "\nTweet: ".join(tweets)

    # Generate personality profile using AI model
    instructions = f"""Here are the tweets of a Twitter user:\n{cleaned_tweets}\n.  Summarize the personality of the user based on their tweets.
    Include their political views, interests, relevant personality traits, and speaking style.  Return only this summary
    as a paragraph of text."""
    response = jarvis.generate_text(cleaned_tweets, instructions, model='gpt-4o', output_type='text')
    return response

def get_reaction(content, file_path, personality_string ):
    """
    Simulate a user's reaction to new content based on their tweets, personality, and topics of interest.

    Parameters:
        content (str): The content the persona is reacting to (can be a URL, HTML, or plain text).
        file_path (string): file path of image or video uploaded by user.
        personality_string (str): string personality traits.
  
    Returns:
        dict: Dictionary with 'reaction_text' (user's simulated response) and 'reaction_score' (0 to 100).
    """
    cleaned_content = content

    # Handle URL input
    if content.strip().lower().startswith("http"):
        try:
            print(f"Fetching webpage... {content}")
            page = requests.get(content, timeout=5)
            soup = BeautifulSoup(page.text, 'html.parser')
            cleaned_content = soup.get_text(separator="\n")
            cleaned_content = jarvis.generate_text(cleaned_content, "Summarize this webpage", model='gpt-4o', output_type='text')
        except Exception as e:
            cleaned_content = f"(Could not fetch webpage. Error: {e})\nOriginal content:\n{content}"

    # Handle raw HTML
    elif "<" in content and ">" in content:
        try:
            soup = BeautifulSoup(content, 'html.parser')
            cleaned_content = soup.get_text(separator="\n")
        except Exception as e:
            cleaned_content = f"(Could not parse HTML. Error: {e})\nOriginal content:\n{content}"

    # Compose full instruction
    instructions = f"""Here is the personality profile of 
    a Twitter user:\n{personality_string}\n"""

    instructions += """You will be given a piece of content (e.g., an article, a tweet, an image). Based on the user's personality profile
      write a simulated reaction to the content in the voice of the user.
Also return how much the user likes the content on a scale from 0 (hates it) to 100 (loves it).  Return your answer as a
JSON object with the following format:
{
    "reaction_text": "...",
    "reaction_score": <reaction_score>
}
"""

    prompt = cleaned_content
    print(f"Cleansed content: {cleaned_content}")
    if file_path and is_image(file_path):
        print(f"Image path: {file_path}")
        response = jarvis.generate_text(prompt, 
                                        instructions, 
                                        image_paths_list=[file_path], 
                                        model='gpt-4o',  
                                        output_type='json_object')
    
    elif file_path and file_path.endswith('.pdf'):
        print(f"PDF path: {file_path}")
        prompt = jarvis.read_pdf(file_path)
        response = jarvis.generate_text(prompt, 
                                        instructions, 
                                        model='gpt-4o', 
                                        output_type='json_object')
    
  
    else:
        response = jarvis.generate_text(prompt, 
                                        instructions, 
                                        model='gpt-4o', 
                                        output_type='json_object')

    return json.loads(response)
