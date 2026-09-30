def get_performance_level(score):
    """
    Determine the performance tier based on the standardized scale:
    90-100 -> Excellent
    80-89  -> Very Good
    70-79  -> Good
    60-69  -> Average
    Below 60 -> Needs Improvement
    """
    if score >= 90.0:
        return "Excellent"
    elif score >= 80.0:
        return "Very Good"
    elif score >= 70.0:
        return "Good"
    elif score >= 60.0:
        return "Average"
    else:
        return "Needs Improvement"

def generate_feedback(scores, matched_keywords=None, missed_keywords=None):
    """
    Generate deterministic, constructive technical feedback based on actual component scores.
    
    Expected scores dict keys:
    - final_score
    - relevance_score
    - keyword_score
    - similarity_score
    - completeness_score
    - grammar_score
    """
    matched_keywords = matched_keywords or []
    missed_keywords = missed_keywords or []

    final_score = scores.get("final_score", 0.0)
    rel_score = scores.get("relevance_score", 0.0)
    kw_score = scores.get("keyword_score", 0.0)
    sim_score = scores.get("similarity_score", 0.0)
    comp_score = scores.get("completeness_score", 0.0)
    gram_score = scores.get("grammar_score", 0.0)

    feedback_parts = []

    # 1. Overall assessment
    if final_score >= 90:
        feedback_parts.append("Strong answer. You covered the major concepts clearly and articulated the technical explanation with precision.")
    elif final_score >= 80:
        feedback_parts.append("Very solid answer. You addressed the core technical requirements effectively with minor room for greater depth.")
    elif final_score >= 70:
        feedback_parts.append("Good answer. The foundational explanation is correct, but expanding on edge cases or deeper mechanics would strengthen it.")
    elif final_score >= 60:
        feedback_parts.append("Average response. You demonstrated a basic grasp of the topic, but several key technical elements were omitted.")
    else:
        feedback_parts.append("Needs Improvement. Your response lacks key technical depth and does not fully align with the expected explanation.")

    # 2. Keyword Coverage Feedback
    if kw_score >= 80:
        if matched_keywords:
            sample_matched = ", ".join([f"'{k}'" for k in matched_keywords[:4]])
            feedback_parts.append(f"Excellent technical terminology! Successfully identified key terms: {sample_matched}.")
    elif kw_score >= 50:
        if missed_keywords:
            sample_missed = ", ".join([f"'{k}'" for k in missed_keywords[:3]])
            feedback_parts.append(f"Moderate vocabulary coverage. To improve, try incorporating concepts like: {sample_missed}.")
    else:
        if missed_keywords:
            sample_missed = ", ".join([f"'{k}'" for k in missed_keywords[:4]])
            feedback_parts.append(f"Your answer missed several important technical concepts. Consider including terminology such as {sample_missed}.")
        else:
            feedback_parts.append("Your answer missed several important technical concepts.")

    # 3. Similarity Feedback
    if sim_score >= 75:
        feedback_parts.append("High alignment with standard industry reference definitions.")
    elif sim_score < 50:
        feedback_parts.append("Your answer has limited overlap with the expected concepts. Review the foundational principles of this topic.")

    # 4. Completeness Feedback
    if comp_score >= 85:
        feedback_parts.append("The explanation is comprehensive and thorough.")
    elif comp_score < 60:
        feedback_parts.append("Your answer covers some concepts but misses important points. Elaborate more on the underlying mechanism.")

    # 5. Grammar & Structure Feedback
    if gram_score < 60:
        feedback_parts.append("Try using complete sentences and a clearer structure.")
    elif gram_score >= 85:
        feedback_parts.append("Well-structured phrasing with clear professional communication.")

    return " ".join(feedback_parts)
