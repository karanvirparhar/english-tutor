import streamlit as st
from datetime import datetime
import re
from dotenv import load_dotenv
import os
from prompts import CHAT_SYSTEM_PROMPT, GRADING_SYSTEM_PROMPT

load_dotenv()

DEFAULT_LLM_PROVIDER = "ollama"
DEFAULT_OLLAMA_MODEL = "gemma4:31b"


def get_config():
    return {
        "llm_provider": os.getenv("LLM_PROVIDER", DEFAULT_LLM_PROVIDER).lower(),
        "ollama_model": os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL),
    }

def get_llm_client():
    provider = get_config()["llm_provider"]
    if provider == "gemini":
        from google import genai as google_genai
        return google_genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    elif provider == "ollama":
        import ollama
        return ollama
    else:
        from openai import OpenAI
        return OpenAI()


def stream_llm_response(messages, placeholder):
    config = get_config()
    client = get_llm_client()
    reply = ""

    if config["llm_provider"] == "gemini":
        prompt_parts = []
        for message in messages:
            if message["role"] == "system":
                prompt_parts.append(message["content"])
            else:
                prompt_parts.append(f"{message['role']}: {message['content']}")
        response = client.models.generate_content_stream(
            model="gemini-flash-latest",
            contents="\n\n".join(prompt_parts)
        )
        for chunk in response:
            if chunk.text:
                reply += chunk.text
                placeholder.markdown(reply)
    elif config["llm_provider"] == "ollama":
        response = client.chat(
            model=config["ollama_model"],
            messages=messages,
            stream=True
        )
        for chunk in response:
            if chunk.message.content:
                reply += chunk.message.content
                placeholder.markdown(reply)
    else:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=300,
            temperature=0.7,
            stream=True
        )
        for chunk in response:
            reply += chunk.choices[0].delta.content or ""
            placeholder.markdown(reply)

    return reply


def initialize_app():
    st.set_page_config(
        page_title="9th Grade English Tutor",
        page_icon="📝",
        layout="wide"
    )

    session_defaults = {
        "submission_history": [],
        "current_feedback": None,
        "chat_history": [],
        "chat_session_active": False,
        "feedback_history": [],
    }
    for key, default_value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def get_llm_feedback(assignment_text, assignment_type):
    st.session_state.feedback_history.append({"role": "user", "content": f"Assignment Type: {assignment_type}\n\nStudent Writing:\n{assignment_text}"})

    placeholder = st.empty()
    messages = [
        {"role": "system", "content": GRADING_SYSTEM_PROMPT},
        {"role": "user", "content": f"Assignment Type: {assignment_type}\n\nStudent Writing:\n{assignment_text}"}
    ]
    reply = stream_llm_response(messages, placeholder)
    st.session_state.feedback_history.append({"role": "assistant", "content": reply})
    return reply

def get_chat_response(user_message, chat_history):
    messages = [{"role": "system", "content": CHAT_SYSTEM_PROMPT}]
    placeholder = st.empty()
    for msg in chat_history[-10:]:
        messages.append({"role": "user" if msg["is_user"] else "assistant", "content": msg["content"]})
    messages.append({"role": "user", "content": user_message})

    return stream_llm_response(
        messages + st.session_state.feedback_history[-10:],
        placeholder
    )

def parse_grade_from_feedback(feedback):
    """Extract letter grade and percentage from feedback"""
    grade_match = re.search(r'GRADE:\s*([A-F][+-]?)\s*\((\d+)%\)', feedback)
    if grade_match:
        return grade_match.group(1), int(grade_match.group(2))
    return "N/A", 0

def main():
    initialize_app()

    with st.sidebar:
        st.header("📚 9th Grade English Writing Tutor")
        
        page_icons = {
            "Chat with Tutor": "💬",
            "Submit Assignment": "📝", 
            "View History": "📊",
            "Writing Tips": "💡"
        }
        page_labels = {
            "Chat with Tutor": "Chat with Tutor",
            "Submit Assignment": "Submit Writing",
            "View History": "My Work",
            "Writing Tips": "Writing Tips"
        }
        
        selected_page = st.selectbox(
            "Navigation",
            ["Chat with Tutor", "Submit Assignment", "View History", "Writing Tips"],
            format_func=lambda x: f"{page_icons[x]} {page_labels[x]}"
        )
        page = selected_page

        st.markdown("---")
        
        st.markdown("### 🚀 Quick Tips")
        st.caption("💬 Ask me anything about writing!")
        st.caption("📝 Get feedback on your essays")
        st.caption("📊 Track your progress")

        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.write("I help 9th graders improve writing with feedback and grades based on CA standards.")

    if page == "Submit Assignment":
        show_submission_page()
    elif page == "Chat with Tutor":
        show_chat_page()
    elif page == "View History":
        show_history_page()
    else:
        show_tips_page()

