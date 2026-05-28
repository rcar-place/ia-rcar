import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.gemini.ai_service import generate_response

async def main():
    try:
        res = await generate_response("Olá, comprei mas veio quebrado", item_context="Título: Vaso de Cerâmica | Preço: 50.00")
        print("Success:", res)
    except Exception as e:
        print("Error caught in test:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
