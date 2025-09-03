import streamlit as st
from models import Messages, FeedBack, RevisedResponse, Trajectory
from prompt_optimizer_controller import PromptOptimizer

if 'add_trajectory' not in st.session_state:
    st.session_state.add_trajectory = False
    st.session_state.trajectories = Trajectory(turns=[])

with st.empty().container():
    if len(st.session_state.trajectories["turns"]) > 0:
        st.markdown("#### Added Trajectories")
    for trajectory in st.session_state.trajectories["turns"]:
        for message in trajectory[0]:
            st.markdown(f"**{message['role'].capitalize()}:** {message['content']}")
        if trajectory[1]:
            if trajectory[1].get("comment"):
                st.markdown(f"*Feedback:* {trajectory[1]['comment']} (Score: {trajectory[1]['score']})")
            if trajectory[1].get("revised"):
                st.markdown(f"*Revised Response:* {trajectory[1]['revised']}")
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
            st.session_state.trajectories["turns"].append((messages_objs, message_improvement))
            st.session_state.new_messages = []
            st.session_state.add_trajectory = False
            st.rerun()

if st.button("Add Trajectory", use_container_width=True, disabled=False if not st.session_state.add_trajectory else True):
    st.session_state.add_trajectory = True
    st.rerun()

prompt = st.text_input("Input Prompt", key="input_prompt", placeholder="You are a planetary science expert", disabled=False if not st.session_state.add_trajectory else True)
if st.button("Generate Prompt", use_container_width=True, disabled=False if not st.session_state.add_trajectory else True):
    st.session_state.generated_prompt = prompt

if "generated_prompt" not in st.session_state:
    st.session_state.generated_prompt = None

if st.session_state.generated_prompt:
    st.markdown("### Generated Prompt")
    text = st.empty()
    text.write("Generating....")
    prompt_optimizer = PromptOptimizer(trajectories=st.session_state.trajectories["turns"])
    resp = prompt_optimizer.optimize(st.session_state.generated_prompt)
    text.empty()
    text.write(resp)
