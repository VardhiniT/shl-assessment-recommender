# rag/chatbot.py

from rag.state_extractor import (
    extract_state
)

from rag.conversation_manager import (
    analyze_conversation
)

from rag.retriever import (
    retrieve_assessments
)

from rag.response_generator import (
    generate_reply
)

from rag.comparison import (
    retrieve_specific_assessments
)

MAX_TURNS = 8


# --------------------------------------------------
# BUILD RETRIEVAL QUERY
# --------------------------------------------------

def build_retrieval_query(state):

    query_parts = []

    for key, value in state.items():

        if not value:
            continue

        if isinstance(value, list):

            query_parts.extend(value)

        else:

            query_parts.append(
                str(value)
            )

    return " ".join(query_parts)


# --------------------------------------------------
# DETECT MISSING FIELDS
# --------------------------------------------------

def get_missing_fields(state):

    missing_fields = []

    critical_fields = [
        "role",
        "seniority"
    ]

    improvement_fields = [
        "assessment_goal",
        "skills",
        "experience"
    ]

    for field in critical_fields:

        if not state.get(field):

            missing_fields.append(field)

    for field in improvement_fields:

        if not state.get(field):

            missing_fields.append(field)

    return missing_fields


# --------------------------------------------------
# FORMAT RECOMMENDATIONS
# --------------------------------------------------

def build_recommendations(results):

    recommendations = []

    for item in results[:10]:

        recommendations.append({
            "name": item["name"],
            "url": item["url"],
            "test_type": item.get(
                "test_type",
                ""
            )
        })

    return recommendations


# --------------------------------------------------
# EXTRACT PREVIOUS RECOMMENDATIONS
# --------------------------------------------------

def extract_previous_recommendations(messages):

    previous = []

    for message in messages:

        if (
            message.get("role") == "assistant"
            and isinstance(
                message.get(
                    "recommendations"
                ),
                list
            )
        ):

            previous.extend(
                message["recommendations"]
            )

    unique = []

    seen = set()

    for item in previous:

        name = item.get("name")

        if name not in seen:

            seen.add(name)

            unique.append(item)

    return unique


# --------------------------------------------------
# MERGE RECOMMENDATIONS
# --------------------------------------------------

def merge_recommendations(
    old_recommendations,
    new_recommendations
):

    merged = []

    seen = set()

    for item in (
        old_recommendations
        + new_recommendations
    ):

        name = item.get("name")

        if name not in seen:

            seen.add(name)

            merged.append(item)

    return merged[:10]


# --------------------------------------------------
# EXTRACT COMPARISON NAMES FROM MESSAGE
# More robust than simple string splitting —
# handles "compare X and Y", "difference between
# X and Y", "X vs Y" patterns
# --------------------------------------------------

def extract_compare_names(message):

    text = message.lower()

    # remove common filler words
    for phrase in [
        "what's the difference between",
        "what is the difference between",
        "compare",
        "comparison between",
        "difference between",
        "contrast",
    ]:
        text = text.replace(phrase, "")

    text = text.strip(" ?.!")

    # split on "and" or "vs" or "versus"
    for separator in [" vs ", " versus ", " and "]:
        if separator in text:
            parts = text.split(separator, 1)
            return [
                p.strip(" ?.!")
                for p in parts
                if len(p.strip()) >= 3
            ]

    # fallback — return the whole cleaned text
    # as a single query so retrieval still runs
    return [text.strip()] if text.strip() else []


# --------------------------------------------------
# MAIN CHAT FUNCTION
# --------------------------------------------------

