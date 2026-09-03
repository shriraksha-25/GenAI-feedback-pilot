from ai.services.feedback_analyzer import analyze_feedback


def process_feedback(feedback_text: str):

    result = analyze_feedback(
        text=feedback_text
    )

    return {
        "feedback_text": result["cleaned_text"],
        "status": result["status"]
    }