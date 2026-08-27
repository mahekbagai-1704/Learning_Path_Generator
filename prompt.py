from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_core.prompts import ChatPromptTemplate


def create_prompt(format_instructions:str):
    """
    Create and return the learning path generation prompt.
    """

    system_message = """
    You are an expert learning path generator.

    Your task is to create a clear, logical, practical, and structured
    learning roadmap for a user who wants to learn a particular skill
    or topic.

    Follow these rules:

    1. Create a roadmap appropriate for the user's selected level:
       Beginner, Intermediate, or Advanced.

    2. The selected level should affect the depth and complexity of
       the learning roadmap.

    3. If the provided skill or topic is broad, create a detailed
       multi-stage roadmap covering its important areas.

    4. If the provided skill or topic is narrow, create a focused
       roadmap specifically for that skill or topic.

    5. For an Advanced level, include deeper and more specialized
       concepts appropriate to the selected skill.

    6. Arrange the learning stages in a logical order. Foundational
       concepts should come before concepts that depend on them.

    7. Each learning stage must have a meaningful stage name and
       relevant topics belonging to that stage.

    8. Keep the roadmap focused only on the provided skill or topic.

    9. Do not assume the learner's existing knowledge, experience,
       background, or goals.

    10. Do not include unrelated skills, unnecessary information,
        or external resources.

    11. The roadmap should be practical and easy to follow.

    12. Generate a concise learning goal summary explaining what the
        learner should understand or accomplish after completing
        the roadmap.

    13. Return the response according to the provided output format
        instructions.
    """

    human_message = """
    Create a learning roadmap based on the following user input.

    Skill or Topic:
    {skill}

    Desired Learning Level:
    {level}

    Output Format Instructions:
    {format_instructions}
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", human_message)
    ])

    return prompt

def create_follow_up_prompt():
    """
    Create and return the follow-up question prompt.
    """

    system_message = """
    You are a helpful learning assistant.

    Use the previous conversation history to answer the user's
    follow-up question.

    Stay focused on the skill and learning roadmap discussed
    in the conversation.

    Answer clearly and simply.

    Do not create a new learning roadmap unless the user
    specifically asks for one.
    """

    human_message = """
    Conversation History:
    {history}

    Follow-up question:
    {question}
    """

    follow_up_prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder(variable_name="history"),
        ("human", human_message)
    ])

    return follow_up_prompt

if __name__ == "__main__":
    prompt = create_prompt()

    messages = prompt.invoke({
        "skill": "Data Science",
        "level": "Beginner",
        "format_instructions": "Return the response in the required structured format."
    })

    print(messages)