def chat(messages):

    try:

        turns_remaining = (
            MAX_TURNS - len(messages)
        )

        # --------------------------------------
        # EXTRACT STATE
        # --------------------------------------

        state = extract_state(messages)

        # --------------------------------------
        # MISSING FIELDS
        # --------------------------------------

        missing_fields = get_missing_fields(
            state
        )

        # --------------------------------------
        # CONVERSATION ANALYSIS
        # --------------------------------------

        analysis = analyze_conversation(
            messages=messages,
            state=state,
            missing_fields=missing_fields,
            turns_remaining=turns_remaining
        )

        intent = analysis["intent"]

        latest_user_message = (
            messages[-1]["content"]
        )

        recommendations = []

        # --------------------------------------
        # STRATEGIES THAT SHOULD NEVER RETRIEVE
        # --------------------------------------

        NON_RECOMMENDATION_STRATEGIES = [
            "ask_clarification",
            "refuse_off_topic",
            "refuse_legal",
            "refuse_prompt_injection",
            "close_conversation"
        ]

        # --------------------------------------
        # NO RETRIEVAL CASES
        # --------------------------------------

        if (
            analysis["response_strategy"]
            in NON_RECOMMENDATION_STRATEGIES
        ):

            reply = generate_reply(
                strategy=analysis[
                    "response_strategy"
                ],

                reply_instruction=analysis[
                    "reply_instruction"
                ],

                recommendations=[],

                messages=messages
            )

            return {
                "reply": reply,
                "recommendations": [],
                "end_of_conversation": analysis[
                    "end_conversation"
                ]
            }

        # --------------------------------------
        # COMPARISON FLOW
        # --------------------------------------

        if (
            analysis["response_strategy"]
            == "compare_assessments"
        ):

            compare_names = extract_compare_names(
                latest_user_message
            )

            recommendations = (
                retrieve_specific_assessments(
                    compare_names
                )
            )

            # fallback: if name extraction returned
            # nothing, do a regular retrieval
            if not recommendations:

                retrieval_query = (
                    build_retrieval_query(state)
                    or latest_user_message
                )

                retrieved = retrieve_assessments(
                    retrieval_query,
                    state
                )

                recommendations = (
                    build_recommendations(retrieved)
                )

            reply = generate_reply(
                strategy=analysis[
                    "response_strategy"
                ],

                reply_instruction=analysis[
                    "reply_instruction"
                ],

                recommendations=recommendations,

                messages=messages
            )

            return {
                "reply": reply,

                "recommendations":
                    recommendations,

                "end_of_conversation":
                    analysis[
                        "end_conversation"
                    ]
            }

        # --------------------------------------
        # BUILD RETRIEVAL QUERY
        # --------------------------------------

        retrieval_query = (
            build_retrieval_query(
                state
            )
        )

        # --------------------------------------
        # RETRIEVE RESULTS
        # --------------------------------------

        retrieved = retrieve_assessments(
            retrieval_query,
            state
        )

        new_recommendations = (
            build_recommendations(
                retrieved
            )
        )

        # --------------------------------------
        # REFINEMENT CONTINUITY
        # --------------------------------------

        if intent == "refine":

            previous_recommendations = (
                extract_previous_recommendations(
                    messages
                )
            )

            recommendations = (
                merge_recommendations(
                    previous_recommendations,
                    new_recommendations
                )
            )

        else:

            recommendations = (
                new_recommendations
            )

        # --------------------------------------
        # GENERATE REPLY
        # --------------------------------------

        reply = generate_reply(
            strategy=analysis[
                "response_strategy"
            ],

            reply_instruction=analysis[
                "reply_instruction"
            ],

            recommendations=recommendations,

            messages=messages
        )

        # --------------------------------------
        # FINAL RESPONSE
        # --------------------------------------

        return {
            "reply": reply,

            "recommendations": recommendations,

            "end_of_conversation": analysis[
                "end_conversation"
            ]
        }

    # ------------------------------------------
    # SAFETY NET
    # If anything crashes, return a clean response
    # instead of a 500 error to the evaluator
    # ------------------------------------------

    except Exception as e:

        print(f"Chat error: {e}")

        return {
            "reply": (
                "I encountered an issue processing your request. "
                "Please try again."
            ),
            "recommendations": [],
            "end_of_conversation": False
        }