import asyncio
import os

from dotenv import load_dotenv
from gemini_ai import GeminiAI


async def main():
    load_dotenv()

    api_key = os.environ.get("GOOGLE_API_KEY")
    gemini = GeminiAI(api_key=api_key)

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

    Housing: Rent
    Housing: Mortgage
    Housing: Home Maintenance / Repairs
    Housing: Property Tax
    Housing: HOA Fees
    Housing: Furniture / Appliances
    Utilities: Electricity
    Utilities: Gas / Heating
    Utilities: Water / Sewer
    Utilities: Trash / Recycling
    Utilities: Internet
    Utilities: Cable / TV
    Utilities: Mobile Phone
    Transportation: Car Payment / Lease
    Transportation: Fuel
    Transportation: Car Insurance
    Transportation: Car Maintenance / Repairs
    Transportation: Public Transit / Train / Bus
    Transportation: Ride-Sharing / Taxi
    Food & Dining: Groceries
    Food & Dining: Restaurants / Dining Out
    Food & Dining: Coffee Shops
    Food & Dining: Snacks / Fast Food
    Personal Care: Gym / Fitness
    Personal Care: Salon / Hair / Spa
    Personal Care: Cosmetics / Toiletries
    Health & Medical: Doctor / Clinic
    Health & Medical: Dental
    Health & Medical: Pharmacy
    Health & Medical: Health Insurance
    Health & Medical: Therapy / Counseling
    Insurance (Non-Health): Life Insurance
    Insurance (Non-Health): Home Insurance
    Insurance (Non-Health): Auto Insurance
    Insurance (Non-Health): Travel Insurance
    Debt & Financial: Loans
    Debt & Financial: Credit Card Payments
    Debt & Financial: Bank Fees / Service Charges
    Shopping: Clothing / Accessories
    Shopping: Electronics / Gadgets
    Shopping: Household Supplies
    Shopping: Online Shopping
    Entertainment: Movies / Concerts / Shows
    Entertainment: Streaming Services
    Entertainment: Books / Magazines
    Entertainment: Games / Apps
    Subscriptions: Memberships
    Subscriptions: News / Magazines
    Subscriptions: Software / SaaS
    Travel: Flights / Train Tickets
    Travel: Accommodation
    Travel: Rental Car / Taxis
    Travel: Travel Activities / Tours
    Family & Children: Childcare / Babysitting
    Family & Children: Education / Tuition
    Family & Children: School Supplies
    Family & Children: Activities / Sports
    Pets: Pet Food & Supplies
    Pets: Vet / Pet Insurance
    Pets: Grooming
    Gifts & Donations: Gift Purchases
    Gifts & Donations: Charitable Donations
    Gifts & Donations: Religious Donations
    Taxes: Income Tax
    Taxes: Property Tax
    Taxes: Other Taxes / Tax Preparation
    Miscellaneous: Uncategorized
    Miscellaneous: One-time / Surprise Expenses
    Miscellaneous: Other

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
