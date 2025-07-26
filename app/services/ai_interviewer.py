import os
import openai
from typing import List, Dict, Any, Optional
from app.core.config import settings
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AIInterviewerService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.system_prompt = """You are an empathetic and skilled interviewer helping someone capture their life memories. Your role is to:

1. Ask thoughtful, open-ended questions that encourage detailed responses
2. Show genuine interest in their experiences and emotions
3. Remember details from previous parts of the conversation
4. Ask follow-up questions based on what they've shared
5. Help them explore deeper aspects of their memories
6. Be conversational and warm, not clinical or robotic
7. Focus on one memory or topic at a time to avoid overwhelming them
8. Capture factual details and specific information

Guidelines:
- Ask one question at a time
- Reference previous details they've shared to show you're listening
- If they mention people, places, or events, ask for more specific details about those
- Help them explore the factual aspects of their memories (who, what, when, where, why, how)
- If they seem to be done with a topic, suggest moving to a related memory or ask about a different time period
- Keep questions natural and conversational
- Avoid yes/no questions - prefer "how", "what", "when", "where", "why" questions
- Focus on getting concrete details and specific information
- Encourage them to share specific facts, dates, names, and descriptions

Your goal is to help them create detailed, factual memories that capture the specific details of what happened. The final summary will be based only on what they actually shared, so focus on getting concrete information rather than emotional interpretations."""

    async def start_interview(self, user_id: str, initial_context: Optional[str] = None) -> Dict[str, Any]:
        """Start a new interview session."""
        try:
            # Create initial conversation context
            conversation_context = []
            
            if initial_context:
                conversation_context.append({
                    "role": "user",
                    "content": f"I'd like to talk about: {initial_context}",
                    "timestamp": datetime.now().isoformat()
                })
            
            # Generate first question
            initial_question = "I'd love to help you capture your memories! Let's start with something that's meaningful to you. What's a memory or experience you'd like to share today?"
            
            # Add initial question to conversation context
            conversation_context.append({
                "role": "assistant",
                "content": initial_question,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "session_id": f"session_{user_id}_{datetime.now().isoformat()}",
                "conversation": conversation_context,
                "current_question": initial_question,
                "user_id": user_id,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error starting interview: {str(e)}")
            raise

    async def continue_interview(self, session_data: Dict[str, Any], user_response: str) -> Dict[str, Any]:
        """Continue the interview with a user response and generate the next question."""
        try:
            # Add user response to conversation
            conversation = session_data.get("conversation", [])
            conversation.append({
                "role": "user",
                "content": user_response,
                "timestamp": datetime.now().isoformat()
            })
            
            # Build messages for OpenAI
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(conversation)
            
            # Generate next question
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=200,
                temperature=0.7,
                stop=None
            )
            
            next_question = response.choices[0].message.content.strip()
            
            # Add AI response to conversation
            conversation.append({
                "role": "assistant",
                "content": next_question,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                **session_data,
                "conversation": conversation,
                "current_question": next_question,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error continuing interview: {str(e)}")
            raise

    async def end_interview(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """End the interview and generate a summary."""
        try:
            conversation = session_data.get("conversation", [])
            
            if not conversation:
                return {
                    **session_data,
                    "summary": "No conversation recorded.",
                    "ended_at": datetime.now().isoformat()
                }
            
            # Create summary prompt for factual, direct memory
            summary_prompt = f"""Based on this conversation, create a factual memory summary using ONLY the details and information the user actually shared. Do not add any embellishments, assumptions, or creative details. Focus on:

1. The specific memories and experiences they mentioned
2. The exact details, people, places, and dates they provided
3. Their actual words and descriptions
4. The facts they shared about what happened

IMPORTANT: 
- Use only information the user explicitly stated
- Do not make up or infer any details
- Do not add dramatic language or creative flourishes
- Keep it factual and direct
- Write in first person using their actual words when possible

Conversation:
{chr(10).join([f"{msg['role']}: {msg['content']}" for msg in conversation])}

Factual memory summary:"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": summary_prompt}],
                max_tokens=300,
                temperature=0.2  # Lower temperature for more factual, less creative responses
            )
            
            summary = response.choices[0].message.content.strip()
            
            return {
                **session_data,
                "summary": summary,
                "ended_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error ending interview: {str(e)}")
            raise

    async def suggest_memory_title(self, conversation: List[Dict[str, str]]) -> str:
        """Generate a suggested title for the memory based on the conversation."""
        try:
            if not conversation:
                return "New Memory"
            
            # Extract user responses
            user_responses = [msg["content"] for msg in conversation if msg["role"] == "user"]
            combined_content = " ".join(user_responses)
            
            title_prompt = f"""Based on this conversation content, generate a short, factual title (max 60 characters) for this memory. The title should reflect the specific memory or experience the user described, using only the details they actually mentioned:

{combined_content}

Factual title:"""
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": title_prompt}],
                max_tokens=50,
                temperature=0.7
            )
            
            title = response.choices[0].message.content.strip()
            # Clean up the title
            title = title.replace('"', '').replace("'", "").strip()
            
            return title if title else "New Memory"
            
        except Exception as e:
            logger.error(f"Error suggesting memory title: {str(e)}")
            return "New Memory" 