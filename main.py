from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

from model import create_model
from prompt import create_prompt, create_follow_up_prompt
from parser import create_parser


def generate_learning_path(
    skill: str,
    level: str,
    chat_history
):
    """
    Generate a structured learning path.
    """

    parser = create_parser()

    format_instructions = parser.get_format_instructions()

    prompt = create_prompt(format_instructions)

    model = create_model()

    chain = prompt | model | parser

    result = chain.invoke({
        "skill": skill,
        "level": level,
        "history": chat_history.messages,
        "format_instructions": format_instructions
    })

    return result


def answer_follow_up(
    question: str,
    chat_history
):
    """
    Answer a follow-up question using conversation history.
    """

    prompt = create_follow_up_prompt()

    model = create_model()

    chain = prompt | model

    response = chain.invoke({
        "history": chat_history.messages,
        "question": question
    })

    return response


def display_learning_path(
    result,
    skill: str,
    level: str
):
    """
    Display the generated learning roadmap.
    """

    print("\n" + "=" * 60)
    print(f"       {skill.upper()} LEARNING ROADMAP")
    print(f"              {level.upper()}")
    print("=" * 60)

    print("\nLEARNING STAGES")
    print("-" * 60)

    for i, stage in enumerate(
        result.learning_stages,
        start=1
    ):
        print(f"\nStage {i}: {stage.name}")

        for j, topic in enumerate(
            stage.topics,
            start=1
        ):
            print(f"   {j}. {topic}")

    print("\nLEARNING GOAL")
    print("-" * 60)

    print(result.learning_goal_summary)


def main():

    chat_history = InMemoryChatMessageHistory()

    skill = input(
        "What skill do you want to learn? : "
    ).strip()

    level = input(
        "What level do you want? "
        "(Beginner, Intermediate, Advanced): "
    ).strip()

    if not skill:
        print("Skill cannot be empty.")
        return

    if level.lower() not in [
        "beginner",
        "intermediate",
        "advanced"
    ]:
        print(
            "Please enter Beginner, Intermediate, "
            "or Advanced."
        )
        return

    # Generate learning roadmap
    result = generate_learning_path(
        skill,
        level,
        chat_history
    )

    # Display roadmap
    display_learning_path(
        result,
        skill,
        level
    )

    # Store initial user input in memory
    chat_history.add_message(
        HumanMessage(
            content=f"Skill: {skill}, Level: {level}"
        )
    )

    # Store generated roadmap in memory
    chat_history.add_message(
        AIMessage(
            content=result.model_dump_json()
        )
    )

    # Follow-up conversation
    while True:

        follow_up = input(
            "\nDo you have a follow-up question? (yes/no): "
        ).strip().lower()

        if follow_up == "no":
            print("\nThank you for using the Learning Roadmap Generator!")
            break

        if follow_up != "yes":
            print("Please enter yes or no.")
            continue

        question = input(
            "\nWhat would you like to know? "
        ).strip()

        if not question:
            print("Question cannot be empty.")
            continue

        # Get answer using conversation history
        response = answer_follow_up(
            question,
            chat_history
        )

        # Store follow-up question in memory
        chat_history.add_message(
            HumanMessage(
                content=question
            )
        )

        # Store AI answer in memory
        chat_history.add_message(
            AIMessage(
                content=response.content
            )
        )

        print("\nAI RESPONSE")
        print("-" * 60)
        print(response.content)


if __name__ == "__main__":
    main()
