def generate_keywords_prompt(user_input, history):
    history_txt = "\n".join(history)

    ai_prompt = (
        "Based on the user's question, "
        "please provide only the relevant keywords "
        "for a database search without additional explanations. "
        "If you think the user's question is not related to the hotel database, "
        "please answer just one word 'NONE'. "
        "If you think it is follow-up question of your previous answers, "
        "please provide the relevant keywords based on the previous conversations. "
        "The keywords should capture the main concepts and intent of the question. "
        "If database query is not necessary, please answer just one word 'NONE'."
    )

    return f"""
{ai_prompt}

Conversation history:
{history_txt or "No history yet"}

User: {user_input}
Ai:
"""
