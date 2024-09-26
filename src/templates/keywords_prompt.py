def generate_keywords_prompt(user_input, history):
    history_txt = "\n".join(history)

    return f"""
User Question: "{user_input}"

First, please check if user's question is follow-up question or not.
If you think it is follow-up question of your previous answers,
please also consider the conversation history to do the following.

Then please generate a list of relevant keywords based on the user's question.
The keywords should capture the main concepts and intent of the question.

Here is the conversation history:
{history_txt}

Keywords: Please answer just several keywords in one line. No need to explain details.
"""
