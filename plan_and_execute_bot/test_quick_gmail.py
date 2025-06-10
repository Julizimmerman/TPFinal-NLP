"""Test rápido solo para Gmail."""
import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from bot.orchestrators.gmail_orchestrator import gmail_orchestrator_node
from bot.schemas import PlanExecute

async def test_gmail():
    """Test solo para Gmail."""
    
    print("📧 Probando Gmail orchestrator...")
    
    try:
        state = PlanExecute(
            input="Envía un correo a test@example.com con asunto 'Prueba' y mensaje 'Hola mundo'",
            session_id="test_123"
        )
        
        result = await gmail_orchestrator_node(state)
        print(f"✅ Resultado: {result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gmail()) 