import streamlit as st

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

from prompt import prompt, follow_up_prompt
from model import llm
from parser import LearningPath


# --------------------------------
# Page Configuration
# --------------------------------

st.set_page_config(
    page_title="Learning Path Generator",
    page_icon="🎯"
)


# --------------------------------
# Title
# --------------------------------

st.title("🎯 Learning Path Generator")

st.write(
    "Generate a structured learning roadmap and "
    "ask follow-up questions about it."
)


# --------------------------------
# Memory
# --------------------------------

if "chat_history" not in st.session_state:
    st.session_state.chat_history = InMemoryChatMessageHistory()

if "learning_path" not in st.session_state:
    st.session_state.learning_path = None

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []


# --------------------------------
# Chains
# --------------------------------

structured_llm = llm.with_structured_output(LearningPath)

roadmap_chain = prompt | structured_llm

follow_up_chain = follow_up_prompt | llm


# --------------------------------
# Sidebar
# --------------------------------

st.sidebar.title("🎯 Learning Path Generator")

st.sidebar.write(
    "Generate a learning roadmap and "
    "continue the conversation with follow-up questions."
)


if st.sidebar.button("Reset"):

    st.session_state.chat_history = InMemoryChatMessageHistory()

    st.session_state.learning_path = None

    st.session_state.chat_messages = []

    st.rerun()


# --------------------------------
# User Input
# --------------------------------

skill = st.text_input(
    "What skill do you want to learn?",
    placeholder="e.g. Python, Machine Learning, Generative AI"
)


level = st.selectbox(
    "Select your level",
    [
        "Beginner",
        "Intermediate",
        "Advanced"
    ]
)


# --------------------------------
# Generate Learning Path
# --------------------------------

if st.button("Generate Learning Path"):

    if not skill:

        st.warning("Please enter a skill.")

    else:

        with st.spinner("Generating your learning path..."):

            result = roadmap_chain.invoke({
                "skill": skill,
                "level": level
            })

        # Save roadmap
        st.session_state.learning_path = result

        # Reset previous conversation
        st.session_state.chat_history = InMemoryChatMessageHistory()

        st.session_state.chat_messages = []

        # Store initial interaction in memory
        st.session_state.chat_history.add_message(
            HumanMessage(
                content=f"Create a {level} learning roadmap for {skill}."
            )
        )

        st.session_state.chat_history.add_message(
            AIMessage(
                content=result.model_dump_json()
            )
        )

        st.success("Learning path generated!")


# --------------------------------
# Display Learning Path
# --------------------------------

if st.session_state.learning_path is not None:

    result = st.session_state.learning_path

    st.subheader("🎯 Learning Goal")

    st.write(
        result.learning_goal_summary
    )


    st.subheader("🗺️ Learning Roadmap")

    for i, stage in enumerate(
        result.learning_stages,
        start=1
    ):

        st.markdown(
            f"### Stage {i}: {stage.name}"
        )

        for topic in stage.topics:

            st.markdown(
                f"- {topic}"
            )


    # --------------------------------
    # Follow-up Conversation
    # --------------------------------

    st.subheader("💡 Ask About Your Learning Path")


    # Display previous messages
    for message in st.session_state.chat_messages:

        with st.chat_message(
            message["role"]
        ):

            st.write(
                message["content"]
            )


    # Chat input
    question = st.chat_input(
    "Ask a question about your learning path..."
    )

    if question:

        # Display user message
        with st.chat_message("user"):

            st.write(question)


        # Generate AI response
        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                response = follow_up_chain.invoke({
                    "history": st.session_state.chat_history.messages,
                    "question": question
                })

            st.write(response.content)


        # Save to LangChain memory
        st.session_state.chat_history.add_message(
            HumanMessage(
                content=question
            )
        )

        st.session_state.chat_history.add_message(
            AIMessage(
                content=response.content
            )
        )


        # Save for UI display
        st.session_state.chat_messages.append({
            "role": "user",
            "content": question
        })

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": response.content
        })




