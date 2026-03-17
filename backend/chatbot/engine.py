from database.chroma_db import db
from agents.definitions import llm_chatbot as llm
from langchain_core.messages import HumanMessage, SystemMessage

class ChatbotEngine:
    def __init__(self):
        self.llm = llm
        
    def generate_response(self, user_query: str, project_context: str = None) -> str:
        """
        Retrieves relevant historical risks and generates a conversational response using the local/remote LLM.
        """
        # Fetch semantic context
        search_results = db.search_similar_risks(user_query, n_results=3)
        context_str = ""
        
        if search_results and search_results.get('documents') and search_results['documents'][0]:
            context_str = "\n".join(search_results['documents'][0])
            
        system_prompt = (
            "You are a helpful AI assistant for Project Risk Management. "
            "Use the provided vector database context and project context to answer the user's question accurately. "
            "If you don't know the answer, say so. Do not invent facts."
        )
        
        user_prompt = f"Question: {user_query}\n\nProject Context:\n{project_context or 'None'}\n\nVector Database Knowledge:\n{context_str}"
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = self.llm.invoke(messages)
        return response.content

chatbot_engine = ChatbotEngine()
