"""LangGraph wrapper that glues planner, executor and re-planner."""
from typing import List
from langgraph.graph import StateGraph, END
from .schemas import PlanExecute, Response, Plan, Act
from .planner import make_plan
from .executor import agent_executor
from .prompts import REPLANNER_PROMPT
from .config import LLM_PLANNER  # we reuse the planner LLM for replanning
from .memory import memory
from .responder import generate_final_response

# ---------- State transition helpers ---------- #

async def plan_step(state: PlanExecute):
    print("🔄 [DEBUG] Iniciando plan_step...")
    print(f"🔄 [DEBUG] Input recibido: {state['input']}")
    
    # Obtener session_id del estado
    session_id = state.get("session_id")
    
    # Crear plan con contexto de conversación
    plan = make_plan(state["input"], session_id)
    print(f"🔄 [DEBUG] Plan generado: {plan.steps}")
    
    # Inicializar conversation_history si no existe
    conversation_history = state.get("conversation_history", [])
    
    return {
        "plan": plan.steps,
        "conversation_history": conversation_history
    }

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
    
    # Incluir contexto de conversación en la tarea si está disponible
    session_id = state.get("session_id")
    context_info = ""
    if session_id:
        context = memory.get_context_for_planning(session_id, max_messages=5)
        if context != "Esta es una nueva conversación.":
            context_info = f"\n\nContexto de conversación:\n{context}"
    
    task_formatted = f"""Para el siguiente plan:
        {plan_str}\n\nTu tarea es ejecutar el paso 1, {task}.{context_info}"""
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
    session_id = state.get("session_id")
    original_input = state.get("input", "")
    
    # Si no hay más pasos en el plan, generar una respuesta final usando el responder
    if not plan:
        print("🔄 [DEBUG] No hay más pasos, generando respuesta final con responder...")
        
        # Obtener el mejor resultado de los pasos ejecutados
        tool_result = ""
        if past_steps:
            # Buscar el resultado más relevante (último con contenido útil)
            for step, result in reversed(past_steps):
                if result and len(result.strip()) > 10:
                    tool_result = result
                    break
        
        if not tool_result:
            tool_result = "No se pudo obtener información específica de las herramientas ejecutadas."
        
        # Generar respuesta final usando el responder
        final_response = await generate_final_response(
            query=original_input,
            tool_result=tool_result,
            session_id=session_id,
            past_steps=past_steps
        )
        
        return {"response": final_response}
    
    plan_str = "\n".join(f"{i+1}. {s}" for i, s in enumerate(plan))
    past = "\n".join(f"{t} --> {r}" for t, r in past_steps)
    print(f"🔄 [DEBUG] Plan string: {plan_str}")
    print(f"🔄 [DEBUG] Past steps: {past}")
    
    # Limitar el número de pasos para evitar bucles infinitos
    if len(past_steps) >= 5:
        print("🔄 [DEBUG] Demasiados pasos ejecutados, finalizando con responder...")
        
        # Obtener el mejor resultado disponible
        tool_result = ""
        if past_steps:
            last_result = past_steps[-1][1]
            tool_result = last_result if last_result else "Proceso completado después de múltiples pasos."
        else:
            tool_result = "Proceso completado después de múltiples pasos."
        
        # Generar respuesta final usando el responder
        final_response = await generate_final_response(
            query=original_input,
            tool_result=tool_result,
            session_id=session_id,
            past_steps=past_steps
        )
        
        return {"response": final_response}
    
    # Incluir contexto de conversación en el replanning
    input_with_context = state["input"]
    if session_id:
        context = memory.get_context_for_planning(session_id, max_messages=5)
        if context != "Esta es una nueva conversación.":
            input_with_context = f"{context}\n\nConsulta actual: {state['input']}"
    
    prompt_chain = REPLANNER_PROMPT | LLM_PLANNER
    print("🔄 [DEBUG] Invocando replanner...")
    
    try:
        reply = (await prompt_chain.ainvoke(
            {
                "input": input_with_context,
                "plan": plan_str or "None",
                "past_steps": past or "None",
            }
        )).content
        print(f"🔄 [DEBUG] Respuesta del replanner: {reply}")

        if reply.startswith("RESPUESTA:"):
            # Usar el responder para generar una respuesta final pulida
            raw_response = reply[len("RESPUESTA:"):].strip()
            
            final_response = await generate_final_response(
                query=original_input,
                tool_result=raw_response,
                session_id=session_id,
                past_steps=past_steps
            )
            
            result = {"response": final_response}
            print(f"🔄 [DEBUG] Finalizando con respuesta del responder: {result}")
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
                print("🔄 [DEBUG] Plan vacío, finalizando con responder...")
                
                final_response = await generate_final_response(
                    query=original_input,
                    tool_result="No se pudo generar un plan válido para continuar.",
                    session_id=session_id,
                    past_steps=past_steps
                )
                
                return {"response": final_response}
        else:
            # fallback: usar el responder para procesar la respuesta
            final_response = await generate_final_response(
                query=original_input,
                tool_result=reply.strip(),
                session_id=session_id,
                past_steps=past_steps
            )
            
            result = {"response": final_response}
            print(f"🔄 [DEBUG] Fallback - respuesta final del responder: {result}")
            return result
            
    except Exception as e:
        print(f"🔄 [DEBUG] Error en replanner: {e}")
        
        final_response = await generate_final_response(
            query=original_input,
            tool_result=f"Error en el proceso de replanificación: {str(e)}",
            session_id=session_id,
            past_steps=past_steps
        )
        
        return {"response": final_response}

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
