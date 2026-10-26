"""Statutory Deficiency Letter Generation and AI Enhancement Service.

Generates official regulatory communication in English, Tamil, and Hindi using Jinja2 templates.
Provides optional Google Gemini LLM integration for regulatory tone refinement.
"""

from datetime import date, timedelta
from typing import Any, Dict, List, Optional
import jinja2

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from app.core.config import settings
from app.models.application import Application
from app.models.flag import Flag
from app.models.institution import Institution
from app.schemas.letter import LetterResponse


ENGLISH_TEMPLATE = """ALL INDIA COUNCIL FOR TECHNICAL EDUCATION
Nelson Mandela Marg, Vasant Kunj, New Delhi-110070
APPROVAL PROCESS BUREAU

Ref No: AICTE/APB/DEF/{{ application.academic_year }}/{{ application.id }}
Date: {{ today }}

To,
The Principal / Secretary,
{{ institution.name }},
{{ institution.address }}, {{ institution.city }}, {{ institution.state }}
Permanent Institute ID: {{ institution.code }}

SUBJECT: NOTICE OF STATUTORY DEFICIENCIES AND REGULATORY DISCREPANCIES FOR APPROVAL CYCLE {{ application.academic_year }}

Sir / Madam,

This has reference to your Application ID #{{ application.id }} submitted for {{ application.category.replace('_', ' ').title() }} under the Approval Process Handbook provisions.

Upon comprehensive automated verification, forensic artifact examination, and statutory compliance cross-checks, the competent authority has noted the following significant deficiencies and discrepancies:

{% for flag in flags %}
--------------------------------------------------------------------------------
{{ loop.index }}. Discrepancy Code: {{ flag.code }} [Severity: {{ flag.severity.upper() }}]
   Category: {{ flag.flag_type.title() }}
   Title: {{ flag.title }}
   Statutory Finding: {{ flag.reason }}
   Rule Reference: {{ flag.rule_id or 'Statutory Regulations' }}
{% endfor %}

{% if additional_remarks %}
Special Observations:
{{ additional_remarks }}
{% endif %}

You are hereby directed to rectify the above deficiencies, upload verified replacement artifacts, and submit your formal compliance representation on the AICTE Portal within {{ deadline_days }} days from the date of issue of this letter (on or before {{ deadline_date }}).

Failure to rectify the highlighted discrepancies within the stipulated timeline shall lead to adverse regulatory action, including reduction in sanctioned intake or rejection of the approval application.

By Order of the Competent Authority,

Regional Officer
Approval Process Bureau
All India Council for Technical Education
"""

TAMIL_TEMPLATE = """அகில இந்திய தொழில்நுட்பக் கல்விக் குழு (AICTE)
நெல்சன் மண்டேலா மார்க், வசந்த் குஞ்ச், புது தில்லி-110070

குறிப்பு எண்: AICTE/APB/DEF/{{ application.academic_year }}/{{ application.id }}
நாள்: {{ today }}

பெறுநர்:
முதல்வர் / தாளாளர்,
{{ institution.name }},
{{ institution.address }}, {{ institution.city }}, {{ institution.state }}
நிரந்தர நிறுவனக் குறியீடு: {{ institution.code }}

பொருள்: {{ application.academic_year }} கல்வி ஆண்டிற்கான குறைபாடுகள் மற்றும் முரண்பாடுகள் குறித்த அறிவிப்பு

ஐயா / அம்மையீர்,

தங்களின் விண்ணப்ப எண் #{{ application.id }} ({{ application.category.replace('_', ' ').title() }}) மீதான சரிபார்ப்பில் கீழ்க்கண்ட குறைபாடுகள் கண்டறியப்பட்டுள்ளன:

{% for flag in flags %}
{{ loop.index }}. குறியீடு: {{ flag.code }} [தீவிரம்: {{ flag.severity.upper() }}]
   வகை: {{ flag.flag_type.title() }}
   விவரம்: {{ flag.title }}
   காரணம்: {{ flag.reason }}
{% endfor %}

மேற்கண்ட குறைபாடுகளை {{ deadline_days }} நாட்களுக்குள் (கடைசி நாள்: {{ deadline_date }}) சரிசெய்து இணையதளத்தில் பதிவேற்றுமாறு அறிவுறுத்தப்படுகிறீர்கள்.

உரிய அதிகாரி,
அகில இந்திய தொழில்நுட்பக் கல்விக் குழு
"""

