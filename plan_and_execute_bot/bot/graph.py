"""LangGraph wrapper that glues planner, executor and re-planner."""
from typing import List
from langgraph.graph import StateGraph, END
from .schemas import PlanExecute, Response, Plan, Act
from .planner import make_plan
from .executor import agent_executor
from .prompts import REPLANNER_PROMPT
from .config import LLM_PLANNER  # we reuse the planner LLM for replanning

# ---------- State transition helpers ---------- #

async def plan_step(state: PlanExecute):
    print("🔄 [DEBUG] Iniciando plan_step...")
    print(f"🔄 [DEBUG] Input recibido: {state['input']}")
    plan = make_plan(state["input"])
    print(f"🔄 [DEBUG] Plan generado: {plan.steps}")
    return {"plan": plan.steps}

async def execute_step(state: PlanExecute):
    print("🔄 [DEBUG] Iniciando execute_step...")
    plan = state["plan"]
    past_steps = state.get("past_steps", [])
    
    print(f"🔄 [DEBUG] Plan actual: {plan}")
    print(f"🔄 [DEBUG] Pasos completados: {len(past_steps)}")
    
    if not plan:
        print("🔄 [DEBUG] No hay más pasos en el plan")
        return {"response": "Plan completado, pero no se pudo obtener una respuesta final."}
    
    # Detectar bucles - si hemos ejecutado la misma tarea más de 2 veces
    task = plan[0]
    task_count = sum(1 for step, _ in past_steps if step == task)
    if task_count >= 2:
        print(f"🔄 [DEBUG] Detectado bucle en la tarea: {task}")
        return {"response": f"No se pudo completar la tarea '{task}' después de múltiples intentos. Por favor, reformula tu consulta."}
    
    plan_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(plan))
    print(f"🔄 [DEBUG] Ejecutando tarea: {task}")
    task_formatted = f"""For the following plan:
        {plan_str}\n\nYou are tasked with executing step 1, {task}."""
    print(f"🔄 [DEBUG] Tarea formateada: {task_formatted}")
    print("🔄 [DEBUG] Invocando agent_executor...")
    
    try:
        agent_response = await agent_executor.ainvoke(
            {"input": task_formatted}
        )
        print(f"🔄 [DEBUG] Respuesta del agente: {agent_response}")
        
        # Agregar el paso completado a past_steps
        new_past_steps = past_steps + [(task, agent_response["output"])]
        
        # Remover el primer paso del plan (ya ejecutado)
        remaining_plan = plan[1:] if len(plan) > 1 else []
        
        result = {
            "past_steps": new_past_steps,
            "plan": remaining_plan
        }
        print(f"🔄 [DEBUG] Resultado de execute_step: {result}")
        return result
        
    except Exception as e:
        print(f"🔄 [DEBUG] Error en execute_step: {e}")
        return {"response": f"Error ejecutando la tarea: {str(e)}"}

async def replan_or_finish(state: PlanExecute):
    """Decide whether to finish or continue."""
    print("🔄 [DEBUG] Iniciando replan_or_finish...")
    print(f"🔄 [DEBUG] Estado actual: {state}")
    
    plan = state.get("plan", [])
    past_steps = state.get("past_steps", [])
    
    # Si no hay más pasos en el plan, intentar generar una respuesta final
    if not plan:
        print("🔄 [DEBUG] No hay más pasos, generando respuesta final...")
        if past_steps:
            last_step_result = past_steps[-1][1]
            # Si el último resultado parece ser una respuesta final, usarla
            if any(keyword in last_step_result.lower() for keyword in ["°c", "clima", "weather", "temperatura", "madrid"]):
                return {"response": last_step_result}
        
        # Si no hay pasos anteriores útiles, generar respuesta genérica
        return {"response": "He completado las tareas disponibles, pero no pude obtener la información solicitada."}
    
    plan_str = "\n".join(f"{i+1}. {s}" for i, s in enumerate(plan))
    past = "\n".join(f"{t} --> {r}" for t, r in past_steps)
    print(f"🔄 [DEBUG] Plan string: {plan_str}")
    print(f"🔄 [DEBUG] Past steps: {past}")
    
    # Limitar el número de pasos para evitar bucles infinitos
    if len(past_steps) >= 5:
        print("🔄 [DEBUG] Demasiados pasos ejecutados, finalizando...")
        if past_steps:
            last_result = past_steps[-1][1]
            return {"response": f"Proceso completado. Último resultado: {last_result}"}
        return {"response": "Proceso completado después de múltiples pasos."}
    
    prompt_chain = REPLANNER_PROMPT | LLM_PLANNER
    print("🔄 [DEBUG] Invocando replanner...")
    
    try:
        reply = (await prompt_chain.ainvoke(
            {
                "input": state["input"],
                "plan": plan_str or "None",
                "past_steps": past or "None",
            }
        )).content
        print(f"🔄 [DEBUG] Respuesta del replanner: {reply}")

        if reply.startswith("RESPONSE:"):
            result = {"response": reply[len("RESPONSE:"):].strip()}
            print(f"🔄 [DEBUG] Finalizando con respuesta: {result}")
            return result
        elif reply.startswith("PLAN:"):
            steps_text = reply[len("PLAN:"):].strip()
            steps = [line.split(".", 1)[1].strip() for line in steps_text.splitlines()
                     if "." in line and line.split(".", 1)[1].strip()]
            if steps:
                result = {"plan": steps}
                print(f"🔄 [DEBUG] Nuevo plan: {result}")
                return result
            else:
                print("🔄 [DEBUG] Plan vacío, finalizando...")
                return {"response": "No se pudo generar un plan válido para continuar."}
        else:
            # fallback: treat as final response
            result = {"response": reply.strip()}
            print(f"🔄 [DEBUG] Fallback - respuesta final: {result}")
            return result
            
    except Exception as e:
        print(f"🔄 [DEBUG] Error en replanner: {e}")
        return {"response": f"Error en el proceso de replanificación: {str(e)}"}

def should_finish(state: PlanExecute):
    has_response = state.get("response") is not None
    has_plan = bool(state.get("plan", []))
    decision = END if has_response else "executor"
    print(f"🔄 [DEBUG] should_finish decision: {decision}")
    print(f"🔄 [DEBUG] Estado tiene respuesta: {has_response}")
    print(f"🔄 [DEBUG] Estado tiene plan: {has_plan}")
    return decision

# ---------- Graph builder ---------- #

def build_chatbot_graph():
    print("🔄 [DEBUG] Construyendo grafo del chatbot...")
    graph = StateGraph(PlanExecute)
    graph.add_node("planner", plan_step)
    graph.add_node("executor", execute_step)
    graph.add_node("replan", replan_or_finish)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "executor")
    graph.add_edge("executor", "replan")
    graph.add_conditional_edges("replan", should_finish)

    compiled_graph = graph.compile()
    print("🔄 [DEBUG] Grafo compilado exitosamente!")
    return compiled_graph
