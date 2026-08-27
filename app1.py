import streamlit as st

from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    ListFlowable,
    ListItem
)

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

from prompt import create_prompt, create_follow_up_prompt
from model import create_model
from parser import create_parser


st.set_page_config(
    page_title="Learning Path Generator",
    page_icon="🎯",
    layout="centered"
)


st.markdown(
    """
    <style>

    .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    h1 {
        text-align: center;
        color: #5B21B6 !important;
        font-size: 2.7rem !important;
        font-weight: 700 !important;
        letter-spacing: -1px;
        margin-bottom: 0.3rem !important;
    }

    h2, h3 {
        color: #5B21B6 !important;
    }

    .subtitle {
        text-align: center;
        color: #7C3AED;
        font-size: 1rem;
        margin-bottom: 1.2rem;
    }

    .intro {
        text-align: center;
        color: #4B5563;
        margin-bottom: 1.8rem;
    }

    button[kind="primary"] {
        background: linear-gradient(
            90deg,
            #7C3AED,
            #9333EA
        ) !important;

        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }

    button[kind="primary"]:hover {
        background: linear-gradient(
            90deg,
            #6D28D9,
            #7E22CE
        ) !important;

        box-shadow: 0 5px 15px rgba(124, 58, 237, 0.25);
    }

    div[data-baseweb="input"] {
        border-radius: 10px;
    }

    div[data-baseweb="select"] {
        border-radius: 10px;
    }

    div[data-testid="stAlert"] {
        border-radius: 10px;
    }

    section[data-testid="stSidebar"] {
        border-right: 1px solid #E9D5FF;
    }

    section[data-testid="stSidebar"] h1 {
        text-align: left;
        font-size: 1.6rem !important;
    }

    </style>
    """,
    unsafe_allow_html=True
)


if "chat_history" not in st.session_state:
    st.session_state.chat_history = InMemoryChatMessageHistory()

if "learning_path" not in st.session_state:
    st.session_state.learning_path = None

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []


def generate_learning_path(skill: str, level: str):

    parser = create_parser()

    format_instructions = parser.get_format_instructions()

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
            st.session_state.chat_history.messages
    })

    return result


def answer_follow_up(question: str):

    prompt = create_follow_up_prompt()

    model = create_model()

    chain = prompt | model

    response = chain.invoke({

        "history":
            st.session_state.chat_history.messages,

        "question":
            question
    })

    return response


def create_pdf(result, skill, level):

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontSize=22,
        textColor=colors.HexColor("#5B21B6"),
        alignment=TA_CENTER,
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        "SubtitleStyle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#6B7280"),
        alignment=TA_CENTER,
        spaceAfter=20
    )

    heading_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontSize=15,
        textColor=colors.HexColor("#5B21B6"),
        spaceBefore=12,
        spaceAfter=8
    )

    stage_style = ParagraphStyle(
        "StageStyle",
        parent=styles["Heading3"],
        fontSize=12,
        textColor=colors.HexColor("#7C3AED"),
        spaceBefore=10,
        spaceAfter=5
    )

    story = []

    story.append(
        Paragraph(
            "Learning Path Generator",
            title_style
        )
    )

    story.append(
        Paragraph(
            f"{skill} | {level}",
            subtitle_style
        )
    )

    story.append(
        Paragraph(
            "Learning Goal",
            heading_style
        )
    )

    story.append(
        Paragraph(
            result.learning_goal_summary,
            styles["BodyText"]
        )
    )

    story.append(
        Spacer(1, 15)
    )

    story.append(
        Paragraph(
            "Learning Roadmap",
            heading_style
        )
    )

    for i, stage in enumerate(
        result.learning_stages,
        start=1
    ):

        story.append(
            Paragraph(
                f"{i:02d}. {stage.name}",
                stage_style
            )
        )

        topics = []

        for topic in stage.topics:

            topics.append(
                ListItem(
                    Paragraph(
                        topic,
                        styles["BodyText"]
                    )
                )
            )

        story.append(
            ListFlowable(
                topics,
                bulletType="bullet",
                leftIndent=20
            )
        )

    document.build(story)

    buffer.seek(0)

    return buffer.getvalue()


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


st.title(
    "🎯 Learning Path Generator"
)

st.markdown(
    """
    <div class="subtitle">
        A GenAI-powered learning path generator built with LangChain.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="intro">
        Turn any skill into a clear, structured learning journey.
    </div>
    """,
    unsafe_allow_html=True
)


skill = st.text_input(
    "Skill or topic",
    placeholder=(
        "e.g. Python, Machine Learning, Generative AI"
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


button_left, button_center, button_right = st.columns(
    [1, 2, 1]
)

with button_center:

    generate_clicked = st.button(
        "🚀 Generate Learning Path",
        type="primary",
        use_container_width=True
    )


if generate_clicked:

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

        st.session_state.learning_path = result

        st.session_state.chat_history = (
            InMemoryChatMessageHistory()
        )

        st.session_state.chat_messages = []

        st.session_state.chat_history.add_message(
            HumanMessage(
                content=(
                    f"Create a {level} learning "
                    f"roadmap for {skill}."
                )
            )
        )

        st.session_state.chat_history.add_message(
            AIMessage(
                content=result.model_dump_json()
            )
        )

        st.success(
            "Your learning path is ready!"
        )


if st.session_state.learning_path is not None:

    result = st.session_state.learning_path

    st.divider()

    st.subheader(
        "🎯 Learning Goal"
    )

    st.info(
        result.learning_goal_summary
    )

    st.subheader(
        "🗺️ Your Learning Journey"
    )

    total_stages = len(
        result.learning_stages
    )

    total_topics = sum(
        len(stage.topics)
        for stage in result.learning_stages
    )

    st.caption(
        f"{skill} · {level} · "
        f"{total_stages} stages · "
        f"{total_topics} topics"
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

        if i < total_stages:

            st.markdown(
                "　↓"
            )


    pdf_file = create_pdf(
        result,
        skill,
        level
    )

    st.download_button(
        label="📥 Download Learning Path as PDF",
        data=pdf_file,
        file_name=(
            f"{skill.replace(' ', '_')}_Learning_Path.pdf"
        ),
        mime="application/pdf",
        use_container_width=True
    )


    st.divider()

    st.subheader(
        "💡 Ask About Your Learning Path"
    )

    st.caption(
        "Have a question about your roadmap? "
        "Ask below."
    )

    for message in st.session_state.chat_messages:

        with st.chat_message(
            message["role"]
        ):

            st.write(
                message["content"]
            )

    question = st.chat_input(
        "Ask a question about your learning path..."
    )

    if question:

        with st.chat_message("user"):

            st.write(
                question
            )

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

        st.session_state.chat_messages.append({
            "role": "user",
            "content": question
        })

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": response.content
        })