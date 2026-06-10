from src.agents.structure_agent import extract_slide_structure
from src.agents.slide_summary_agent import extract_slide_summary
from src.agents.transcript_agent import enhance_with_transcript
from src.agents.qa_agent import extract_qa
from src.agents.signoff_agent import generate_signoff


def run_signoff_pipeline(
    slide_text: str,
    transcript_text: str,
    signoff_style: str
) -> dict:
    """
    串接完整簽文產製流程。
    目前每一步先產生 Prompt，不直接呼叫 AI API。
    """

    slide_structure_prompt = extract_slide_structure(slide_text)

    slide_summary_prompt = extract_slide_summary(
        slide_structure=slide_structure_prompt,
        slide_text=slide_text
    )

    transcript_enhancement_prompt = enhance_with_transcript(
        slide_structure=slide_structure_prompt,
        slide_summary=slide_summary_prompt,
        transcript_text=transcript_text
    )

    qa_prompt = extract_qa(transcript_text)

    signoff_prompt = generate_signoff(
        slide_structure=slide_structure_prompt,
        slide_summary=slide_summary_prompt,
        transcript_enhancement=transcript_enhancement_prompt,
        qa_summary=qa_prompt,
        signoff_style=signoff_style
    )

    return {
        "slide_structure_prompt": slide_structure_prompt,
        "slide_summary_prompt": slide_summary_prompt,
        "transcript_enhancement_prompt": transcript_enhancement_prompt,
        "qa_prompt": qa_prompt,
        "signoff_prompt": signoff_prompt
    }