def show_submission_page():
    st.header("📝 Submit Your Writing")

    assignment_type = st.selectbox(
        "📋 What kind of writing?",
        ["Argumentative (Making an argument)", "Informative (Explaining something)", "Narrative (Story)", "Other"]
    )

    assignment_title = st.text_input("📖 Title", placeholder="What's your assignment called?")

    st.markdown("### ✍️ Your Writing")
    assignment_text = st.text_area(
        "Paste or type your writing here:",
        height=300,
        placeholder="Start typing your assignment here...",
        help="Paste your essay, story, or writing assignment and I'll give you feedback!"
    )

    if assignment_text:
        word_count = len(assignment_text.split())
        st.caption(f"📊 Word count: {word_count}")

        if word_count < 50:
            st.warning("⚠️ That's pretty short! Try adding more details and examples.")
        elif word_count > 1000:
            st.info("ℹ️ That's a long piece! I'll focus on the most important feedback.")

    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        submit_button = st.button(
            "📤 Submit Assignment",
            type="primary",
            use_container_width=True,
            disabled=not (assignment_text and len(assignment_text.strip()) > 20)
        )
        st.caption("Each submission is saved to your history")

    if submit_button:
        if not assignment_text or len(assignment_text.strip()) < 20:
            st.error("❌ Please enter your writing (at least 20 characters).")
        else:
            with st.spinner("🤔 Looking at your writing..."):
                # Get feedback from LLM
                feedback = get_llm_feedback(assignment_text, assignment_type)

                # Parse grade
                letter_grade, percentage = parse_grade_from_feedback(feedback)

                # Store in session state
                submission = {
                    'timestamp': datetime.now(),
                    'assignment_title': assignment_title,
                    'assignment_type': assignment_type,
                    'assignment_text': assignment_text,
                    'feedback': feedback,
                    'letter_grade': letter_grade,
                    'percentage': percentage
                }

                st.session_state.submission_history.append(submission)
                st.session_state.current_feedback = submission

    # Display feedback if available
    if st.session_state.current_feedback:
        show_feedback_display(st.session_state.current_feedback)

