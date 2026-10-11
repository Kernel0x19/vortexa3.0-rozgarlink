"""
LangGraph-based Chatbot Agent with Ollama integration for RozgarLink.
"""

import re
from typing import AsyncGenerator, TypedDict, Annotated, List, Optional, Dict, Any
from datetime import datetime

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
try:
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.models import ChatMessageRecord, ChatThread, UserMemory, StudentProfile
from app.knowledge.hybrid_rag import HybridRAG

settings = get_settings()


class ChatState(TypedDict):
    """State for the chatbot conversation."""
    messages: Annotated[List[BaseMessage], add_messages]
    user_id: str
    user_profile: Optional[Dict[str, Any]]
    context: Optional[str]
    retrieved_docs: Optional[List[Dict[str, Any]]]
    long_term_memory: str
    db: Any
    student_profile: Optional[StudentProfile]


class ChatbotAgent:
    """
    LangGraph-based chatbot agent with Ollama integration.

    Features:
    - Local LLM inference via Ollama
    - RAG using existing vector search
    - Conversation memory with checkpointer
    - Student profile-aware responses
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
    ):
        # Use config settings with optional overrides
        self.model_name = model_name or settings.groq_model
        # Lower temperature for factual Q&A to reduce hallucination
        self.temperature = temperature if temperature is not None else 0.1

        # Groq replaces Ollama — zero infra, runs in Groq's cloud
        self.llm = None
        self._init_llm()

        # Initialize vector search for RAG
        self.vector_search_available = False
        try:
            self.rag = HybridRAG()
            self.vector_search_available = True
        except Exception:
            self.vector_search_available = False

        # Build the graph
        self.graph = self._build_graph()
        self.app = self.graph.compile()

    def _init_llm(self):
        """Initialize or re-initialize the LLM on demand."""
        try:
            from langchain_groq import ChatGroq
            if settings.groq_api_key:
                self.llm = ChatGroq(
                    model=self.model_name,
                    temperature=self.temperature,
                    groq_api_key=settings.groq_api_key,
                    streaming=True,
                )
                return self.llm
        except Exception:
            pass

        try:
            from langchain_community.chat_models import ChatOllama
            self.llm = ChatOllama(
                base_url=settings.ollama_base_url,
                model=settings.ollama_model,
                temperature=self.temperature,
            )
            return self.llm
        except Exception:
            pass
        return None

    def _get_llm(self):
        if self.llm is not None:
            return self.llm
        return self._init_llm()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state graph."""
        graph = StateGraph(ChatState)

        # Add nodes
        graph.add_node("retrieve_context", self._retrieve_context)
        graph.add_node("generate_response", self._generate_response)

        # Add edges
        graph.add_edge(START, "retrieve_context")
        graph.add_edge("retrieve_context", "generate_response")
        graph.add_edge("generate_response", END)

        return graph

    async def _retrieve_context(self, state: ChatState) -> ChatState:
        """Retrieve relevant context from vector store using RAG with two-stage approach."""
        user_id = state.get("user_id", "")
        messages = state.get("messages", [])

        # Get the latest human message
        latest_human_msg = None
        for msg in reversed(messages):
            if isinstance(msg, HumanMessage):
                latest_human_msg = msg
                break

        if not latest_human_msg:
            return state

        query = latest_human_msg.content

        # Do not attach old scholarship matches to acknowledgements or greetings.
        # With no retrieval context, the model can simply respond courteously.
        if self._is_social_message(query):
            state["context"] = ""
            state["retrieved_docs"] = []
            return state

        # Keep retrieval scoped to education opportunities. General questions are
        # answered by the LLM normally, without irrelevant scholarship cards.
        if not self._needs_opportunity_retrieval(query):
            state["context"] = ""
            state["retrieved_docs"] = []
            return state

        # Two-stage retrieval system based on query type
        if self.vector_search_available and query:
            try:
                # Stage 1: Brief list for eligibility questions
                if self._is_eligibility_list_query(query):
                    context_docs = self.rag.retrieve_for_profile(
                        state["db"], query, state.get("student_profile"), limit=3
                    )
                    # Format as BRIEF list (titles + amount only)
                    state["context"] = self._format_brief_list(context_docs)
                    state["retrieved_docs"] = context_docs
                
                # Stage 2: Full details for specific scholarship queries or follow-up questions
                else:
                    context_docs = self.rag.retrieve_for_profile(
                        state["db"], query, state.get("student_profile"), limit=8
                    )
                    # Format with FULL details
                    state["context"] = self._format_context(context_docs)
                    state["retrieved_docs"] = context_docs
                    
            except Exception as e:
                # Log error but continue without context
                print(f"RAG retrieval error: {e}")
                state["context"] = ""
                state["retrieved_docs"] = []

        return state

    @staticmethod
    def _is_eligibility_list_query(message: str) -> bool:
        """Detect queries asking for a list of eligible scholarships (Stage 1 queries)."""
        normalized = message.lower()
        list_patterns = [
            "which scholarship", "what scholarship", "scholarships am i eligible",
            "scholarships i can apply", "show me scholarship", "list scholarship",
            "eligible for which", "what can i apply", "recommend scholarship",
            "suggest scholarship", "scholarship for me", "find scholarship",
            # Hindi/Marathi
            "कौनसी शिष्यवृत्ती", "कौन सी स्कॉलरशिप", "योग्य", "पात्र",
            "शिष्यवृत्ती दाखवा", "स्कॉलरशिप बताओ"
        ]
        # Check if it's asking for a list (not asking about specific scholarship)
        is_list_query = any(pattern in normalized for pattern in list_patterns)
        # But exclude if asking about specific scholarship details
        detail_keywords = ["tell me about", "details about", "more about", "explain", "describe", "information about"]
        is_detail_query = any(keyword in normalized for keyword in detail_keywords)
        
        return is_list_query and not is_detail_query

    @staticmethod
    def _is_social_message(message: str) -> bool:
        """Detect social messages, greetings, and casual conversation that don't need scholarship retrieval."""
        normalized = re.sub(r"[^\w\s\u0900-\u097f]", "", message.lower()).strip()
        
        # Short greetings and acknowledgments
        social_messages = {
            "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
            "thanks", "thank you", "thankyou", "thx", "ty", "ok", "okay", "cool",
            "nice", "great", "awesome", "perfect", "got it", "understood",
            # Hindi/Marathi greetings
            "नमस्ते", "हैलो", "हाय", "धन्यवाद", "धन्यवाद तुम्हाला", "आभार", 
            "ठीक आहे", "समजले", "छान"
        }
        
        # Check for exact matches with short messages (under 6 words)
        words = normalized.split()
        if len(words) <= 5:
            if normalized in social_messages:
                return True
            # Check if it's just a greeting with extra words like "hi there" or "hello how are you"
            if any(greeting in words for greeting in ["hi", "hello", "hey", "नमस्ते", "हैलो"]):
                return True
        
        return False

    @staticmethod
    def _needs_opportunity_retrieval(message: str) -> bool:
        """Return True only for requests that need the opportunities knowledge base."""
        normalized = message.lower()
        opportunity_terms = (
            # Core terms
            "scholarship", "scholarships", "scheme", "schemes", "grant", "stipend",
            "fellowship", "internship", "placement", "student aid", "nsp",
            # Paraphrases that appear in real student queries
            "financial aid", "financial assistance", "bursary", "endowment",
            "research fellowship", "national fellowship",
            # Action words
            "apply", "application", "apply for", "how to apply",
            "portal", "documents required", "documents needed",
            "deadline", "last date", "amount", "how much",
            "income limit", "income ceiling", "income below",
            "who is eligible", "am i eligible", "eligibility criteria",
            "eligibility", "eligible", "income certificate", "caste certificate",
            "scholarship application", "scholarship form",
            # Programme identifiers
            "aicte", "ugc", "dst", "inspire", "icar", "nsp", "mahadbt",
            "post matric", "pre matric", "central sector",
            "swanath", "pragati", "saksham", "yasasvi", "maulana azad",
            "devnarayan", "nmms", "rajarshi",
            # Languages
            "शिष्यवृत्ती", "स्कॉलरशिप", "छात्रवृत्ति", "वजीफा", "इंटर्नशिप",
        )
        return any(term in normalized for term in opportunity_terms)

    def _format_brief_list(self, docs: List[Dict[str, Any]]) -> str:
        """Format retrieved documents as a BRIEF list (Stage 1: names + amount only)."""
        if not docs:
            return ""

        brief_parts = []
        for i, doc in enumerate(docs, 1):
            title = doc.get('title', 'Scholarship')
            
            # Extract only essential info
            entry = f"{i}. **{title}**"
            
            # Add amount range if available
            if doc.get("amount"):
                entry += f" - Up to ₹{doc['amount']:,}/year"
            elif doc.get("amount_max"):
                amount_max = doc.get("amount_max", 0)
                entry += f" - Up to ₹{amount_max:,}/year"
            
            brief_parts.append(entry)

        brief_list = "\n".join(brief_parts)
        
        # Add helpful hint for follow-up
        brief_list += "\n\n💡 Ask me about any specific scholarship for complete details (eligibility, documents, deadlines, etc.)"
        
        return brief_list

    def _format_context(self, docs: List[Dict[str, Any]]) -> str:
        """Format retrieved documents in a natural, readable way."""
        if not docs:
            return ""

        context_parts = []
        for i, doc in enumerate(docs, 1):
            title = doc.get('title', 'Scholarship')
            
            # Natural formatting
            entry = f"{i}. **{title}**\n"
            
            # Description
            description = doc.get('description', '')
            if description:
                if len(description) > 300:
                    description = description[:297] + "..."
                entry += f"   {description}\n"
            
            # Amount
            if doc.get("amount"):
                entry += f"   Amount: ₹{doc['amount']:,} per year\n"
            
            # Deadline
            if doc.get('deadline'):
                entry += f"   Deadline: {doc['deadline']}\n"
            
            # Application URL
            if doc.get("source_url"):
                entry += f"   Apply: {doc['source_url']}\n"
            
            context_parts.append(entry.strip())

        return "\n\n".join(context_parts)

    async def _generate_response(self, state: ChatState) -> ChatState:
        """Generate AI response using the LLM with context."""
        messages = state.get("messages", [])
        user_id = state.get("user_id", "")
        user_profile = state.get("user_profile", {})
        context = state.get("context", "")
        long_term_memory = state.get("long_term_memory", "")
        retrieved_docs = state.get("retrieved_docs", [])

        # Build system prompt with student context
        system_prompt = self._build_system_prompt(user_profile, context, long_term_memory)

        # Prepare messages for LLM
        llm_messages = [SystemMessage(content=system_prompt)]

        # Add conversation history (last 10 messages to avoid token limits)
        recent_messages = messages[-10:] if len(messages) > 10 else messages
        llm_messages.extend(recent_messages)

        # Generate response with NO token limit - let the model generate complete responses
        llm = self._get_llm()
        if not llm:
            error_msg = AIMessage(content="I am currently unable to connect to the language model. Please verify your Groq API key configuration.")
            state["messages"] = messages + [error_msg]
            return state

        try:
            response = await llm.ainvoke(llm_messages)
            state["messages"] = messages + [response]
        except Exception as e:
            error_msg = AIMessage(content=f"I apologize, but I encountered an error: {str(e)}. Please try again.")
            state["messages"] = messages + [error_msg]

        return state

    def _build_system_prompt(self, user_profile: Dict[str, Any], context: str, long_term_memory: str = "") -> str:
        """Build system prompt with strict adherence to retrieved context to improve faithfulness."""
        current_date = datetime.now().strftime("%B %d, %Y")

        # Build concise profile summary
        profile_parts = []
        if user_profile:
            if user_profile.get("stream"):
                profile_parts.append(f"Stream: {user_profile['stream']}")
            if user_profile.get("cgpa"):
                profile_parts.append(f"CGPA: {user_profile['cgpa']}")
            if user_profile.get("category"):
                profile_parts.append(f"Category: {user_profile['category']}")
            if user_profile.get("income_annual"):
                profile_parts.append(f"Income: ₹{user_profile['income_annual']:,}/year")
            if user_profile.get("state"):
                profile_parts.append(f"State: {user_profile['state']}")

        profile_str = ", ".join(profile_parts) if profile_parts else "No profile"

        # Include long-term memory
        memory_str = f"\n\nWhat I remember about you:\n{long_term_memory}" if long_term_memory else ""

        # Balanced system prompt - faithful yet helpful, with two-stage awareness
        system_prompt = f"""You are RozgarLink, a friendly and knowledgeable AI assistant helping Indian students find scholarships, internships, and educational opportunities.

Today: {current_date}
Student Profile: {profile_str}{memory_str}

AVAILABLE SCHOLARSHIP INFORMATION:
{context if context else "I don't have specific scholarship data for this query right now."}

RESPONSE GUIDELINES:

**Two-Stage Response System:**
1. **Brief List Queries** (e.g., "which scholarships am I eligible for?"):
   - Present the scholarship titles with amounts clearly
   - Keep response concise and scannable
   - Add a friendly prompt encouraging them to ask for details
   - Example: "Here are 3 scholarships you're eligible for: [list]. Want to know more about any of these?"

2. **Detail Queries** (e.g., "tell me about AICTE Pragati"):
   - Provide comprehensive information from the available data
   - Include eligibility criteria, amounts, deadlines, documents, and application process
   - Use the available scholarship information as your primary source
   - When providing specific details, reference the scholarship name

**Accuracy Requirements:**
- Don't invent specific amounts, dates, or criteria not in the available information
- When uncertain about details, clearly indicate the limitation
- Always distinguish between information from the available data vs general guidance

**Response Style:**
- Keep responses proportional to the question type
- Use clear formatting for scholarship details
- Be encouraging and supportive
- Answer in the same language as the student
- For brief lists: concise and scannable
- For details: comprehensive and well-organized

Remember: Be helpful and thorough with available information while being honest about limitations."""

        return system_prompt

    async def chat(
        self,
        db: Session,
        user_id: str,
        message: str,
        user_profile: Optional[Dict[str, Any]] = None,
        thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a chat message and return the AI response.

        Args:
            user_id: Unique identifier for the user
            message: User's message
            user_profile: Optional student profile for personalization
            thread_id: Optional thread ID for conversation continuity

        Returns:
            Dict containing response, retrieved docs, and thread info
        """
        thread = self._get_or_create_thread(db, user_id, thread_id, message)
        messages = self._recent_messages(db, thread.id)
        messages.append(HumanMessage(content=message))
        memory = self._long_term_memory(db, user_id)

        # Initial state
        initial_state: ChatState = {
            "messages": messages,
            "user_id": user_id,
            "user_profile": user_profile or {},
            "context": None,
            "retrieved_docs": None,
            "long_term_memory": memory,
            "db": db,
            "student_profile": db.query(StudentProfile).filter_by(user_id=user_id).first(),
        }

        # Run the graph
        result = await self.app.ainvoke(initial_state)

        # Get the AI response (last message)
        final_messages = result.get("messages", [])
        ai_response = None
        for msg in reversed(final_messages):
            if isinstance(msg, AIMessage):
                ai_response = msg.content
                break

        self._save_message_pair(db, thread, message, ai_response or "")
        self._remember(db, user_id, message)
        db.commit()

        return {
            "response": ai_response or "I apologize, but I couldn't generate a response. Please try again.",
            "retrieved_docs": result.get("retrieved_docs", []),
            "thread_id": thread.id,
            "message_count": db.query(ChatMessageRecord).filter_by(thread_id=thread.id).count(),
        }

    async def stream_chat(
        self,
        db: Session,
        user_id: str,
        message: str,
        user_profile: Optional[Dict[str, Any]] = None,
        thread_id: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream model tokens while persisting the completed turn and thread state."""
        thread = self._get_or_create_thread(db, user_id, thread_id, message)
        messages = self._recent_messages(db, thread.id)
        messages.append(HumanMessage(content=message))
        state: ChatState = {
            "messages": messages,
            "user_id": user_id,
            "user_profile": user_profile or {},
            "context": None,
            "retrieved_docs": None,
            "long_term_memory": self._long_term_memory(db, user_id),
            "db": db,
            "student_profile": db.query(StudentProfile).filter_by(user_id=user_id).first(),
        }
        state = await self._retrieve_context(state)
        prompt = self._build_system_prompt(state["user_profile"], state.get("context") or "", state["long_term_memory"])
        
        # Use self.llm with NO token limit for complete responses
        llm = self._get_llm()
        if not llm:
            yield {"type": "token", "content": "I am currently unable to connect to the language model. Please verify your Groq API key configuration."}
            yield {
                "type": "done",
                "thread_id": thread.id,
                "retrieved_docs": state.get("retrieved_docs") or [],
                "message_count": db.query(ChatMessageRecord).filter_by(thread_id=thread.id).count(),
            }
            return

        response_text = ""
        try:
            async for chunk in llm.astream([SystemMessage(content=prompt), *messages]):
                token = chunk.content if isinstance(chunk.content, str) else ""
                if token:
                    response_text += token
                    yield {"type": "token", "content": token}
            self._save_message_pair(db, thread, message, response_text)
            self._remember(db, user_id, message)
            db.commit()
            yield {
                "type": "done",
                "thread_id": thread.id,
                "retrieved_docs": state.get("retrieved_docs") or [],
                "message_count": db.query(ChatMessageRecord).filter_by(thread_id=thread.id).count(),
            }
        except Exception as exc:
            db.rollback()
            yield {"type": "error", "detail": str(exc)}

    def _get_or_create_thread(self, db: Session, user_id: str, thread_id: Optional[str], first_message: str) -> ChatThread:
        thread = db.query(ChatThread).filter_by(id=thread_id, user_id=user_id).first() if thread_id else None
        if thread:
            return thread
        title = " ".join(first_message.split())[:80] or "New conversation"
        thread = ChatThread(user_id=user_id, title=title)
        db.add(thread)
        db.flush()
        return thread

    def _recent_messages(self, db: Session, thread_id: str, limit: int = 12) -> List[BaseMessage]:
        records = db.query(ChatMessageRecord).filter_by(thread_id=thread_id).order_by(ChatMessageRecord.created_at.desc()).limit(limit).all()
        messages: List[BaseMessage] = []
        for record in reversed(records):
            messages.append(HumanMessage(content=record.content) if record.role == "user" else AIMessage(content=record.content))
        return messages

    def _long_term_memory(self, db: Session, user_id: str) -> str:
        memories = db.query(UserMemory).filter_by(user_id=user_id).order_by(UserMemory.updated_at.desc()).limit(8).all()
        return "\n".join(f"- {memory.content}" for memory in reversed(memories))

    def _remember(self, db: Session, user_id: str, message: str) -> None:
        """Persist explicit preferences/facts without storing every chat message as memory."""
        match = re.search(r"(?:remember that|remember|i prefer|my goal is)\s+(.+)", message, re.IGNORECASE)
        if not match:
            return
        content = match.group(1).strip().rstrip(".")[:500]
        if content and not db.query(UserMemory).filter_by(user_id=user_id, content=content).first():
            db.add(UserMemory(user_id=user_id, content=content, source="chat"))

    def _save_message_pair(self, db: Session, thread: ChatThread, user_message: str, assistant_message: str) -> None:
        db.add_all([
            ChatMessageRecord(thread_id=thread.id, role="user", content=user_message),
            ChatMessageRecord(thread_id=thread.id, role="assistant", content=assistant_message),
        ])
        thread.updated_at = datetime.utcnow()

    async def get_conversation_history(self, db: Session, user_id: str, thread_id: str) -> List[Dict[str, Any]]:
        thread = db.query(ChatThread).filter_by(id=thread_id, user_id=user_id).first()
        if not thread:
            return []
        records = db.query(ChatMessageRecord).filter_by(thread_id=thread.id).order_by(ChatMessageRecord.created_at).all()
        return [{"role": record.role, "content": record.content} for record in records]

    async def clear_conversation(self, db: Session, user_id: str, thread_id: str) -> bool:
        thread = db.query(ChatThread).filter_by(id=thread_id, user_id=user_id).first()
        if not thread:
            return False
        db.query(ChatMessageRecord).filter_by(thread_id=thread.id).delete()
        db.commit()
        return True

    def list_threads(self, db: Session, user_id: str) -> List[Dict[str, Any]]:
        threads = db.query(ChatThread).filter_by(user_id=user_id).order_by(ChatThread.updated_at.desc()).all()
        return [{"id": thread.id, "title": thread.title, "updated_at": thread.updated_at.isoformat()} for thread in threads]


# Singleton instance
_chatbot_agent: Optional[ChatbotAgent] = None


def get_chatbot_agent() -> ChatbotAgent:
    """Get or create the singleton chatbot agent instance."""
    global _chatbot_agent
    if _chatbot_agent is None:
        _chatbot_agent = ChatbotAgent()
    return _chatbot_agent


# Convenience function for direct use
async def chat_with_bot(
    db: Session,
    user_id: str,
    message: str,
    user_profile: Optional[Dict[str, Any]] = None,
    thread_id: Optional[str] = None
) -> Dict[str, Any]:
    """Convenience function to chat with the bot."""
    agent = get_chatbot_agent()
    return await agent.chat(db, user_id, message, user_profile, thread_id)


# ---------------------------------------------------------------------------
# Eval-only function — NOT used by any production endpoint.
# Returns both the answer and the raw retrieved context chunks so that
# offline evaluation frameworks (Ragas, DeepEval) can score them.
# The production chat API shape is left completely unchanged.
# ---------------------------------------------------------------------------

async def query_scholarship_with_context(question: str) -> Dict[str, Any]:
    """
    Stateless eval entry-point for the Scholarship RAG pipeline.

    Runs a single question through retrieval + generation and returns:
        {
            "answer":   str,          # generated response
            "contexts": list[str],    # raw text of each retrieved chunk
        }

    Uses its own short-lived DB session (same pattern as run_ingestion) so
    it can be called from eval scripts without an active HTTP request context.
    Does NOT persist any chat history or memory.
    """
    from app.db.session import SessionLocal  # imported here to avoid circular imports at module load
    from app.db.models import Opportunity as Opp

    db = SessionLocal()
    try:
        agent = ChatbotAgent()

        # --- Retrieval (bypass eligibility filter for eval) ---
        # retrieve_for_profile filters out docs when profile=None because
        # evaluate_eligibility returns eligible=False for anonymous users.
        # For eval we always want real context, so we use semantic_search directly.
        # Increased from 5 to 8 for better recall
        candidates = agent.rag.semantic_search(question, limit=8, category="scholarship")
        ids = [item["opportunity_id"] for item in candidates if item.get("opportunity_id")]
        opportunities: Dict[str, Any] = {
            opp.id: opp for opp in db.query(Opp).filter(
                Opp.id.in_(ids), Opp.is_active.is_(True)
            ).all()
        } if ids else {}

        retrieved_docs: List[Dict[str, Any]] = []
        for candidate in candidates:
            opp = opportunities.get(candidate.get("opportunity_id"))
            if not opp:
                continue
            retrieved_docs.append({
                "opportunity_id": opp.id,
                "title": opp.title,
                "description": opp.description or "",
                "category": opp.category.value if opp.category else "scholarship",
                "relevance_score": candidate["score"],
                "deadline": opp.deadline.isoformat() if opp.deadline else None,
                "amount": opp.amount_max or opp.amount_min,
            })

        # Build raw context strings for Ragas
        contexts: List[str] = []
        for doc in retrieved_docs:
            parts = [doc.get("title", "")]
            if doc.get("description"):
                parts.append(doc["description"])
            if doc.get("deadline"):
                parts.append(f"Deadline: {doc['deadline']}")
            if doc.get("amount"):
                parts.append(f"Amount: {doc['amount']}")
            contexts.append(" | ".join(p for p in parts if p))

        if not contexts:
            contexts = ["No context retrieved."]

        # --- Natural context string for generation ---
        context_parts = []
        for i, doc in enumerate(retrieved_docs, 1):
            title = doc.get('title', 'Scholarship')
            
            entry = f"{i}. **{title}**\n"
            
            # Description
            description = doc.get('description', '')
            if description:
                if len(description) > 300:
                    description = description[:297] + "..."
                entry += f"   {description}\n"
            
            # Amount
            if doc.get("amount"):
                entry += f"   Amount: ₹{doc['amount']:,} per year\n"
            
            # Deadline
            if doc.get('deadline'):
                entry += f"   Deadline: {doc['deadline']}\n"
            
            context_parts.append(entry.strip())
            
        context_str = "\n\n".join(context_parts) if retrieved_docs else ""

        # --- Generation ---
        system_prompt = agent._build_system_prompt({}, context_str, "")
        llm_messages = [SystemMessage(content=system_prompt), HumanMessage(content=question)]
        try:
            response = await agent.llm.ainvoke(llm_messages)
            answer: str = response.content if isinstance(response.content, str) else str(response.content)
        except Exception as exc:
            answer = f"[eval error: {exc}]"

        return {"answer": answer, "contexts": contexts}
    finally:
        db.close()


