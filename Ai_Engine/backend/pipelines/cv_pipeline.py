import os
import shutil
import zipfile
from pathlib import Path
from typing import List, Tuple, Dict, Any

from dotenv import load_dotenv

import json

# --- LangChain Updated Imports ---
from langchain_classic.chains import LLMChain
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.output_parsers import PydanticOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
# --- Pydantic ---
from pydantic import BaseModel, Field

load_dotenv()

os.environ["TOKENIZERS_PARALLELISM"] = "false"

class CVAnalysisOutput(BaseModel):
    skills: list[str] = Field(description="List of technical and soft skills extracted from the CV")
    score: int = Field(description="A score from 1 to 10 evaluating the candidate's fit")
    reasons: str = Field(description="Brief reasoning for the score and extracted skills")


class RAGPipeline:
    """
    A simple RAG pipeline using:
    - Embeddings: HuggingFaceEmbeddings ("all-MiniLM-L6-v2")
    - LLM: ChatGoogleGenerativeAI (default "gemini-2.5-flash")
    - Vector store: FAISS (saved/loaded locally)
    """

    def __init__(
        self,
        persist_dir: str = "vectorstore/faiss_index",
        chunk_size: int = 1200,
        chunk_overlap: int = 200,
        k: int = 8,
        temperature: float = 0.2,
        model_name: str = None
    ) -> None:
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.k = k
        self.temperature = temperature

        self.model_name = model_name or os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")

        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.llm = ChatGoogleGenerativeAI(model=self.model_name, temperature=self.temperature)

        self.db = None
        if any(self.persist_dir.iterdir()):
            self._load_index()

        self.qa_chain = None
        if self.db is not None:
            self._build_qa_chain()

    def evaluate_single_cv(self, pdf_path: str, job_description: str) -> Dict[str, Any]:
        """
        Evaluates a single CV directly against a Job Description without using FAISS.
        """
        path = Path(pdf_path)
        if not path.exists():
            return {"error": "CV file not found"}

        # Extract text from the single PDF
        loader = PDFPlumberLoader(str(path))
        docs = loader.load()
        cv_text = "\n".join([doc.page_content for doc in docs])

        # Prepare the Prompt for direct LLM evaluation
        template = (
            "You are an expert Technical HR Recruiter and AI CV Analyzer.\n"
            "Evaluate the candidate's CV against the provided Job Description.\n\n"
            "Candidate CV:\n{cv_text}\n\n"
            "Job Description:\n{job_description}\n\n"
            "You MUST output the response ONLY as a valid JSON object with the following exact keys:\n"
            "1. 'match_score': An integer from 0 to 100 representing how well the CV matches the requirements.\n"
            "2. 'matched_skills': A list of strings containing the skills present in the CV that match the JD.\n"
            "3. 'missing_skills': A list of strings containing important skills missing from the CV.\n"
            "4. 'justification': A brief sentence explaining the score.\n"
        )
        prompt = PromptTemplate(
            input_variables=["cv_text", "job_description"],
            template=template,
        )
        
        # Invoke the chain
        chain = LLMChain(llm=self.llm, prompt=prompt)
        raw_answer = chain.invoke({"cv_text": cv_text, "job_description": job_description})
        raw_text = raw_answer.get("text", "")

        # Parse JSON
        try:
            cleaned_answer = raw_text.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned_answer)
        except json.JSONDecodeError:
            return {"error": "Failed to parse AI response as JSON", "raw_text": raw_text}

    def _build_qa_chain(self) -> None:
        retriever = self.db.as_retriever(search_kwargs={"k": self.k})
        
        template = (
            "You are an expert Technical HR Recruiter and AI CV Analyzer.\n"
            "Evaluate the candidate's CV (provided in Context) against the required Job Description or Question.\n\n"
            "Context (Candidate CV):\n{context}\n\n"
            "Job Description / Query: {question}\n\n"
            "You MUST output the response ONLY as a valid JSON object with the following exact keys:\n"
            "1. 'match_score': An integer from 0 to 100 representing how well the CV matches the requirements.\n"
            "2. 'matched_skills': A list of strings containing the skills present in the CV that match the query.\n"
            "3. 'missing_skills': A list of strings containing important skills missing from the CV.\n"
            "4. 'justification': A brief sentence explaining the score.\n\n"
            "Do not include any markdown formatting like ```json, just the raw JSON object.\n"
        )
        prompt = PromptTemplate(
            input_variables=["context", "question"], # تم تصحيح input إلى question
            template=template,
        )
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt},
        )
        
    def _save_index(self) -> None:
        if self.db is not None:
            self.db.save_local(str(self.persist_dir))

    def _load_index(self) -> None:
        self.db = FAISS.load_local(
            str(self.persist_dir),
            self.embeddings,
            allow_dangerous_deserialization=True,
        )

    def _ensure_index(self) -> None:
        if self.db is None:
            raise RuntimeError("Vector index is empty. Upload PDFs first.")


    def set_params(self, k: int = None, temperature: float = None) -> Dict[str, Any]:
        updated = {}
        if k is not None:
            self.k = int(k)
            updated["k"] = self.k
        if temperature is not None:
            self.temperature = float(temperature)
            self.llm = ChatGoogleGenerativeAI(model=self.model_name, temperature=self.temperature)
            updated["temperature"] = self.temperature

        if self.db is not None:
            self._build_qa_chain()

        return updated

    def reset_index(self) -> None:
        if self.persist_dir.exists():
            shutil.rmtree(self.persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.db = None
        self.qa_chain = None

    def add_file(self, file_path: str) -> Dict[str, Any]:
        """
        Add a single PDF, or extract a ZIP and add all PDFs inside it.
        Returns summary dict with counts.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"{file_path} does not exist")

        pdf_paths: List[Path] = []

        if path.suffix.lower() == ".zip":
            extract_dir = path.with_suffix("")
            extract_dir.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(path, "r") as zf:
                zf.extractall(extract_dir)
            for p in extract_dir.rglob("*.pdf"):
                pdf_paths.append(p)
        elif path.suffix.lower() == ".pdf":
            pdf_paths.append(path)
        else:
            raise ValueError("Only .pdf or .zip files are supported.")

        docs = []
        for pdf in pdf_paths:
            loader = PDFPlumberLoader(str(pdf))
            docs.extend(loader.load())

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )
        chunks = splitter.split_documents(docs)

        if self.db is None:
            self.db = FAISS.from_documents(chunks, self.embeddings)
        else:
            self.db.add_documents(chunks)

        self._save_index()
        self._build_qa_chain()

        return {
            "files_added": [str(p) for p in pdf_paths],
            "num_pages": len(docs),
            "num_chunks": len(chunks),
        }

    def ask(self, question: str) -> Dict[str, Any]:
        if self.qa_chain is None:
            return {"answer": "No documents available.", "sources": []}
            
        res = self.qa_chain.invoke({"query": question})
        raw_answer = res.get("result", "")
        
        parsed_answer = {}
        try:
            cleaned_answer = raw_answer.replace("```json", "").replace("```", "").strip()
            parsed_answer = json.loads(cleaned_answer)
        except json.JSONDecodeError:
            parsed_answer = {"error": "Failed to parse AI response as JSON", "raw_text": raw_answer}

        src_docs = res.get("source_documents", []) or []
        sources = [{"source": d.metadata.get("source"), "page": d.metadata.get("page", 0) + 1} for d in src_docs]

        return {"analysis": parsed_answer, "sources": sources}

    def stats(self) -> Dict[str, Any]:

        has_index = self.db is not None
        return {
            "has_index": has_index,
            "persist_dir": str(self.persist_dir),
            "k": self.k,
            "temperature": self.temperature,
            "model_name": self.model_name
        }
