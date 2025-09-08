import json
from io import StringIO
import streamlit as st
from models import Messages, FeedBack, RevisedResponse, Trajectory
from prompt_optimizer_controller import PromptOptimizer
from pydantic import ValidationError
from dotenv import load_dotenv
load_dotenv()

if 'add_trajectory' not in st.session_state:
    st.session_state.add_trajectory = False
    st.session_state.trajectories = Trajectory(messages=[])

if 'import_trajectory' not in st.session_state:
    st.session_state.import_trajectory = False


if st.button('Import Messages', use_container_width=True, disabled=st.session_state.import_trajectory):
    st.session_state.import_trajectory = True
    st.rerun()

if st.session_state.import_trajectory:
    _schema = json.dumps({
        "messages": [
            (
                [
                    {"role": "user", "content": "What is the capital of France?"},
                    {"role": "assistant", "content": "The capital of France is Paris."}
                ],
                {"comment": "Good response", "score": 0.9}
            ),
            (
                [
                    {"role": "user", "content": "What is 2 + 2?"},
                    {"role": "assistant", "content": "2 + 2 equals 4."}
                ],
                {"revised": "The sum of 2 and 2 is 4."}
            ),
            (
                [
                    {"role": "user", "content": "What is the capital of Germany?"},
                    {"role": "assistant", "content": "The capital of Germany is Berlin."}
                ],
                None
            )
        ]
    }, indent=4)
    example = st.expander("Example", expanded=False)
    example.write(f"```json\n{_schema}\n```")
    # Import using Json file
    uploaded_file = st.file_uploader("Choose a JSON file", type="json")
    if st.button("Upload", use_container_width=True):
        if uploaded_file is not None:
            # To convert to a string based IO:
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            # To read file as string:
            string_data = stringio.read()
            try:
                st.session_state.trajectories = Trajectory.model_validate_json(string_data)
                st.session_state.import_trajectory = False
                st.rerun()
            except ValidationError as e:
                st.error(f"Invalid JSON: {e}")
                st.markdown("### JSON Schema:")
                st.json(Trajectory.model_json_schema(), expanded=True)

st.markdown("---")
with st.empty().container():
    if len(st.session_state.trajectories.messages) > 0:
        st.markdown("#### Added Messages")
    for idx, trajectory in enumerate(st.session_state.trajectories.messages):
        col_traj, col_btn = st.columns([0.95, 0.05])
        with col_traj:
            for message in trajectory[0]:
                st.markdown(f"**{message.role.capitalize()}:** {message.content}")
            if trajectory[1]:
                if isinstance(trajectory[1], FeedBack):
                    st.markdown(f"*Feedback:* {trajectory[1].comment} (Score: {trajectory[1].score})")
                if isinstance(trajectory[1], RevisedResponse):
                    st.markdown(f"*Revised Response:* {trajectory[1].revised}")
        with col_btn:
            remove_traj_btn = st.button("❌", key=f"remove_traj_{idx}", help="Remove this trajectory")
            if remove_traj_btn:
                st.session_state.trajectories.messages.pop(idx)
                st.rerun()
        st.markdown("---")

if st.session_state.add_trajectory:
    with st.container(border=True):
        if "new_messages" not in st.session_state:
            st.session_state.new_messages = []
        placeholder = st.empty()
        col1, col2 = st.columns([0.3, 0.7], gap="medium")
        with col1:
            role = st.selectbox("Role", ["user", "assistant"], key="role_select")
        with col2:
            content = st.text_area("Content", key="content_area", height=5)
        if st.button("Add New Message"):
            if content:
                st.session_state.new_messages.append({"role": role, "content": content})
        st.markdown("---")
        st.write("Give either Feedback or a Revised Response:")
        col1, col2 = st.columns(2, gap="medium", border=True)
        with col1:
            st.write("**Feedback Section**")
            feedback_comments = st.text_input("Feedback Comments (optional)", key="feedback_comments")
            feedback_rating = st.slider("Feedback Rating (optional)", min_value=0.0, max_value=1.0, value=0.0, step=0.01, format="%.2f", key="feedback_rating")
        with col2:
            st.write("**Revised Response Section**")
            revised_response = st.text_area("Revised Response (optional)", key="revised_response", height=5)

        if st.session_state.new_messages:
            with placeholder.container():
                st.write("Messages to be added:")
                for idx, msg in enumerate(st.session_state.new_messages):
                    col_msg, col_btn = st.columns([0.9, 0.1])
                    with col_msg:
                        st.markdown(f"**{msg['role'].capitalize()}:** {msg['content']}")
                    with col_btn:
                        remove_btn = st.button("❌", key=f"remove_msg_{idx}", help="Remove this message")
                        if remove_btn:
                            st.session_state.new_messages.pop(idx)
                            st.rerun()

    if st.button("Submit Messages"):
        if st.session_state.new_messages:
            message_improvement = None
            if feedback_comments and not revised_response:
                message_improvement = FeedBack(comment=feedback_comments, score=feedback_rating)
            elif revised_response and not feedback_comments:
                message_improvement = RevisedResponse(revised=revised_response)
            elif feedback_comments and revised_response:
                st.error("Please provide either feedback or a revised response, not both.")
                st.rerun()
            messages_objs = [Messages(role=msg["role"], content=msg["content"]) for msg in st.session_state.new_messages]
            st.session_state.trajectories.messages.append((messages_objs, message_improvement))
            st.session_state.new_messages = []
            st.session_state.add_trajectory = False
            st.rerun()

if st.button("Add Messages", use_container_width=True, disabled=False if not st.session_state.add_trajectory else True):
    st.session_state.add_trajectory = True
    st.rerun()

st.markdown("---")
if st.button("Export Messages as JSON", use_container_width=True, disabled=len(st.session_state.trajectories.messages) == 0):
    json_string = st.session_state.trajectories.model_dump_json()
    st.download_button("Download JSON", json_string, "trajectories.json", "application/json")

st.markdown("---")
prompt = st.text_input("Your Prompt", key="input_prompt", placeholder="You are a planetary science expert", disabled=False if not st.session_state.add_trajectory else True)
text = st.empty()
if st.button("Generate Optimized Prompt", use_container_width=True,):
    text.empty()
    text.write("Generating....")
    prompt_optimizer = PromptOptimizer(trajectories=st.session_state.trajectories.model_dump().get("messages", []))
    st.session_state.generated_prompt = prompt_optimizer.optimize(prompt)

if "generated_prompt" not in st.session_state:
    st.session_state.generated_prompt = None


if st.session_state.generated_prompt:
    text.empty()
    text.markdown("### Generated Prompt")
    text.write(st.session_state.generated_prompt)
