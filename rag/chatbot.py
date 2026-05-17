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
# MAIN CHAT FUNCTION
# --------------------------------------------------

def chat(messages):

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

        latest_message = (
            messages[-1]["content"]
        )

        lower_message = (
            latest_message.lower()
            .replace("compare", "")
            .replace(".", "")
        )

        compare_names = []

        if " and " in lower_message:

            compare_names = [
                x.strip()
                for x in lower_message.split(
                    " and "
                )
            ]

        recommendations = (
            retrieve_specific_assessments(
                compare_names
            )
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