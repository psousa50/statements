
import asyncio
import os
from dotenv import load_dotenv

from gemini_pro import GeminiPro

async def main():
    load_dotenv()
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    gemini = GeminiPro(api_key=api_key)
    
    prompt = """From the list of Categories and SubCategories, choose which one best matches the following transaction descriptions.
    Assign a score from 1 to 5 on your confidence of the match, where 1 is low confidence and 5 is high confidence.

    Lxcooks, Lda.
    Payment from Galp Power, S.a.
    Sabores Do Dia - Gelado Artesanal, Lda."
    1st Café
    4928code
    7-Eleven
    A Casa Do Bacalhau
    A Padaria Portuguesa
    A Piriquita Da N2
    Ab Storstockholms Loka
    Aerofarma Laboratorios S.A.I.C
    Airbnb
    Alges Com Sabores
    Alipay

    ######### Categories #############:

    Income: Salary
    Income: Wages
    Income: Bonuses
    Income: Interest
    Income: Dividends
    Income: Other Income
    Housing: Rent
    Housing: Mortgage
    Housing: Home Maintenance
    Housing: Repairs
    Housing: Property Tax
    Housing: HOA Fees
    Housing: Furniture
    Housing: Appliances
    Utilities: Electricity
    Utilities: Gas
    Utilities: Heating
    Utilities: Water
    Utilities: Sewer
    Utilities: Trash
    Utilities: Recycling
    Utilities: Internet
    Utilities: Cable
    Utilities: TV
    Utilities: Mobile Phone
    Transportation: Car Payment
    Transportation: Lease
    Transportation: Fuel
    Transportation: Car Insurance
    Transportation: Car Maintenance
    Transportation: Repairs
    Transportation: Public Transit
    Transportation: Train
    Transportation: Bus
    Transportation: Ride-Sharing
    Transportation: Taxi
    Food & Dining: Groceries
    Food & Dining: Restaurants
    Food & Dining: Dining Out
    Food & Dining: Coffee Shops
    Food & Dining: Snacks
    Food & Dining: Fast Food
    Personal Care: Gym
    Personal Care: Fitness
    Personal Care: Salon
    Personal Care: Hair
    Personal Care: Spa
    Personal Care: Cosmetics
    Personal Care: Toiletries

    ######### Output should be JSON, like this: #########
    {
        "Esplanada Cafe": {"category": "Food & Dining: Dining Out", "confidence": 5}
    }    
    """
    
    print("\n=== Testing Single Prompt Generation ===")
    print(f"Prompt: {prompt}")
    
    try:
        response = await gemini.generate(prompt)
        print("\nResponse:")
        print(response)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())