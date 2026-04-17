import sys
import os

# Add the root directory to sys.path since we are in scratch/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from chatbot import PharmaChatbot

bot = PharmaChatbot()
queries = [
    "Which product has the highest discount?",
    "What is the average sales price?",
    "Total products in the system",
    "Find products with discount greater than 10"
]

for query in queries:
    try:
        sql = bot._get_sql_query(query)
        print("-" * 40)
        print(f"QUERY: {query}")
        print(f"SQL OUTPUT:\n{sql}")
    except Exception as e:
        print(f"ERROR: {e}")
