import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

import memory

load_dotenv()

client = genai.Client()

persona_choice = st.sidebar.selectbox("Choose persona", ["Travel Planner", "Math Tutor", "Chef", "Custom"])

if persona_choice == "Custom":
    persona = st.sidebar.text_input("Custom persona", "Friendly Assistant")
else:
    persona = persona_choice

custom_prompt = st.sidebar.text_area("Define your chatbot's role")

system_instruction = custom_prompt if custom_prompt else f"You are a {persona}. Please assist the user with their queries."

def summarize_conversation(messages: list[dict]) -> tuple[str, int]:
    conversation_text = "\n".join(f"{msg['role']}: {msg['content']}" for msg in messages)
    summary_prompt = f"Summarize the following conversation concisely:\n{conversation_text}\nSummary:"

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=summary_prompt,
        config=types.GenerateContentConfig(max_output_tokens=750)
    )

    summarization_tokens = response.usage_metadata.total_token_count

    return response.text, summarization_tokens


if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assisstant", "content": "Yo what up boi, U need help?"}
    ]

if "context" not in st.session_state:
    st.session_state.context = list(st.session_state.messages)

if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0

if "summary" not in st.session_state:
    st.session_state.summary = ""

if "last_input_tokens" not in st.session_state:
    st.session_state.last_input_tokens = 0

if "last_output_tokens" not in st.session_state:
    st.session_state.last_output_tokens = 0

if "last_summarization_tokens" not in st.session_state:
    st.session_state.last_summarization_tokens = 0

with st.sidebar:
    st.header("📊 Conversation Summary")
    if st.session_state.summary:
        st.write(st.session_state.summary)
    else:
        st.info("Summary will appear here after a few messages.")

    st.header("💰 Token Usage")

    if st.session_state.last_input_tokens > 0:
        st.markdown("**Last Chat Interaction:**")
        st.markdown(f"- Chat Input (sent to API): {st.session_state.last_input_tokens} tokens")
        st.markdown(f"- Chat Output (from API): {st.session_state.last_output_tokens} tokens")
        st.markdown(f"- Chat Total: {st.session_state.last_input_tokens + st.session_state.last_output_tokens} tokens")

        if st.session_state.last_summarization_tokens > 0:
            st.markdown(f"- **Summarization API Call:** {st.session_state.last_summarization_tokens} tokens")
            st.caption("(Summarization uses gemini-3.1-flash-lite, which is much cheaper)")

        st.divider()

    st.markdown(f"**Cumulative Total:** {st.session_state.total_tokens} tokens")
    st.caption("Lower tokens = lower costs!")

    if st.button("🔄 Reset Conversation"):
        st.session_state.messages = [{"role": "assisstant", "content": "Yo what up boi, U need help?"}]
        st.session_state.context = list(st.session_state.messages)
        st.session_state.total_tokens = 0
        st.session_state.summary = ""
        st.session_state.last_input_tokens = 0
        st.session_state.last_output_tokens = 0
        st.session_state.last_summarization_tokens = 0
        st.rerun()

    st.header("🧠 Long-Term Memory")

    all_memories = memory.get_all_memories()

    if not all_memories:
        st.info("No memories stored yet.")
    else:
        for memory_type in memory.MEMORY_TYPES:
            type_memories = [m for m in all_memories if m["memory_type"] == memory_type]
            if not type_memories:
                continue

            st.subheader(memory_type.capitalize())
            for m in type_memories:
                with st.expander(m["content"][:50] + ("..." if len(m["content"]) > 50 else "")):
                    edited_content = st.text_area(
                        "Content", value=m["content"], key=f"mem_content_{m['id']}"
                    )
                    save_col, delete_col = st.columns(2)
                    with save_col:
                        if st.button("💾 Save", key=f"mem_save_{m['id']}"):
                            new_embedding = memory.embed_text(client, edited_content)
                            memory.update_memory(m["id"], memory_type, edited_content, new_embedding)
                            st.rerun()
                    with delete_col:
                        if st.button("🗑️ Delete", key=f"mem_delete_{m['id']}"):
                            memory.delete_memory(m["id"])
                            st.rerun()

    st.divider()
    confirm_wipe = st.checkbox("Confirm permanent deletion of ALL memories")
    if st.button("🗑️ Delete All Memories", disabled=not confirm_wipe):
        memory.delete_all_memories()
        st.rerun()

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Yo we can chat here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.context.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    st.session_state.last_summarization_tokens = 0

    user_message_count = sum(1 for msg in st.session_state.messages if msg['role'] == 'user')

    if user_message_count > 0 and user_message_count % 10 == 0:

        messages_to_summarize = st.session_state.context[:-1]
        current_user_message = st.session_state.context[-1]

        summary_text, summarization_tokens = summarize_conversation(messages_to_summarize)

        st.session_state["summary"] = summary_text
        st.session_state.last_summarization_tokens = summarization_tokens
        st.session_state.total_tokens += summarization_tokens

        st.session_state.context = [
            {"role": "system", "content": f"This is a summary of the conversation so far: {st.session_state['summary']}"},
            current_user_message
        ]

        memory.extract_memories(client, messages_to_summarize)

    gemini_history = [
        {
            "role": "model" if m["role"] == "assisstant" else "user",
            "parts": [{"text": m["content"]}],
        }
        for m in st.session_state.context
    ]

    relevant_memories = memory.retrieve_relevant_memories(client, prompt)
    full_system_instruction = system_instruction + memory.format_memories_for_prompt(relevant_memories)

    with st.chat_message("assisstant"):
        stream = client.models.generate_content_stream(
            model="gemini-3.6-flash",
            contents=gemini_history,
            config=types.GenerateContentConfig(system_instruction=full_system_instruction),
        )

        usage = {}

        def stream_text():
            for chunk in stream:
                if chunk.usage_metadata:
                    usage["metadata"] = chunk.usage_metadata
                yield chunk.text

        msg = st.write_stream(stream_text())

    if "metadata" in usage:
        st.session_state.last_input_tokens = usage["metadata"].prompt_token_count or 0
        st.session_state.last_output_tokens = usage["metadata"].candidates_token_count or 0
        st.session_state.total_tokens += st.session_state.last_input_tokens + st.session_state.last_output_tokens

    st.session_state.messages.append({"role": "assisstant", "content": msg})
    st.session_state.context.append({"role": "assisstant", "content": msg})
