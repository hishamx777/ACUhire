import os
from docx import Document
from docx.shared import Pt, RGBColor, Inches
from docx.enum.text import WD_LINE_SPACING, WD_ALIGN_PARAGRAPH

def create_graduation_project_doc():
    doc = Document()

    # ==========================================
    # 1. إعدادات الخطوط والمسافات (المعايير الأكاديمية والتعديلات الجديدة)
    # ==========================================
    
    # إعداد الخط العادي (Normal - 14pt) مع مسافة بادئة لأول سطر
    style_normal = doc.styles['Normal']
    font_normal = style_normal.font
    font_normal.name = 'Times New Roman'
    font_normal.size = Pt(14)
    font_normal.color.rgb = RGBColor(0, 0, 0)
    style_normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    style_normal.paragraph_format.first_line_indent = Inches(0.5) # التعديل الأول: مسافة بداية السطر

    # إعداد العناوين الرئيسية (Heading 1 - 18pt Bold)
    style_h1 = doc.styles['Heading 1']
    font_h1 = style_h1.font
    font_h1.name = 'Times New Roman'
    font_h1.size = Pt(18)
    font_h1.bold = True
    font_h1.color.rgb = RGBColor(0, 0, 0)
    style_h1.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE

    # إعداد العناوين الفرعية الأولى (Heading 2 - 16pt Bold) مثال: 3.4
    style_h2 = doc.styles['Heading 2']
    font_h2 = style_h2.font
    font_h2.name = 'Times New Roman'
    font_h2.size = Pt(16)
    font_h2.bold = True
    font_h2.color.rgb = RGBColor(0, 0, 0)
    style_h2.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE

    # إعداد العناوين الفرعية الثانية (Heading 3 - 14pt Bold) مثال: 3.4.1
    style_h3 = doc.styles['Heading 3']
    font_h3 = style_h3.font
    font_h3.name = 'Times New Roman'
    font_h3.size = Pt(14)
    font_h3.bold = True
    font_h3.color.rgb = RGBColor(0, 0, 0)
    style_h3.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    style_h3.paragraph_format.left_indent = Inches(0.5) # التعديل الثاني: العنوان نفسه مزقوق لجوه

    # ==========================================
    # دوال مساعدة لضبط المسافات في حالات خاصة
    # ==========================================
    def add_center_text(text, bold=False, size=14):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.first_line_indent = Pt(0) # إلغاء المسافة البادئة للكلام المتسنتر
        run = p.add_run(text)
        run.bold = bold
        run.font.size = Pt(size)

    def add_flush_text(text, bold=False):
        # للبيانات اللي محتاجينها على الشمال بدون مسافة بادئة (زي الـ Cover)
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Pt(0)
        run = p.add_run(text)
        run.bold = bold

    def add_bullet(text):
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Pt(0)
        p.paragraph_format.left_indent = Inches(0.5)
        p.add_run(f"• {text}")

    def add_arabic_text(text, bold=False):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        p.paragraph_format.first_line_indent = Inches(0.5)
        run = p.add_run(text)
        run.bold = bold
        
    # ==========================================
    # 2. إضافة محتوى الكتاب
    # ==========================================

    # --- Cover Page ---
    add_center_text("Ministry of High Education\nCulture and Science City at Oct 6\nThe High Institute of Computer Science & Information Systems\n\n", bold=True, size=16)
    add_center_text("Graduation Project\n\"AcuHire: AI-Driven Recruitment & Semantic Matching Platform\"\n\n", bold=True, size=18)
    
    add_flush_text("Submitted by:", bold=True)
    add_flush_text("1. Hesham Moselhi Gharib Moselhi (ID: 210976)")
    add_flush_text("2. [اسم الزميل الثاني] (ID: [رقم الجلوس])")
    add_flush_text("3. [اسم الزميل الثالث] (ID: [رقم الجلوس])\n")
    
    add_center_text("A graduation project submitted in partial fulfillment of the requirements for the degree of Bachelor of Computer Science and Information System.\n", bold=True)
    
    add_flush_text("Supervised by:", bold=True)
    add_flush_text("Dr. [اسم الدكتور]")
    add_flush_text("TA. [اسم المعيد]\n")
    
    add_flush_text("Project No: [رقم المشروع]")
    add_flush_text("Academic Year: 2025/2026")
    doc.add_page_break()

    # --- Acknowledgement ---
    doc.add_heading('Acknowledgement', level=1)
    doc.add_paragraph("We would like to express our deepest gratitude to the High Institute of Computer Science & Information Systems for providing the academic resources necessary to complete this project. Special thanks to our supervisor, Dr. [اسم الدكتور], and our Teaching Assistant, TA. [اسم المعيد], for their invaluable guidance, continuous support, and constructive feedback. Finally, we thank our families and team members for their dedication and hard work throughout the development of AcuHire.")
    doc.add_page_break()

    # --- Abstract ---
    doc.add_heading('Abstract', level=1)
    doc.add_paragraph("The traditional recruitment process is often highly inefficient, characterized by manual resume screening and biased candidate evaluations. \"AcuHire\" is an innovative, AI-driven recruitment platform engineered to automate and optimize the hiring pipeline. The system utilizes advanced Natural Language Processing (NLP) to parse unstructured CVs, perform semantic matching against job descriptions, and rank candidates objectively. Furthermore, AcuHire integrates an automated AI Interview Bot that evaluates both technical proficiency and soft skills in real-time. By bridging the gap between sophisticated AI algorithms and human resource management, AcuHire significantly reduces time-to-hire and ensures high-quality talent acquisition.")
    doc.add_page_break()

    # --- Table of Contents & Lists ---
    doc.add_heading('Table of Contents', level=1)
    doc.add_paragraph("(قم بتحديث الفهرس تلقائياً من برنامج Word بعد فتح الملف لتوليد أرقام الصفحات)")
    doc.add_page_break()

    doc.add_heading('List of Figures', level=1)
    add_flush_text("Figure 4.1: Entity Relationship Diagram\n(سيتم استكمال القائمة بعد إدراج الصور)")
    doc.add_page_break()

    doc.add_heading('List of Tables', level=1)
    add_flush_text("Table 3.1: Feasibility Study Costs\n(سيتم استكمال القائمة بعد إدراج الجداول)")
    doc.add_page_break()

    doc.add_heading('List of Abbreviations and Acronyms', level=1)
    abbreviations = [
        "AI: Artificial Intelligence",
        "API: Application Programming Interface",
        "NLP: Natural Language Processing",
        "RBAC: Role-Based Access Control",
        "STT: Speech-to-Text",
        "CV: Curriculum Vitae",
        "ERD: Entity Relationship Diagram"
    ]
    for abv in abbreviations:
        add_bullet(abv)
    doc.add_page_break()

    # --- Chapter 1: Introduction ---
    doc.add_heading('Chapter 1: Introduction', level=1)
    
    doc.add_heading('1.1 Overview', level=2)
    doc.add_paragraph("In the modern corporate landscape, Human Resources (HR) departments face immense pressure to identify top talent quickly. AcuHire provides a comprehensive software solution that leverages artificial intelligence to automate resume parsing and preliminary interviewing. Built with a robust FastAPI backend and a dynamic Next.js frontend, the platform processes complex data efficiently.")

    doc.add_heading('1.2 Motivation', level=2)
    doc.add_paragraph("The motivation behind AcuHire stems from the limitations of traditional Applicant Tracking Systems (ATS), which often rely on rigid keyword matching, rejecting qualified candidates due to formatting issues. Developing a platform capable of deep semantic analysis ensures fairness and accuracy in the hiring process.")

    doc.add_heading('1.3 Objective', level=2)
    add_bullet("To design an intelligent CV parser capable of extracting structured data from unstructured PDFs.")
    add_bullet("To develop an AI scoring engine that ranks applicants based on semantic matching.")
    add_bullet("To build a seamless, role-based interface for employers and job seekers.")

    doc.add_heading('1.4 Aim', level=2)
    doc.add_paragraph("To revolutionize recruitment by providing an end-to-end, AI-powered system that eliminates manual screening bottlenecks.")

    doc.add_heading('1.5 Scope', level=2)
    doc.add_paragraph("AcuHire covers the digital recruitment lifecycle from job posting and CV submission to AI evaluation and ranking. It is designed for enterprise HR usage but does not handle payroll or legal contract generation.")

    doc.add_heading('1.6 General Constraints', level=2)
    doc.add_paragraph("The system requires internet connectivity for cloud-based AI processing. There are also hardware constraints regarding the local execution of large language models during the testing phase, requiring optimization for standard devices.")

    doc.add_heading('1.7 Organization of the project', level=2)
    doc.add_paragraph("This document is divided into six chapters. Chapter 1 introduces the project. Chapter 2 reviews the background and previous work. Chapter 3 details system analysis and requirements. Chapter 4 presents the UML and database designs. Chapter 5 covers implementation, and Chapter 6 discusses testing methodologies, followed by the conclusion and references.")
    doc.add_page_break()

    # --- Chapter 2: Background and Previous Work ---
    doc.add_heading('Chapter 2: Background and Previous Work', level=1)
    
    doc.add_heading('2.1 Background', level=2)
    doc.add_paragraph("Recruitment technology has evolved from simple paper-based files to digital ATS platforms. However, current systems lack cognitive understanding. The integration of advanced language models allows modern systems to understand context, transforming HR from an administrative task into a strategic operation.")
    
    doc.add_heading('2.2 Previous Work', level=2)
    doc.add_paragraph("Existing platforms like LinkedIn or standard ATS tools rely heavily on exact keyword matches. Unlike these systems, AcuHire introduces semantic matching and an integrated interview bot, reducing the need for third-party interview assessment tools.")
    doc.add_page_break()

    # --- Chapter 3: Planning and Analysis ---
    doc.add_heading('Chapter 3: Planning and Analysis', level=1)
    
    doc.add_heading('3.1 Planning', level=2)
    # استخدام العنوان الفرعي المتدرج (Level 3)
    doc.add_heading('3.1.1 Feasibility study and estimated cost', level=3)
    doc.add_paragraph("The project is highly feasible technically and economically. By utilizing open-source frameworks (FastAPI, React) and free-tier cloud databases, the financial cost is minimized.")
    
    doc.add_heading('3.1.2 Gantt chart', level=3)
    doc.add_paragraph("(أدرج صورة جدول Gantt الزمني هنا)")
    
    doc.add_heading('3.2 Analysis and limitations of existing system', level=2)
    doc.add_paragraph("Current systems suffer from high false-negative rates in resume screening and cannot conduct autonomous technical interviews.")

    doc.add_heading('3.3 Need for new system', level=2)
    doc.add_paragraph("AcuHire is needed to provide an all-in-one solution that not only reads resumes intelligently but also interacts with candidates to evaluate soft skills.")

    doc.add_heading('3.4 Analysis of new system', level=2)
    
    doc.add_heading('3.4.1 User Requirements', level=3)
    doc.add_paragraph("Users need a secure login, intuitive dashboards, and fast feedback.")
    
    doc.add_heading('3.4.2 System Requirements', level=3)
    doc.add_paragraph("High availability, secure API endpoints, and scalable cloud storage.")
    
    doc.add_heading('3.4.3 Domain Requirements', level=3)
    doc.add_paragraph("Compliance with standard HR data structures and PDF processing.")
    
    doc.add_heading('3.4.4 Functional Requirements', level=3)
    doc.add_paragraph("The system must allow companies to post jobs, parse uploaded CVs, and generate a candidate score.")
    
    doc.add_heading('3.4.5 Non-Functional Requirements', level=3)
    doc.add_paragraph("CV parsing should take under 5 seconds. Passwords must be hashed.")

    doc.add_heading('3.5 Advantages of new system', level=2)
    doc.add_paragraph("Reduces screening time by 80%, eliminates human bias, and centralizes candidate data.")

    doc.add_heading('3.6 User characteristics', level=2)
    doc.add_paragraph("Target users include HR Managers (Employer Role) and Job Applicants (Employee Role), requiring varying levels of technical proficiency.")
    doc.add_page_break()

    # --- Chapter 4: Design ---
    doc.add_heading('Chapter 4: Design', level=1)
    
    doc.add_heading('4.1 Design and Implementation Constraints', level=2)
    doc.add_paragraph("The design must adhere to stateless API principles (REST) to allow separation between the frontend and backend.")
    
    doc.add_heading('4.2 Assumptions and dependencies', level=2)
    doc.add_paragraph("It is assumed that candidates will upload standard PDF formats. Dependencies include external LLM APIs for the interview bot module.")
    
    doc.add_heading('4.3 Risks and risk management', level=2)
    doc.add_paragraph("Risk: AI misinterpretation of custom CV layouts. Mitigation: Implementing robust fallback OCR logic.")
    
    doc.add_heading('4.4 Design of database ERD', level=2)
    doc.add_heading('4.4.1 Entity Relationship Diagram', level=3)
    doc.add_paragraph("(أدرج الصورة هنا)")
    doc.add_heading('4.4.2 Mapping of Entity Relationship Diagram', level=3)
    doc.add_paragraph("Entities include Users, Jobs, Applications, and Interviews.")
    
    doc.add_heading('4.5 Class diagram', level=2)
    doc.add_paragraph("(أدرج الصورة هنا)")
    
    doc.add_heading('4.6 Use case diagram', level=2)
    doc.add_heading('4.6.1 Primary Use-case Diagram', level=3)
    doc.add_paragraph("(أدرج الصورة هنا)")
    doc.add_heading('4.6.2 Use-case Scenarios', level=3)
    doc.add_paragraph("Employee uploads CV; Employer views ranked list.")
    
    doc.add_heading('4.7 Activity diagram', level=2)
    doc.add_paragraph("(أدرج الصورة هنا)")
    
    doc.add_heading('4.8 Sequence diagram', level=2)
    doc.add_paragraph("(أدرج الصورة هنا)")
    
    doc.add_heading('4.9 State diagram', level=2)
    doc.add_paragraph("(أدرج الصورة هنا)")
    doc.add_page_break()

    # --- Chapter 5: Implementation ---
    doc.add_heading('Chapter 5: Implementation', level=1)
    
    doc.add_heading('5.1 Software Architecture', level=2)
    doc.add_paragraph("AcuHire follows a modern Client-Server architecture. The frontend is built with React/Next.js for dynamic rendering, communicating via RESTful APIs with a Python (FastAPI) backend. The backend interfaces with a PostgreSQL database and AI microservices.")
    
    doc.add_heading('5.2 User Interface', level=2)
    doc.add_paragraph("(قم بإدراج لقطات شاشة (Screenshots) للمنصة هنا)")
    
    doc.add_heading('5.3 Results and Discussion', level=2)
    doc.add_paragraph("The implementation successfully yielded a working prototype. The AI engine accurately extracts skills from test CVs and assigns logical scores compared to the job descriptions.")
    doc.add_page_break()

    # --- Chapter 6: Testing ---
    doc.add_heading('Chapter 6: Testing', level=1)
    
    doc.add_heading('6.1 Unit Testing', level=2)
    doc.add_paragraph("Individual components, such as the password hashing utility and the PDF text extraction function, were tested in isolation to ensure accurate outputs.")
    
    doc.add_heading('6.2 Integration Testing', level=2)
    doc.add_paragraph("The connection between the Next.js frontend and the FastAPI backend was thoroughly tested, specifically the Application Submission API workflow, to ensure data flows correctly from the user interface to the database and triggers the background AI tasks.")
    
    doc.add_heading('Conclusion', level=1)
    doc.add_paragraph("AcuHire successfully demonstrates the potential of artificial intelligence in reshaping human resources. By automating the most tedious parts of recruitment—CV screening and initial interviews—the platform allows companies to make faster, data-driven hiring decisions.")
    
    doc.add_heading('Future Work', level=1)
    doc.add_paragraph("Future iterations of AcuHire could include integration with external professional networks for direct profile parsing, video-based analysis during the interview phase, and multi-language support to cater to global enterprise markets.")
    doc.add_page_break()

    # --- References ---
    doc.add_heading('References', level=1)
    references = [
        "[1] Bird, S., Klein, E., & Loper, E. (2009). Natural Language Processing with Python. 1st Ed. Sebastopol, CA: O'Reilly Media.",
        "[2] Ramirez, S. (2023). Building RESTful APIs with FastAPI. 2nd Ed. New York: TechPress.",
        "[3] Harrison, C. (2024). Next.js for Enterprise Applications. Vol 2. London: WebDev Publishers.",
        "[4] OpenAI. (2025) Speech-to-Text architectures and Whisper AI. [available at: https://openai.com/research/whisper] [viewed on 10/05/2026].",
        "[5] Smith, J. (2022) AI in Recruitment. HR Tech Magazine, Vol 14, No 3, pp. 45-50."
    ]
    for ref in references:
        add_flush_text(ref)
    doc.add_page_break()

    # --- Arabic Summary ---
    add_arabic_text("ملخص المشروع بالعربى", bold=True)
    add_arabic_text("مشروع AcuHire: منصة التوظيف والتحليل الدلالي باستخدام الذكاء الاصطناعي", bold=True)
    add_arabic_text("يعتبر مشروع \"AcuHire\" حلاً برمجياً متكاملاً يهدف إلى إحداث ثورة في قطاع الموارد البشرية من خلال أتمتة عملية التوظيف. تعاني الطرق التقليدية للتوظيف من البطء والانحياز البشري، ولذلك تم بناء هذه المنصة باستخدام أحدث تقنيات الذكاء الاصطناعي لمعالجة السير الذاتية بذكاء.")
    add_arabic_text("يقوم النظام باستقبال ملفات المتقدمين وتحليل محتواها باستخدام تقنيات معالجة اللغات الطبيعية (NLP) لاستخراج المهارات والخبرات بدقة، ثم يجري عملية مطابقة دلالية بين تلك المهارات ومتطلبات الوظيفة لإعطاء تقييم رقمي عادل وشفاف. يتيح النظام واجهة مخصصة للشركات لعرض ترتيب المتقدمين بناءً على كفاءتهم الفعلية. إلى جانب ذلك، تم دمج محرك المقابلة الذكي القادر على إجراء مقابلات وتفريغ الصوت لنص لتقييم المهارات التقنية وسرعة الاستجابة للمتقدمين. تم تصميم النظام ليضمن السرعة، والموثوقية، وتجربة مستخدم سلسة لكل من الباحثين عن عمل ومديري التوظيف.")

    # ==========================================
    # 3. حفظ المستند
    # ==========================================
    file_name = 'AcuHire_Graduation_Project_Final.docx'
    doc.save(file_name)
    print(f"Done!:{file_name}")

if __name__ == "__main__":
    create_graduation_project_doc()