def show_feedback_display(submission):
    st.markdown("---")
    st.header("📊 Your Grade")

    col1, col2, col3 = st.columns(3)

    with col1:
        grade_color = {
            'A': 'green', 'B': 'blue', 'C': 'orange', 'D': 'light red', 'F': 'red'
        }.get(submission['letter_grade'][0], 'gray')

        st.markdown(f"""
        <div style="text-align: center; padding: 20px; border-radius: 10px; background-color: {grade_color}; color: white;">
            <h1 style="margin: 0; font-size: 3em;">{submission['letter_grade']}</h1>
            <h3 style="margin: 0;">{submission['percentage']}%</h3>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.info(f"""
        **Title:** {submission['assignment_title']}
        **Type:** {submission['assignment_type']}
        **Date:** {submission['timestamp'].strftime('%m/%d/%Y at %I:%M %p')}
        """)

    with col3:
        word_count = len(submission['assignment_text'].split())
        st.metric("Words", word_count)

        if submission['percentage'] >= 90:
            st.success("🌟 Great job!")
        elif submission['percentage'] >= 80:
            st.success("👍 Good work!")
        elif submission['percentage'] >= 70:
            st.warning("📈 Good start!")
        else:
            st.error("💪 Keep trying!")

    st.markdown("### 📝 Feedback")

    tab1, tab2, tab3 = st.tabs(["📊 Grade Breakdown", "💡 Feedback", "📚 Vocabulary"])

    with tab1:
        # Extract and display grade breakdown
        feedback_lines = submission['feedback'].split('\n')
        breakdown_section = False
        breakdown_text = ""

        for line in feedback_lines:
            if "BREAKDOWN:" in line:
                breakdown_section = True
                continue
            elif breakdown_section and line.strip().startswith('•'):
                breakdown_text += line + "\n"
            elif breakdown_section and not line.strip().startswith('•') and line.strip():
                break

        if breakdown_text:
            st.code(breakdown_text, language=None)

        justification_match = re.search(r'JUSTIFICATION:\s*(.+?)(?=\n\n|\nSPECIFIC|$)', submission['feedback'], re.DOTALL)
        if justification_match:
            st.write(justification_match.group(1).strip())

    with tab2:
        feedback_match = re.search(r'SPECIFIC FEEDBACK:\s*(.+?)(?=\nVOCABULARY|$)', submission['feedback'], re.DOTALL)
        if feedback_match:
            st.write(feedback_match.group(1).strip())

        next_steps_match = re.search(r'NEXT STEPS:\s*(.+?)$', submission['feedback'], re.DOTALL)
        if next_steps_match:
            st.info(next_steps_match.group(1).strip())

    with tab3:
        vocab_match = re.search(r'VOCABULARY SUGGESTIONS:\s*(.+?)(?=\nNEXT STEPS|$)', submission['feedback'], re.DOTALL)
        if vocab_match:
            vocab_text = vocab_match.group(1).strip()
            vocab_lines = vocab_text.split('\n')
            for line in vocab_lines:
                if line.strip() and (line.strip().startswith(('1.', '2.', '3.', '4.', '5.'))):
                    st.write(f"• {line.strip()[2:].strip()}")

    if st.button("🔄 Revise & Submit Again", use_container_width=True):
        st.session_state.current_feedback = None
        st.rerun()

def show_history_page():
    st.header("📚 Assignment History")

    if not st.session_state.submission_history:
        st.info("📝 No assignments submitted yet. Go to 'Submit Assignment' to get started!")
        return

    # Summary stats
    total_assignments = len(st.session_state.submission_history)
    avg_grade = sum(s['percentage'] for s in st.session_state.submission_history) / total_assignments

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Assignments", total_assignments)
    with col2:
        st.metric("Average Grade", f"{avg_grade:.1f}%")
    with col3:
        latest_grade = st.session_state.submission_history[-1]['percentage']
        prev_grade = st.session_state.submission_history[-2]['percentage'] if len(st.session_state.submission_history) > 1 else latest_grade
        improvement = latest_grade - prev_grade
        st.metric("Latest Grade", f"{latest_grade}%", delta=f"{improvement:+.0f}%" if improvement != 0 else None)

    st.markdown("---")

    # Display history
    for i, submission in enumerate(reversed(st.session_state.submission_history)):
        with st.expander(f"📝 {submission['assignment_title']} - {submission['letter_grade']} ({submission['percentage']}%) - {submission['timestamp'].strftime('%m/%d/%Y')}"):
            col1, col2 = st.columns([2, 1])

            with col1:
                st.write(f"**Type:** {submission['assignment_type']}")
                st.write(f"**Word Count:** {len(submission['assignment_text'].split())}")

                # Show brief feedback
                justification_match = re.search(r'JUSTIFICATION:\s*(.+?)(?=\n\n|\nSPECIFIC|$)', submission['feedback'], re.DOTALL)
                if justification_match:
                    st.write(f"**Feedback:** {justification_match.group(1).strip()}")

            with col2:
                grade_color = {
                    'A': '🟢', 'B': '🔵', 'C': '🟠', 'D': '🔴', 'F': '🔴'
                }.get(submission['letter_grade'][0], '⚪')

                st.markdown(f"### {grade_color} {submission['letter_grade']}")
                st.markdown(f"**{submission['percentage']}%**")

def show_chat_page():
    st.header("💬 Chat with Your Writing Tutor")

    if not st.session_state.chat_history:
        st.markdown("""
        👋 **Hey! I'm your writing tutor.** Need help with homework or want feedback?

        Ask me anything:
        - ✍️ How to start an essay
        - 📚 Better vocabulary words  
        - ✍️ Grammar mistakes
        - 🎯 Story ideas

        Type your question below! 👇
        """)
        st.divider()

    for i, message in enumerate(st.session_state.chat_history):
        if message["is_user"]:
            with st.chat_message("user", avatar="👤"):
                st.markdown(message["content"])
                st.caption(f"You · {message['timestamp'].strftime('%I:%M %p')}")
        else:
            with st.chat_message("assistant", avatar="🎓"):
                st.markdown(message["content"])
                st.caption(f"Tutor · {message['timestamp'].strftime('%I:%M %p')}")

    if not st.session_state.chat_history:
        st.markdown("### 💡 Quick Questions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 How do I write a thesis?", use_container_width=True):
                handle_chat_message("How do I write a strong thesis statement?")
        with col2:
            if st.button("📚 5 vocabulary words", use_container_width=True):
                handle_chat_message("Give me 5 vocabulary words for my essay.")

        st.divider()

    user_input = st.chat_input("Ask me a writing question...")
    if user_input:
        handle_chat_message(user_input)

    if st.session_state.chat_history:
        st.divider()
        if st.button("🔄 Start Over", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.chat_session_active = False
            st.rerun()

def handle_chat_message(user_message):
    """Process user message and get tutor response"""
    if not user_message.strip():
        return

    # Add user message to history
    user_msg = {
        "content": user_message,
        "is_user": True,
        "timestamp": datetime.now()
    }
    st.session_state.chat_history.append(user_msg)
    st.session_state.chat_session_active = True

    # Get tutor response
    with st.spinner("🤔 Tutor is thinking..."):
        tutor_response = get_chat_response(user_message, st.session_state.chat_history)

    # Add tutor response to history
    tutor_msg = {
        "content": tutor_response,
        "is_user": False,
        "timestamp": datetime.now()
    }
    st.session_state.chat_history.append(tutor_msg)

    st.rerun()

def show_tips_page():
    st.header("💡 Writing Tips & Resources")

    # Writing tips tabs
    tab1, tab2, tab3, tab4 = st.tabs(["✍️ General Tips", "📝 Essay Structure", "📚 Vocabulary", "🔍 Revision"])

    with tab1:
        st.markdown("""
        ### 🎯 General Writing Tips

        **Before You Start:**
        - Read the assignment prompt carefully
        - Brainstorm ideas before writing
        - Create an outline with main points
        - Consider your audience and purpose

        **While Writing:**
        - Start with a strong hook
        - Use clear topic sentences
        - Support claims with evidence
        - Connect ideas with transitions

        **Remember:**
        - Write in your own voice
        - Use specific examples
        - Vary your sentence structure
        - Stay focused on your main argument
        """)

    with tab2:
        st.markdown("""
        ### 📐 Essay Structure Guide

        **Introduction (1 paragraph):**
        - Hook: Interesting fact, question, or quote
        - Background: Context for your topic
        - Thesis: Your main argument or claim

        **Body Paragraphs (2-4 paragraphs):**
        - Topic sentence: Main point of paragraph
        - Evidence: Facts, examples, quotes
        - Analysis: Explain how evidence supports your point
        - Transition: Connect to next paragraph

        **Conclusion (1 paragraph):**
        - Restate thesis in new words
        - Summarize main points
        - Call to action or final thought
        """)

    with tab3:
        st.markdown("""
        ### 📖 Vocabulary Building

        **Instead of "good":** excellent, outstanding, remarkable, impressive
        **Instead of "bad":** terrible, awful, inadequate, disappointing
        **Instead of "big":** enormous, massive, substantial, significant
        **Instead of "small":** tiny, minimal, insignificant, minute

        **Transition Words:**
        - **To add ideas:** furthermore, additionally, moreover, also
        - **To contrast:** however, nevertheless, on the other hand, yet
        - **To show cause:** therefore, consequently, as a result, thus
        - **To conclude:** ultimately, in conclusion, finally, overall
        """)

    with tab4:
        st.markdown("""
        ### 🔍 Revision Checklist

        **Content & Organization:**
        - [ ] Clear thesis statement
        - [ ] Logical paragraph order
        - [ ] Strong evidence and examples
        - [ ] Effective introduction and conclusion

        **Style & Clarity:**
        - [ ] Varied sentence structure
        - [ ] Appropriate word choice
        - [ ] Clear, concise writing
        - [ ] Consistent tone and voice

        **Grammar & Mechanics:**
        - [ ] Correct punctuation
        - [ ] Proper spelling
        - [ ] Subject-verb agreement
        - [ ] Correct capitalization

        **Final Check:**
        - [ ] Read aloud for flow
        - [ ] Check assignment requirements
        - [ ] Proofread one more time
        """)

if __name__ == "__main__":
    main()