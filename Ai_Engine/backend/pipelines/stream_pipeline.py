import os
import json
import time
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
class InterviewState(BaseModel):
    """
    Tracks the current state of the interview for a specific candidate.
    """
    current_question: Optional[QuestionItem] = None
    accumulated_answer: str = ""
    question_start_time: float = 0.0
    history: List[Dict[str, Any]] = [] #The list that will compile the entire interview for the final evaluation.

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
        temperature: float = 0.4 
        ) -> None:
        self.model_name = model_name or os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
        self.temperature = temperature
        self.llm = ChatGoogleGenerativeAI(model=self.model_name, temperature=self.temperature)
        self.question_chain = self._build_question_chain()
        self.eval_chain = self._build_evaluation_chain()
        
        # New: Initialize the state
        self.state = InterviewState()

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
    def fast_keyword_match(
        self, 
        candidate_answer: str, 
        expected_keywords: List[str], 
        threshold: float = 0.7
    ) -> Optional[Dict[str, Any]]:
        """
        Fast O(N) keyword matching filter to bypass LLM evaluation if the answer is clearly correct.
        """
        if not expected_keywords:
            return None
            
        answer_lower = candidate_answer.lower()
        matched_words = []
        
        for kw in expected_keywords:
            if kw.lower() in answer_lower:
                matched_words.append(kw)

        hit_ratio = len(matched_words) / len(expected_keywords)

        if hit_ratio >= threshold:
            score = int(hit_ratio * 100)
            return {
                "score": score,
                "is_acceptable": True,
                "feedback": f"Auto-approved. Matched key concepts: {', '.join(matched_words)}",
                "next_action": "advance"
            }
        
        return None

    def process_transcript_chunk(self, transcript_chunk: str) -> Optional[Dict[str, Any]]:
        """
        Receives a chunk of speech, adds it to the buffer, and applies the One-Strike rule.
        """
        self.state.accumulated_answer += " " + transcript_chunk.strip()
        
        if not self.state.current_question:
            return None
            
        fast_eval = self.fast_keyword_match(
            candidate_answer=self.state.accumulated_answer,
            expected_keywords=self.state.current_question.expected_keywords,
            threshold=0.8
        )
        
        if fast_eval:
            self.state.accumulated_answer = ""
            return fast_eval
            
        return None 

    def finalize_answer(self) -> str:
        """
        Called when candidate stops speaking. 
        Saves the answer and time to history, and uses keyword matching to decide on a follow-up.
        DOES NOT call the LLM for deep evaluation to save compute.
        """
        if not self.state.current_question or not self.state.accumulated_answer.strip():
            return "follow_up"

        # Calculating actual response time
        time_taken = time.time() - self.state.question_start_time
        
        # Keyword filter for determining follow-ups
        fast_eval = self.fast_keyword_match(
            candidate_answer=self.state.accumulated_answer,
            expected_keywords=self.state.current_question.expected_keywords,
            threshold=0.6 # If you don't cover 60% of the words, we'll follow back.
        )
        
        next_action = "advance" if fast_eval else "follow_up"

        # Storing the answer for the final evaluation to be conducted after the interview.
        self.state.history.append({
            "question": self.state.current_question.question_text,
            "expected_keywords": self.state.current_question.expected_keywords,
            "answer": self.state.accumulated_answer,
            "time_taken": time_taken
        })
        
        # Clearing the memory for the next question
        self.state.accumulated_answer = ""
        
        return next_action # It returns a string to the router so it can generate the sub-question or proceed.

    def generate_interview_bank(self, role: str, core_skills: List[str], num_questions: int = 5) -> List[QuestionItem]:
        """
        Pre-computes a queue of interview questions to ensure zero-latency.
        """
        print(f"⚙️ Generating {num_questions} questions for {role}...")
        
        template = (
            "You are a Senior Technical Lead in Egypt interviewing a candidate for the {role} position.\n"
            "Your task is to generate exactly {num_questions} technical interview questions covering these skills: {skills}.\n\n"
            "CRITICAL RULES:\n"
            "1. Code-Switching: Speak in natural Egyptian Arabic, but keep ALL technical terms, frameworks, and patterns in ENGLISH.\n"
            "2. Progression: Start with an 'Easy' question, move to 'Medium', and end with 'Hard'.\n\n"
            "You MUST output ONLY a valid JSON array of objects, with NO markdown formatting or code blocks. Each object must exactly match this schema:\n"
            "[\n"
            "  {{\n"
            "    \"question_text\": \"Question in Egyptian Arabic + English tech terms\",\n"
            "    \"expected_keywords\": [\"keyword1\", \"keyword2\"],\n"
            "    \"difficulty\": \"Easy/Medium/Hard\",\n"
            "    \"target_skill\": \"skill name\"\n"
            "  }}\n"
            "]\n"
        )
        
        prompt = PromptTemplate(
            input_variables=["role", "skills", "num_questions"],
            template=template
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        try:
            response = chain.invoke({
                "role": role,
                "skills": ", ".join(core_skills),
                "num_questions": num_questions
            })
            
            raw_text = response.get("text", "").replace("```json", "").replace("```", "").strip()
            data_list = json.loads(raw_text)
            
            return [QuestionItem(**item) for item in data_list]
            
        except Exception as e:
            print(f"Error generating question bank: {e}")
            return [
                QuestionItem(
                    question_text=f"كلمنا عن خبرتك في الـ {skill} وإزاي بتتعامل مع المشاكل اللي بتظهرلك؟",
                    expected_keywords=[skill.lower(), "experience", "problem solving"],
                    difficulty="Medium",
                    target_skill=skill
                ) for skill in core_skills[:num_questions]
            ]
        
    def _evaluate_accuracy_only(self, question: str, answer: str) -> int:
        """
        Evaluates the technical accuracy of the answer based on academic and industry standards.
        Returns a score from 0 to 100.
        """
        template = (
            "You are an expert AI Technical Evaluator.\n"
            "Evaluate the candidate's answer to the following technical question.\n"
            "Compare the answer strictly against academic definitions, official documentation, and standard industry concepts.\n\n"
            "Question: {question}\n"
            "Candidate Answer: {answer}\n\n"
            "You MUST output ONLY an integer between 0 and 100 representing the accuracy score. "
            "Do not output any text, explanation, or markdown formatting. Just the number.\n"
        )
        
        prompt = PromptTemplate(
            input_variables=["question", "answer"],
            template=template
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        try:
            response = chain.invoke({
                "question": question,
                "answer": answer
            })
            
            raw_text = response.get("text", "").strip()
            # Extract just the integer from the response to avoid parsing errors
            score = int(''.join(filter(str.isdigit, raw_text)))
            
            # Ensure the score is within logical bounds
            return max(0, min(100, score))
            
        except Exception as e:
            print(f"Error in deep evaluation: {e}")
            return 0  # Fallback score in case of API failure
        
    def generate_final_report(self) -> Dict[str, Any]:
        """
        Called strictly AFTER the interview is over.
        Evaluates accuracy based on research/books (60% weight) and response time (40% weight).
        """
        print("📊 Generating final comprehensive evaluation report...")
        final_results = []
        total_score = 0
        
        for item in self.state.history:
            # 1. Evaluation of technical accuracy solely by an LLM (out of 100)
            # We will build a new prompt that measures academic accuracy and pass `item["question"]` and `item["answer"]` to it.
            accuracy_score = self._evaluate_accuracy_only(item["question"], item["answer"])
            
            # 2. Quantitative time assessment (out of 100)
            optimal_time = 30 # الوقت المثالي
            if item["time_taken"] <= optimal_time:
                time_score = 100
            else:
                penalty = (item["time_taken"] - optimal_time) * 2
                time_score = max(0, 100 - penalty)
                
            # 3. Final calculation (60% accuracy + 40% time)
            final_item_score = (accuracy_score * 0.60) + (time_score * 0.40)
            
            final_results.append({
                "question": item["question"],
                "accuracy_score": accuracy_score,
                "time_score": time_score,
                "final_score": final_item_score
            })
            total_score += final_item_score
            
        return {
            "overall_score": total_score / len(self.state.history) if self.state.history else 0,
            "details": final_results
        }