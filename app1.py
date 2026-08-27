import streamlit as st

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

from prompt import create_prompt, create_follow_up_prompt
from model import create_model
from parser import create_parser


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Learning Path Generator",
    page_icon="🎯",
    layout="centered"
)


# ==================================================
# SESSION STATE
# ==================================================

if "chat_history" not in st.session_state:

    st.session_state.chat_history = (
        InMemoryChatMessageHistory()
    )


if "learning_path" not in st.session_state:

    st.session_state.learning_path = None


if "chat_messages" not in st.session_state:

    st.session_state.chat_messages = []


# ==================================================
# GENERATE LEARNING PATH
# ==================================================

def generate_learning_path(
    skill: str,
    level: str
):
    """
    Generate a structured learning path.
    """

    parser = create_parser()

    format_instructions = (
        parser.get_format_instructions()
    )

    prompt = create_prompt(
        format_instructions
    )

    model = create_model()

    chain = prompt | model | parser

    result = chain.invoke({

        "skill": skill,

        "level": level,

        "format_instructions":
            format_instructions,

        "history":
            st.session_state
            .chat_history
            .messages

    })

    return result


# ==================================================
# ANSWER FOLLOW-UP
# ==================================================

def answer_follow_up(
    question: str
):
    """
    Answer a follow-up question using memory.
    """

    prompt = create_follow_up_prompt()

    model = create_model()

    chain = prompt | model

    response = chain.invoke({

        "history":
            st.session_state
            .chat_history
            .messages,

        "question":
            question

    })

    return response


# ==================================================
# SIDEBAR
# ==================================================

with st.sidebar:

    st.title("🎯 Learning Path")

    st.caption(
        "Generate a structured roadmap and "
        "get guidance along the way."
    )

    st.divider()

    st.caption(
        "Memory is maintained during the "
        "current session."
    )

    if st.button(
        "↻ Reset",
        use_container_width=True
    ):

        st.session_state.chat_history = (
            InMemoryChatMessageHistory()
        )

        st.session_state.learning_path = None

        st.session_state.chat_messages = []

        st.rerun()


# ==================================================
# HEADER
# ==================================================

c1, c2, c3 = st.columns(
    [0.5, 8, 0.5]
)

with c2:

    st.title(
        "🎯 Learning Path Generator"
    )


c1, c2, c3 = st.columns(
    [0.5, 2, 0.5]
)

with c2:

    st.caption(
        "A GenAI-powered learning path "
        "generator built with LangChain."
    )


st.markdown(
    "**Create a structured roadmap for any skill** "
    "**and learn step by step.**"
)


# ==================================================
# USER INPUT
# ==================================================

skill = st.text_input(

    "Skill or topic",

    placeholder=(
        "e.g. Python, Machine Learning, "
        "Generative AI"
    )
)


level = st.selectbox(

    "Learning level",

    [
        "Beginner",
        "Intermediate",
        "Advanced"
    ]
)


# ==================================================
# GENERATE LEARNING PATH
# ==================================================

if st.button(

    "🚀 Generate Learning Path",

    type="primary",

    use_container_width=True

):

    if not skill.strip():

        st.warning(
            "Please enter a skill or topic."
        )

    else:

        with st.spinner(
            "Creating your learning path..."
        ):

            result = generate_learning_path(
                skill,
                level
            )


        # ------------------------------------------
        # Store learning path
        # ------------------------------------------

        st.session_state.learning_path = result


        # ------------------------------------------
        # Reset memory for new roadmap
        # ------------------------------------------

        st.session_state.chat_history = (
            InMemoryChatMessageHistory()
        )

        st.session_state.chat_messages = []


        # ------------------------------------------
        # Store initial user request
        # ------------------------------------------

        st.session_state.chat_history.add_message(

            HumanMessage(

                content=(
                    f"Create a {level} learning "
                    f"roadmap for {skill}."
                )

            )

        )


        # ------------------------------------------
        # Store generated roadmap
        # ------------------------------------------

        st.session_state.chat_history.add_message(

            AIMessage(

                content=result.model_dump_json()

            )

        )


        st.success(
            "Your learning path is ready!"
        )


# ==================================================
# DISPLAY LEARNING PATH
# ==================================================

if st.session_state.learning_path is not None:

    result = st.session_state.learning_path

    st.divider()


    # ----------------------------------------------
    # LEARNING GOAL
    # ----------------------------------------------

    st.subheader(
        "🎯 Learning Goal"
    )

    st.info(
        result.learning_goal_summary
    )


    # ----------------------------------------------
    # ROADMAP
    # ----------------------------------------------

    st.subheader(
        "🗺️ Your Learning Roadmap"
    )


    for i, stage in enumerate(

        result.learning_stages,

        start=1

    ):

        st.markdown(
            f"### {i:02d}  {stage.name}"
        )


        for topic in stage.topics:

            st.markdown(
                f"　• {topic}"
            )


        # Connector between stages

        if i < len(
            result.learning_stages
        ):

            st.markdown(
                "　↓"
            )


    # ==================================================
    # FOLLOW-UP
    # ==================================================

    st.divider()

    st.subheader(
        "💡 Ask About Your Learning Path"
    )

    st.caption(
        "Have a question about your roadmap? "
        "Ask below."
    )


    # ----------------------------------------------
    # DISPLAY PREVIOUS QUESTIONS AND ANSWERS
    # ----------------------------------------------

    for message in (
        st.session_state.chat_messages
    ):

        with st.chat_message(
            message["role"]
        ):

            st.write(
                message["content"]
            )


    # ----------------------------------------------
    # NEW FOLLOW-UP QUESTION
    # ----------------------------------------------

    question = st.chat_input(
        "Ask a question about your learning path..."
    )


    if question:

        # ------------------------------------------
        # Display user message
        # ------------------------------------------

        with st.chat_message("user"):

            st.write(question)


        # ------------------------------------------
        # Generate AI response
        # ------------------------------------------

        with st.chat_message("assistant"):

            with st.spinner(
                "Thinking..."
            ):

                response = answer_follow_up(
                    question
                )


            st.write(
                response.content
            )


        # ------------------------------------------
        # Store question in memory
        # ------------------------------------------

        st.session_state.chat_history.add_message(

            HumanMessage(
                content=question
            )

        )


        # ------------------------------------------
        # Store AI response in memory
        # ------------------------------------------

        st.session_state.chat_history.add_message(

            AIMessage(
                content=response.content
            )

        )


        # ------------------------------------------
        # Store messages for UI
        # ------------------------------------------

        st.session_state.chat_messages.append({

            "role": "user",

            "content": question

        })


        st.session_state.chat_messages.append({

            "role": "assistant",

            "content": response.content

        })