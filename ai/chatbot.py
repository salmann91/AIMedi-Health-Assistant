import os
import sys
from typing import List, Dict

try:
    from langchain_groq import ChatGroq
    from langchain_core.messages import SystemMessage, HumanMessage
except Exception:  # pragma: no cover - defensive import fallback
    ChatGroq = None
    SystemMessage = HumanMessage = None

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from rag.retriever import MedicalRetriever
except Exception:  # pragma: no cover - defensive import fallback
    MedicalRetriever = None

from .prompts import CHAT_PROMPT


class HealthChatbot:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        self.llm = None
        self.retriever = None
        self.chat_history = []
        self.report_summary = ""
        self._available = False

        if not self.api_key or ChatGroq is None or SystemMessage is None or HumanMessage is None:
            return

        try:
            self.llm = ChatGroq(
                groq_api_key=self.api_key,
                model_name="llama-3.3-70b-versatile",
                temperature=0.5
            )
            if MedicalRetriever is not None:
                self.retriever = MedicalRetriever()
                self.retriever.initialize()
            self._available = True
        except Exception as e:
            print(f"Error initializing chatbot: {e}")
            self._available = False

    def set_report_context(self, summary: str):
        self.report_summary = summary

    def chat(self, question: str) -> str:
        """Process chat question and return response or a safe fallback."""
        if not question or not question.strip():
            return "Please ask a question."

        if not self._available or self.llm is None:
            return "I can help with general guidance, but the AI chat service is currently unavailable. Please review the report details directly."

        try:
            relevant_docs = []
            if self.retriever is not None:
                relevant_docs = self.retriever.retrieve(question, k=3)
            context = "\n\n".join([doc['text'] for doc in relevant_docs])

            chat_history_str = self._format_chat_history()

            prompt = CHAT_PROMPT.format(
                report_summary=self.report_summary,
                context=context,
                chat_history=chat_history_str,
                question=question
            )

            messages = [
                SystemMessage(content="You are a helpful medical AI assistant."),
                HumanMessage(content=prompt)
            ]

            response = self.llm.invoke(messages)
            answer = response.content

            self.chat_history.append({"role": "user", "content": question})
            self.chat_history.append({"role": "assistant", "content": answer})

            return answer
        except Exception as e:
            print(f"Error in chat: {e}")
            return "I apologize, but I encountered an error processing your question. Please try again."

    def _format_chat_history(self) -> str:
        if not self.chat_history:
            return "No previous conversation."

        formatted = []
        for msg in self.chat_history[-6:]:
            role = "Patient" if msg["role"] == "user" else "Assistant"
            formatted.append(f"{role}: {msg['content']}")

        return "\n".join(formatted)

    def clear_history(self):
        self.chat_history = []
