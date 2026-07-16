import os
import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import LLMChain

load_dotenv()


# ==========================================
# 1. Data Structures (Pydantic Models)
# ==========================================

class QuestionItem(BaseModel):
    """
    Data structure representing a generated interview question.
    """
    question_text: str = Field(
        description="The interview question phrased in Egyptian Tech-lead style (Arabic with English tech terms)."
    )
    expected_keywords: List[str] = Field(
        description="List of mandatory technical keywords (must be in English) expected in a correct answer."
    )
    difficulty: str = Field(
        description="Difficulty level of the question: 'Easy', 'Medium', or 'Hard'."
    )
    target_skill: str = Field(
        description="The primary technical skill being evaluated (e.g., 'FastAPI', 'System Design')."
    )


class AnswerEvaluation(BaseModel):
    """
    Data structure representing the AI's evaluation of a candidate's answer.
    """
    score: int = Field(description="Score from 0 to 100 based on keyword presence and technical accuracy.")
    is_acceptable: bool = Field(description="True if the answer meets the minimum technical requirements.")
    feedback: str = Field(description="Brief constructive feedback for internal HR report.")
    next_action: str = Field(description="'advance' to next topic, 'follow_up' for clarification, or 'terminate'.")


# ==========================================
# 2. Main Logic Class (OOP Architecture)
# ==========================================

class InterviewEngine:
    """
    The Brain of the Real-time Interview System.
    Handles dynamic question generation with Code-Switching and answer evaluation.
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: float = 0.4  # Slightly higher temp for natural, conversational tone
    ) -> None:
        self.model_name = model_name or os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
        self.temperature = temperature
        
        # Initialize Gemini LLM
        self.llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=self.temperature
        )
        
        # Initialize Prompt Chains
        self.question_chain = self._build_question_chain()
        self.eval_chain = self._build_evaluation_chain()

    def _build_question_chain(self) -> LLMChain:
        """
        Builds the LangChain prompt template for generating Egyptian Tech-Lead style questions.
        """
        template = (
            "You are a Senior Technical Lead at a top tech company in Egypt conducting a technical interview.\n"
            "Your task is to generate ONE technical interview question based on the candidate's skill and target difficulty.\n\n"
            "CRITICAL TONE AND LANGUAGE RULES:\n"
            "1. Use 'Code-Switching': Speak in natural Egyptian Arabic, but keep ALL technical terms, design patterns, and programming concepts in ENGLISH.\n"
            "2. Example style: 'إيه رأيك في الـ Dependency Injection؟ وبتتعامل إزاي مع الـ Memory Leak لما بيحصل عندك في الـ Production؟'\n"
            "3. Do NOT translate technical terms into Arabic (e.g., do NOT say 'حقن التبعية', say 'Dependency Injection').\n\n"
            "Input Parameters:\n"
            "- Target Skill: {skill}\n"
            "- Difficulty Level: {difficulty}\n"
            "- Job Role: {role}\n\n"
            "You MUST output ONLY a valid JSON object matching this exact schema, with NO markdown formatting:\n"
            "{{\n"
            "  \"question_text\": \"Question in Egyptian Arabic + English tech terms\",\n"
            "  \"expected_keywords\": [\"keyword1\", \"keyword2\", \"keyword3\"],\n"
            "  \"difficulty\": \"{difficulty}\",\n"
            "  \"target_skill\": \"{skill}\"\n"
            "}}\n"
        )
        
        prompt = PromptTemplate(
            input_variables=["skill", "difficulty", "role"],
            template=template
        )
        return LLMChain(llm=self.llm, prompt=prompt)

    def _build_evaluation_chain(self) -> LLMChain:
        """
        Builds the evaluation chain used as a fallback or deep-evaluator for candidate answers.
        """
        template = (
            "You are an AI Technical Interview Evaluator.\n"
            "Evaluate the candidate's spoken answer against the interview question and the mandatory expected keywords.\n\n"
            "Interview Question: {question}\n"
            "Mandatory Keywords (English): {keywords}\n"
            "Candidate Answer (Spoken Text via STT): {answer}\n\n"
            "Evaluation Criteria:\n"
            "1. Check if the candidate mentioned the concepts related to the mandatory keywords.\n"
            "2. Spoken STT might have minor spelling errors; evaluate based on technical accuracy and context.\n\n"
            "You MUST output ONLY a valid JSON object matching this exact schema:\n"
            "{{\n"
            "  \"score\": integer between 0 and 100,\n"
            "  \"is_acceptable\": boolean (true if score >= 60),\n"
            "  \"feedback\": \"short evaluation explanation in English for the HR report\",\n"
            "  \"next_action\": \"advance\" or \"follow_up\"\n"
            "}}\n"
        )
        prompt = PromptTemplate(
            input_variables=["question", "keywords", "answer"],
            template=template
        )
        return LLMChain(llm=self.llm, prompt=prompt)

    def generate_question(self, skill: str, role: str, difficulty: str = "Medium") -> QuestionItem:
        """
        Generates a tailored technical question using the Code-Switching persona.
        """
        try:
            response = self.question_chain.invoke({
                "skill": skill,
                "role": role,
                "difficulty": difficulty
            })
            
            raw_text = response.get("text", "").replace("```json", "").replace("```", "").strip()
            data = json.loads(raw_text)
            
            # Validate and return as structured Pydantic object
            return QuestionItem(**data)
            
        except Exception as e:
            print(f"Error generating question: {e}")
            # Fallback safe QuestionItem in case of API failure
            return QuestionItem(
                question_text=f"ممكن تكلمني أكتر عن خبرتك في الـ {skill} وإزاي بتستخدمه في مشاريعك؟",
                expected_keywords=[skill.lower(), "experience", "projects"],
                difficulty=difficulty,
                target_skill=skill
            )

    def evaluate_answer_llm(self, question_item: QuestionItem, candidate_answer: str) -> AnswerEvaluation:
        """
        Evaluates the answer using Gemini (This is the deep-level evaluation).
        In the next step, we will add the fast Keyword-Matching filter BEFORE calling this.
        """
        try:
            response = self.eval_chain.invoke({
                "question": question_item.question_text,
                "keywords": ", ".join(question_item.expected_keywords),
                "answer": candidate_answer
            })
            
            raw_text = response.get("text", "").replace("```json", "").replace("```", "").strip()
            data = json.loads(raw_text)
            
            return AnswerEvaluation(**data)
            
        except Exception as e:
            print(f"Error evaluating answer: {e}")
            return AnswerEvaluation(
                score=0,
                is_acceptable=False,
                feedback="Error processing evaluation.",
                next_action="follow_up"
            )