"""LangGraph wrapper that glues planner, executor and re-planner."""
from typing import List
from langgraph.graph import StateGraph, END
from .schemas import PlanExecute, Response, Plan, Act
from .planner import make_plan
from .executor import agent_executor
from .executors import execute_specialized_task, execute_multiple_tasks
from .prompts import REPLANNER_PROMPT
from .config import LLM_PLANNER  # we reuse the planner LLM for replanning
from .memory import memory
from .responder import generate_final_response

# ---------- State transition helpers ---------- #

async def plan_step(state: PlanExecute):
    print("🔄 [DEBUG] Iniciando plan_step...")
    print(f"🔄 [DEBUG] Estado completo recibido: {state}")
    
    # Handle different input formats more robustly
    user_input = None
    
    # Try different ways to get the user input
    if "input" in state:
        user_input = state["input"]
    elif "messages" in state and state["messages"]:
        # Handle LangGraph Studio format with messages
        last_message = state["messages"][-1]
        if isinstance(last_message, dict):
            user_input = last_message.get("content", "")
        else:
            user_input = str(last_message)
    elif "message" in state:
        user_input = state["message"]
    else:
        # Look for any string value in the state
        for key, value in state.items():
            if isinstance(value, str) and value.strip():
                user_input = value
                break
    
    if not user_input:
        print("🔄 [DEBUG] No se pudo encontrar input en el estado")
        return {"response": "No se pudo obtener la consulta del usuario."}
    
    print(f"🔄 [DEBUG] Input procesado: {user_input}")
    
    # Obtener session_id del estado
    session_id = state.get("session_id")
    
    # Crear plan con contexto de conversación
    plan = await make_plan(user_input, session_id)
    print(f"🔄 [DEBUG] Plan generado: {plan.steps}")
    
    # Inicializar conversation_history si no existe
    conversation_history = state.get("conversation_history", [])
    
    return {
        "input": user_input,  # Ensure input is preserved in state
        "plan": plan.steps,
        "conversation_history": conversation_history
    }

