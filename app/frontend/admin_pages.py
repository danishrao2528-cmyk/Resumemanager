import streamlit as st

from api import (
    ai_candidate_search,
    delete_candidate,
    get_admin_stats,
    get_all_resumes,
    get_candidate,
    get_candidates,
    show_api_error,
)


# =========================================================
# DELETE CANDIDATE
# =========================================================

def _confirm_delete(
    user_id: int,
    full_name: str,
    key_prefix: str,
):

    st.error(
        f"⚠️ Delete {full_name} "
        "and their resume permanently?"
    )

    confirm = st.checkbox(
        "I understand this cannot be undone",
        key=(
            f"{key_prefix}_confirm_"
            f"{user_id}"
        ),
    )

    if st.button(
        "🗑️ Delete Candidate",
        key=(
            f"{key_prefix}_delete_"
            f"{user_id}"
        ),
        type="primary",
    ):

        if not confirm:
            st.warning(
                "Confirm the deletion first."
            )
            return

        response = delete_candidate(
            user_id
        )

        if (
            response is not None
            and response.status_code
            == 204
        ):
            st.success(
                "Candidate and resume deleted."
            )

            st.session_state.candidate_detail = (
                None
            )

            st.rerun()

        show_api_error(
            response
        )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

def admin_dashboard():

    st.caption(
        "🛡️ ADMIN WORKSPACE"
    )

    st.title(
        f"Welcome back, "
        f"{st.session_state.full_name} 👋"
    )

    st.write(
        "Review candidate activity, browse "
        "submitted resumes, and find strong "
        "matches using AI-assisted search."
    )

    st.divider()

    # ==========================================
    # GET STATISTICS
    # ==========================================

    response = get_admin_stats()

    if (
        response is None
        or response.status_code != 200
    ):
        show_api_error(response)
        return

    stats = response.json()

    total = stats[
        "total_candidates"
    ]

    with_resume = stats[
        "candidates_with_resume"
    ]

    without_resume = stats[
        "candidates_without_resume"
    ]

    # ==========================================
    # DASHBOARD CARDS
    # ==========================================

    c1, c2, c3 = st.columns(3)

    with c1:
        with st.container(
            border=True
        ):
            st.markdown(
                "### 👥 Candidates"
            )

            st.metric(
                "Total registered",
                total,
            )

            st.caption(
                "Candidate accounts"
            )

    with c2:
        with st.container(
            border=True
        ):
            st.markdown(
                "### 📄 Resume Ready"
            )

            st.metric(
                "With resume",
                with_resume,
            )

            st.caption(
                "Ready for recruitment search"
            )

    with c3:
        with st.container(
            border=True
        ):
            st.markdown(
                "### ⏳ Pending"
            )

            st.metric(
                "Without resume",
                without_resume,
            )

            st.caption(
                "Candidates still incomplete"
            )

    # ==========================================
    # RECRUITMENT READINESS
    # ==========================================

    st.write("")

    st.subheader(
        "📊 Recruitment readiness"
    )

    if total > 0:
        completion = (
            with_resume / total
        )

    else:
        completion = 0

    st.progress(
        completion
    )

    st.caption(
        f"{round(completion * 100)}% "
        "of candidates have submitted "
        "a resume."
    )

    # ==========================================
    # QUICK ACTIONS
    # ==========================================

    st.write("")

    st.subheader(
        "⚡ Quick actions"
    )

    q1, q2, q3 = st.columns(3)

    with q1:
        with st.container(
            border=True
        ):
            st.markdown(
                "### 👥 Candidates"
            )

            st.write(
                "Review candidate accounts, "
                "resume status, and details."
            )

            st.info(
                "Open **Candidates** "
                "from the sidebar."
            )

    with q2:
        with st.container(
            border=True
        ):
            st.markdown(
                "### 📄 All Resumes"
            )

            st.write(
                "Browse every submitted "
                "candidate resume."
            )

            st.info(
                "Open **All Resumes** "
                "from the sidebar."
            )

    with q3:
        with st.container(
            border=True
        ):
            st.markdown(
                "### ✨ AI Search"
            )

            st.write(
                "Describe a hiring requirement "
                "and rank suitable candidates."
            )

            st.info(
                "Open **AI Candidate Search** "
                "from the sidebar."
            )