HINDI_TEMPLATE = """अखिल भारतीय तकनीकी शिक्षा परिषद (AICTE)
नेल्सन मंडेला मार्ग, वसंत कुंज, नई दिल्ली-110070

संदर्भ संख्या: AICTE/APB/DEF/{{ application.academic_year }}/{{ application.id }}
दिनांक: {{ today }}

सेवा में,
प्राचार्य / सचिव,
{{ institution.name }},
{{ institution.address }}, {{ institution.city }}, {{ institution.state }}
स्थायी संस्थान आईडी: {{ institution.code }}

विषय: शैक्षणिक सत्र {{ application.academic_year }} के लिए अनुमोदन आवेदन में कमियों एवं विसंगतियों की सूचना

महोदय / महोदया,

आपके आवेदन संख्या #{{ application.id }} ({{ application.category.replace('_', ' ').title() }}) की जांच के उपरांत निम्नलिखित विसंगतियां पाई गई हैं:

{% for flag in flags %}
{{ loop.index }}. विसंगति कोड: {{ flag.code }} [गंभीरता: {{ flag.severity.upper() }}]
   श्रेणी: {{ flag.flag_type.title() }}
   शीर्षक: {{ flag.title }}
   विवरण: {{ flag.reason }}
{% endfor %}

अतः आपको निर्देशित किया जाता है कि {{ deadline_days }} दिनों के भीतर (अंतिम तिथि: {{ deadline_date }}) तक इन कमियों का निवारण करें।

सक्षम प्राधिकारी के आदेश से,
क्षेत्रीय अधिकारी, AICTE
"""


class LetterService:
    """Generates and refines formal regulatory notices for colleges."""

    def __init__(self):
        self.templates = {
            "eng": jinja2.Template(ENGLISH_TEMPLATE),
            "tam": jinja2.Template(TAMIL_TEMPLATE),
            "hin": jinja2.Template(HINDI_TEMPLATE),
        }

    def generate_deficiency_letter(
        self,
        application: Application,
        institution: Institution,
        open_flags: List[Flag],
        language: str = "eng",
        deadline_days: int = 15,
        additional_remarks: Optional[str] = None,
    ) -> LetterResponse:
        """Render formal deficiency notice using Jinja2 language template."""
        lang_key = language.lower().strip()
        template = self.templates.get(lang_key, self.templates["eng"])

        today = date.today()
        deadline_date = today + timedelta(days=deadline_days)

        rendered_text = template.render(
            application=application,
            institution=institution,
            flags=open_flags,
            today=today.strftime("%d-%m-%Y"),
            deadline_date=deadline_date.strftime("%d-%m-%Y"),
            deadline_days=deadline_days,
            additional_remarks=additional_remarks,
        )

        subject = f"Notice of Deficiencies - Application #{application.id} ({application.academic_year})"
        flag_codes = [f.code for f in open_flags]

        return LetterResponse(
            application_id=application.id,
            institution_name=institution.name,
            language=lang_key,
            subject=subject,
            content=rendered_text,
            deficiencies_count=len(open_flags),
            open_flags=flag_codes,
            status="draft",
            gemini_enhanced=False,
        )

    async def improve_letter_with_gemini(
        self, draft_content: str, language: str = "eng", tone: str = "formal_regulatory"
    ) -> str:
        """Refine regulatory deficiency draft wording using Gemini LLM if configured."""
        if not settings.GEMINI_API_KEY or not GEMINI_AVAILABLE:
            # Fallback returning original text with standard polish notice
            return draft_content

        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = (
                f"You are a legal counsel drafting official notices for the All India Council for Technical Education (AICTE). "
                f"Refine the following deficiency notice to ensure unambiguous legal clarity, regulatory precision, "
                f"and authoritative tone while retaining all specific codes, dates, and names. Language: {language}.\n\n"
                f"Draft:\n{draft_content}"
            )
            response = await model.generate_content_async(prompt)
            if response and response.text:
                return response.text
        except Exception:
            pass

        return draft_content


# Singleton instance
letter_service = LetterService()