async def execute_step(state: PlanExecute):
    print("🔄 [DEBUG] Iniciando execute_step...")
    plan = state["plan"]
    past_steps = state.get("past_steps", [])
    tool_results = state.get("tool_results", [])  # Acumula resultados de tools
    
    print(f"🔄 [DEBUG] Plan actual: {plan}")
    print(f"🔄 [DEBUG] Pasos completados: {len(past_steps)}")
    
    if not plan:
        print("🔄 [DEBUG] No hay más pasos en el plan")
        return {"response": "Plan completado, pero no se pudo obtener una respuesta final."}
    
    # Determinar cuántos pasos ejecutar en esta iteración
    steps_to_execute = []
    
    # Siempre ejecutar el primer paso
    steps_to_execute.append(plan[0])
    
    # Si hay más pasos y son complementarios, ejecutarlos también
    if len(plan) > 1:
        # Identificar si los siguientes pasos son complementarios
        # (por ejemplo, crear tareas múltiples, buscar y analizar, etc.)
        current_step = plan[0].lower()
        
        # Detectar patrones de múltiples operaciones relacionadas
        for i in range(1, min(len(plan), 3)):  # Máximo 3 pasos por ejecución
            next_step = plan[i].lower()
            
            # Casos donde tiene sentido ejecutar múltiples pasos:
            should_execute_together = False
            
            # 1. Múltiples creaciones de tareas
            if ("crear" in current_step and "tarea" in current_step and
                "crear" in next_step and "tarea" in next_step):
                should_execute_together = True
            
            # 2. Operaciones de listado seguidas de operaciones específicas
            elif ("listar" in current_step and any(word in next_step for word in ["completar", "eliminar", "editar"])):
                should_execute_together = True
                
            # 3. Búsquedas seguidas de acciones específicas
            elif ("buscar" in current_step and any(word in next_step for word in ["completar", "eliminar", "editar"])):
                should_execute_together = True
                
            # 4. Obtener información del clima seguido de consejos
            elif ("clima" in current_step and "consejo" in next_step):
                should_execute_together = True
            
            if should_execute_together:
                steps_to_execute.append(plan[i])
            else:
                break
    
    print(f"🔄 [DEBUG] Ejecutando {len(steps_to_execute)} pasos: {steps_to_execute}")
    
    # Detectar bucles de manera más inteligente
    # Solo finalizar si una tarea específica ha fallado múltiples veces
    for task in steps_to_execute:
        # Contar intentos de esta tarea específica
        task_attempts = [(step, result) for step, result in past_steps if step == task]
        
        # Si la tarea ha fallado más de 2 veces, entonces sí hay un bucle problemático
        failed_attempts = [result for _, result in task_attempts if result and "Error" in result]
        if len(failed_attempts) >= 2:
            print(f"🔄 [DEBUG] Detectado bucle problemático en la tarea: {task} (falló {len(failed_attempts)} veces)")
            
            # Generar una respuesta más útil usando el responder
            from .responder import generate_final_response
            session_id = state.get("session_id")
            original_input = state.get("input", "")
            
            final_response = await generate_final_response(
                query=original_input,
                tool_result=f"No se pudo completar la tarea '{task}' después de múltiples intentos fallidos.",
                session_id=session_id,
                past_steps=past_steps
            )
            return {"response": final_response}
    
    plan_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(plan))
    
    # Incluir contexto de conversación si está disponible
    session_id = state.get("session_id")
    context_info = ""
    if session_id:
        context = memory.get_context_for_planning(session_id, max_messages=5)
        if context != "Esta es una nueva conversación.":
            context_info = f"\n\nContexto de conversación:\n{context}"
    
    # Formatear la tarea considerando múltiples pasos
    if len(steps_to_execute) == 1:
        task_formatted = f"""Para el siguiente plan:
        {plan_str}\n\nTu tarea es ejecutar el paso 1: {steps_to_execute[0]}.{context_info}"""
    else:
        steps_text = "\n".join(f"- {step}" for step in steps_to_execute)
        task_formatted = f"""Para el siguiente plan:
        {plan_str}\n\nTu tarea es ejecutar los siguientes pasos relacionados:
        {steps_text}
        
        Ejecuta todas estas tareas en secuencia, usando múltiples herramientas si es necesario.{context_info}"""
    
    print(f"🔄 [DEBUG] Tarea formateada: {task_formatted}")
    print("🔄 [DEBUG] Invocando ejecutor especializado...")
    
    try:
        # Usar el ejecutor especializado directamente
        if len(steps_to_execute) == 1:
            # Ejecutar una sola tarea
            result = await execute_specialized_task(task_formatted, session_id)
        else:
            # Ejecutar múltiples tareas relacionadas
            result = await execute_multiple_tasks(steps_to_execute, session_id)
        
        print(f"🔄 [DEBUG] Respuesta del ejecutor especializado: {result}")
        
        # Agregar todos los pasos completados a past_steps
        new_past_steps = past_steps[:]
        for step in steps_to_execute:
            new_past_steps.append((step, result))
            tool_results.append(result)  # Acumula el resultado de la tool
        
        print(f"🔄 [DEBUG] tool_results acumulados: {tool_results}")
        # Remover los pasos ejecutados del plan
        remaining_plan = plan[len(steps_to_execute):] if len(plan) > len(steps_to_execute) else []
        
        result_dict = {
            "past_steps": new_past_steps,
            "plan": remaining_plan,
            "tool_results": tool_results
        }
        print(f"🔄 [DEBUG] Resultado de execute_step: {result_dict}")
        return result_dict
        
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
    
    # Get original input with the same robust handling as plan_step
    original_input = state.get("input", "")
    if not original_input and "messages" in state and state["messages"]:
        last_message = state["messages"][-1]
        if isinstance(last_message, dict):
            original_input = last_message.get("content", "")
        else:
            original_input = str(last_message)
    elif not original_input:
        original_input = state.get("message", "")
    
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
        print(f"🔄 [DEBUG] [RESPONSE] Respuesta final generada: {final_response}")
        return {"response": final_response}
    
    plan_str = "\n".join(f"{i+1}. {s}" for i, s in enumerate(plan))
    past = "\n".join(f"{t} --> {r}" for t, r in past_steps)
    print(f"🔄 [DEBUG] Plan string: {plan_str}")
    print(f"🔄 [DEBUG] Past steps: {past}")
    
    # Detectar bucles infinitos de manera más inteligente
    # Contar pasos únicos ejecutados exitosamente
    successful_steps = [step for step, result in past_steps if result and "EXITOSO" in result]
    unique_successful_steps = len(set(successful_steps))
    
    # Contar pasos fallidos repetidos
    failed_steps = [step for step, result in past_steps if result and "Error" in result]
    repeated_failures = len([step for step in set(failed_steps) if failed_steps.count(step) >= 2])
    
    # Contar pasos repetidos exitosos (que podrían indicar un bucle)
    repeated_successful_steps = []
    for step in set(successful_steps):
        count = successful_steps.count(step)
        if count >= 3:  # Si un paso exitoso se repite 3+ veces, es un bucle
            repeated_successful_steps.append(step)
    
    # Finalizar solo si hay demasiados pasos fallidos repetidos O si hay bucles de pasos exitosos
    # O si ya se ejecutaron muchos pasos sin progreso real
    if (repeated_failures >= 5 or 
        len(repeated_successful_steps) >= 2 or 
        (len(past_steps) >= 25 and unique_successful_steps <= 3)):
        print(f"🔄 [DEBUG] Detectado bucle o demasiados pasos. Pasos exitosos únicos: {unique_successful_steps}, Fallos repetidos: {repeated_failures}, Total pasos: {len(past_steps)}")
        
        # Obtener el mejor resultado disponible
        tool_result = ""
        if past_steps:
            # Buscar el último resultado exitoso
            for step, result in reversed(past_steps):
                if result and "EXITOSO" in result and len(result.strip()) > 10:
                    tool_result = result
                    break
            if not tool_result:
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
        print(f"🔄 [DEBUG] [RESPONSE] Respuesta final generada: {final_response}")
        return {"response": final_response}
    
    # Incluir contexto de conversación en el replanning
    input_with_context = original_input
    if session_id:
        context = memory.get_context_for_planning(session_id, max_messages=5)
        if context != "Esta es una nueva conversación.":
            input_with_context = f"{context}\n\nConsulta actual: {original_input}"
    
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
            print(f"🔄 [DEBUG] [RESPONSE] Respuesta final generada: {final_response}")
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
                print(f"🔄 [DEBUG] [RESPONSE] Respuesta final generada: {final_response}")
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
            print(f"🔄 [DEBUG] [RESPONSE] Respuesta final generada: {final_response}")
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
        print(f"🔄 [DEBUG] [RESPONSE] Respuesta final generada: {final_response}")
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