# =========================================================
# CANDIDATES PAGE
# =========================================================

def candidates_page():

    st.caption(
        "👥 ADMIN WORKSPACE"
    )

    st.title(
        "Candidates"
    )

    st.write(
        "Review candidate accounts, resume "
        "status, and profile details."
    )

    st.divider()

    # ==========================================
    # GET CANDIDATES
    # ==========================================

    response = get_candidates()

    if (
        response is None
        or response.status_code != 200
    ):
        show_api_error(response)
        return

    candidates = response.json()

    if not candidates:
        st.info(
            "No candidates registered yet."
        )
        return

    # ==========================================
    # PAGE METRICS
    # ==========================================

    ready = sum(
        1
        for candidate in candidates
        if candidate["has_resume"]
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        with st.container(
            border=True
        ):
            st.metric(
                "👥 Total Candidates",
                len(candidates),
            )

    with c2:
        with st.container(
            border=True
        ):
            st.metric(
                "📄 Resume Ready",
                ready,
            )

    with c3:
        with st.container(
            border=True
        ):
            st.metric(
                "⏳ Pending Resume",
                len(candidates) - ready,
            )

    st.write("")

    # ==========================================
    # CANDIDATE LIST
    # ==========================================

    for candidate in candidates:

        with st.container(
            border=True
        ):

            info, status, action = (
                st.columns(
                    [4, 2, 1],
                    vertical_alignment="center",
                )
            )

            with info:

                st.markdown(
                    f"### 👤 "
                    f"{candidate['full_name']}"
                )

                st.caption(
                    f"@{candidate['username']}  "
                    f"•  {candidate['email']}"
                )

            with status:

                if candidate[
                    "has_resume"
                ]:
                    st.success(
                        "✅ Resume Ready"
                    )

                else:
                    st.warning(
                        "⏳ No Resume"
                    )

            with action:

                if st.button(
                    "👁️ View",
                    key=(
                        "view_candidate_"
                        f"{candidate['id']}"
                    ),
                    use_container_width=True,
                ):

                    detail_response = (
                        get_candidate(
                            candidate["id"]
                        )
                    )

                    if (
                        detail_response
                        is not None
                        and
                        detail_response.status_code
                        == 200
                    ):
                        st.session_state[
                            "candidate_detail"
                        ] = (
                            detail_response.json()
                        )

                    else:
                        show_api_error(
                            detail_response
                        )

    # ==========================================
    # SELECTED CANDIDATE
    # ==========================================

    detail = (
        st.session_state.get(
            "candidate_detail"
        )
    )

    if detail:

        st.divider()

        st.subheader(
            "🔎 Candidate Detail"
        )

        with st.container(
            border=True
        ):

            c1, c2, c3 = (
                st.columns(3)
            )

            c1.metric(
                "👤 Name",
                detail["full_name"],
            )

            c2.metric(
                "🔑 Username",
                detail["username"],
            )

            c3.metric(
                "🛡️ Role",
                detail["role"].title(),
            )

            st.write(
                f"✉️ **Email:** "
                f"{detail['email']}"
            )

            if detail.get(
                "resume_text"
            ):

                st.subheader(
                    "📄 Resume"
                )

                st.text_area(
                    "Full resume",
                    value=detail[
                        "resume_text"
                    ],
                    height=300,
                    disabled=True,
                    key=(
                        "candidate_resume_"
                        f"{detail['id']}"
                    ),
                )

            else:
                st.info(
                    "This candidate has not "
                    "created a resume yet."
                )

        with st.expander(
            "⚠️ Danger zone"
        ):
            _confirm_delete(
                detail["id"],
                detail["full_name"],
                "candidate_page",
            )


# =========================================================
# ALL RESUMES PAGE
# =========================================================

def all_resumes_page():

    st.caption(
        "📄 ADMIN WORKSPACE"
    )

    st.title(
        "All Resumes"
    )

    st.write(
        "Browse every resume submitted "
        "by registered candidates."
    )

    st.divider()

    response = get_all_resumes()

    if (
        response is None
        or response.status_code != 200
    ):
        show_api_error(response)
        return

    resumes = response.json()

    if not resumes:
        st.info(
            "No resumes have been "
            "submitted yet."
        )
        return

    # ==========================================
    # SUMMARY
    # ==========================================

    with st.container(
        border=True
    ):
        st.metric(
            "📄 Submitted Resumes",
            len(resumes),
        )

    st.write("")

    # ==========================================
    # RESUME LIST
    # ==========================================

    for resume in resumes:

        title = (
            f"📄 {resume['full_name']} "
            f"• Resume #{resume['id']}"
        )

        with st.expander(
            title
        ):

            c1, c2 = st.columns(2)

            with c1:
                st.write(
                    f"✉️ **Email:** "
                    f"{resume['email']}"
                )

            with c2:
                st.write(
                    f"👤 **Username:** "
                    f"@{resume['username']}"
                )

            st.divider()

            st.markdown(
                "### 📄 Resume Text"
            )

            st.write(
                resume["resume_text"]
            )


# =========================================================
# AI CANDIDATE SEARCH
# =========================================================

def ai_search_page():

    st.caption(
        "✨ ADMIN WORKSPACE"
    )

    st.title(
        "AI Candidate Search"
    )

    st.write(
        "Describe the candidate you need and "
        "let AI rank the strongest resume matches."
    )

    st.divider()

    # ==========================================
    # SEARCH FORM
    # ==========================================

    with st.container(
        border=True
    ):

        st.subheader(
            "🔎 Candidate requirement"
        )

        st.caption(
            "Describe skills, technologies, "
            "experience, or role requirements "
            "using natural language."
        )

        requirement = (
            st.text_area(
                "What kind of candidate "
                "are you looking for?",
                height=150,
                placeholder=(
                    "Example: I need a Python "
                    "backend developer with FastAPI, "
                    "PostgreSQL, Docker and REST API "
                    "experience."
                ),
            )
        )

        search = st.button(
            "✨ Find Candidates",
            type="primary",
            use_container_width=True,
        )

    # ==========================================
    # RUN SEARCH
    # ==========================================

    if search:

        if (
            len(
                requirement.strip()
            )
            < 10
        ):
            st.warning(
                "Describe your requirement "
                "in a little more detail."
            )

        else:

            with st.spinner(
                "✨ AI is comparing your "
                "requirement with candidate "
                "resumes..."
            ):

                response = (
                    ai_candidate_search(
                        requirement.strip()
                    )
                )

            if (
                response is not None
                and response.status_code
                == 200
            ):
                st.session_state[
                    "ai_results"
                ] = response.json()

                st.session_state[
                    "show_all_ai"
                ] = False

            else:
                show_api_error(
                    response
                )

    # ==========================================
    # GET RESULTS
    # ==========================================

    results = (
        st.session_state.get(
            "ai_results"
        )
    )

    if not results:

        st.info(
            "💡 Enter a job requirement "
            "above to start matching candidates."
        )

        return

    st.write("")

    st.subheader(
        "🎯 Search results"
    )

    # ==========================================
    # EXTRACTED KEYWORDS
    # ==========================================

    keywords = results.get(
        "extracted_keywords",
        [],
    )

    if keywords:

        with st.container(
            border=True
        ):

            st.markdown(
                "#### 🔑 Extracted requirements"
            )

            st.write(
                " • ".join(
                    keywords
                )
            )

    # ==========================================
    # MATCHES
    # ==========================================

    matches = results.get(
        "matches",
        [],
    )

    if not matches:

        st.info(
            "No meaningful candidates "
            "scored 60/100 or higher."
        )

        return

    st.success(
        f"✅ Found {len(matches)} "
        f"candidate match"
        f"{'es' if len(matches) != 1 else ''} "
        "scoring 60/100 or higher."
    )

    if st.session_state.get(
        "show_all_ai"
    ):
        visible = matches

    else:
        visible = matches[:10]

    # ==========================================
    # MATCH CARDS
    # ==========================================

    for index, match in enumerate(
        visible,
        start=1,
    ):

        with st.container(
            border=True
        ):

            info, score = (
                st.columns(
                    [4, 1],
                    vertical_alignment="center",
                )
            )

            with info:

                if index == 1:
                    medal = "🥇"

                elif index == 2:
                    medal = "🥈"

                elif index == 3:
                    medal = "🥉"

                else:
                    medal = "👤"

                st.subheader(
                    f"{medal} #{index} "
                    f"{match['full_name']}"
                )

                st.caption(
                    match["email"]
                )

            with score:

                st.metric(
                    "Match Score",
                    (
                        f"{match['match_score']}"
                        "/100"
                    ),
                )

            # ==================================
            # SCORE BAR
            # ==================================

            st.progress(
                match[
                    "match_score"
                ] / 100
            )

            # ==================================
            # RECOMMENDATION
            # ==================================

            if (
                match[
                    "recommendation"
                ]
                == "Recommended"
            ):

                st.success(
                    "✅ Recommended"
                )

            else:

                st.warning(
                    "⚠️ "
                    f"{match['recommendation']}"
                )

            # ==================================
            # AI REASON
            # ==================================

            st.markdown(
                "#### 💬 AI Assessment"
            )

            st.write(
                match["reason"]
            )

            # ==================================
            # SKILLS
            # ==================================

            c1, c2 = st.columns(2)

            with c1:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        "#### ✅ Matched Skills"
                    )

                    matched = (
                        match[
                            "matched_skills"
                        ]
                    )

                    if matched:
                        for skill in matched:
                            st.write(
                                f"✓ {skill}"
                            )

                    else:
                        st.write("—")

            with c2:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        "#### ⚠️ Missing Skills"
                    )

                    missing = (
                        match[
                            "missing_skills"
                        ]
                    )

                    if missing:
                        for skill in missing:
                            st.write(
                                f"• {skill}"
                            )

                    else:
                        st.write(
                            "✅ No missing skills"
                        )

            # ==================================
            # VIEW RESUME
            # ==================================

            if st.button(
                "👁️ View Candidate Resume",
                key=(
                    "ai_view_"
                    f"{match['user_id']}"
                ),
            ):

                detail_response = (
                    get_candidate(
                        match["user_id"]
                    )
                )

                if (
                    detail_response
                    is not None
                    and
                    detail_response.status_code
                    == 200
                ):

                    st.session_state[
                        "candidate_detail"
                    ] = (
                        detail_response.json()
                    )

                else:
                    show_api_error(
                        detail_response
                    )

            # ==================================
            # CANDIDATE DETAIL
            # ==================================

            current_detail = (
                st.session_state.get(
                    "candidate_detail"
                )
                or {}
            )

            if (
                current_detail.get(
                    "id"
                )
                == match["user_id"]
            ):

                detail = (
                    st.session_state[
                        "candidate_detail"
                    ]
                )

                with st.expander(
                    "📄 Candidate Detail",
                    expanded=True,
                ):

                    st.write(
                        f"**Username:** "
                        f"@{detail['username']}"
                    )

                    st.write(
                        f"**Email:** "
                        f"{detail['email']}"
                    )

                    if detail.get(
                        "resume_text"
                    ):

                        st.text_area(
                            "Full resume",
                            value=detail[
                                "resume_text"
                            ],
                            height=280,
                            disabled=True,
                            key=(
                                "ai_resume_"
                                f"{detail['id']}"
                            ),
                        )

                    with st.expander(
                        "⚠️ Candidate management"
                    ):

                        _confirm_delete(
                            detail["id"],
                            detail[
                                "full_name"
                            ],
                            "ai_page",
                        )

    # ==========================================
    # SHOW MORE
    # ==========================================

    if (
        len(matches) > 10
        and
        not st.session_state.get(
            "show_all_ai"
        )
    ):

        if st.button(
            f"Show More "
            f"({len(matches) - 10} more)",
            use_container_width=True,
        ):

            st.session_state[
                "show_all_ai"
            ] = True

            st.rerun()