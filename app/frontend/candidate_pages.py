import streamlit as st

from api import (
    create_my_resume,
    get_my_resume,
    show_api_error,
    update_my_resume,
)


def _resume_response():
    response = get_my_resume()

    if response is None:
        return None, None

    if response.status_code == 200:
        return response.json(), response

    if response.status_code == 404:
        return None, response

    return None, response


def candidate_dashboard():
    resume, response = _resume_response()

    has_resume = resume is not None

    st.caption("👤 CANDIDATE WORKSPACE")

    st.title(
        f"Welcome, {st.session_state.full_name} 👋"
    )

    st.write(
        "Manage your professional resume and keep "
        "your candidate profile ready for "
        "administrator searches."
    )

    st.divider()

    # ==========================================
    # PROFILE CARDS
    # ==========================================

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.markdown("### 👤 Profile")

            st.caption("Full Name")

            st.markdown(
                f"## {st.session_state.full_name}"
            )

            st.caption(
                f"Username: @{st.session_state.username}"
            )

    with col2:
        with st.container(border=True):
            st.markdown("### ✉️ Account")

            st.markdown(
                f"**{st.session_state.email}**"
            )

            st.caption(
                "Candidate account"
            )

            st.caption(
                "Profile details are read-only"
            )

    with col3:
        with st.container(border=True):
            st.markdown("### 📄 Resume")

            st.caption("Status")

            if has_resume:
                st.markdown(
                    "## ✅ Created"
                )

                st.caption(
                    "Your resume is searchable "
                    "by administrators."
                )

            else:
                st.markdown(
                    "## ⏳ Not Created"
                )

                st.caption(
                    "Create your resume to "
                    "become searchable."
                )

    # ==========================================
    # API ERROR HANDLING
    # ==========================================

    if response is None:
        st.warning(
            "API connection unavailable."
        )

    elif response.status_code not in (
        200,
        404,
    ):
        show_api_error(response)

    # ==========================================
    # CANDIDATE READINESS
    # ==========================================

    st.write("")

    st.subheader(
        "📊 Candidate readiness"
    )

    readiness = (
        100
        if has_resume
        else 55
    )

    st.progress(
        readiness / 100
    )

    st.caption(
        f"Candidate readiness: {readiness}%"
    )

    st.write("")

    # ==========================================
    # RESUME ACTION
    # ==========================================

    with st.container(border=True):

        if has_resume:
            st.subheader(
                "✅ Your candidate profile is ready"
            )

            st.write(
                "Your resume has been created and "
                "can be discovered through "
                "administrator searches and "
                "AI Candidate Search."
            )

            st.success(
                "Your resume is currently active."
            )

            st.info(
                "📄 Open **My Resume** from the "
                "sidebar whenever you want to "
                "review or update it."
            )

        else:
            st.subheader(
                "🚀 Complete your candidate profile"
            )

            st.write(
                "You have not created your resume yet. "
                "Add it once and you can update the "
                "same resume whenever needed."
            )

            st.warning(
                "Your candidate profile is not "
                "searchable until you create a resume."
            )

            st.info(
                "📄 Open **My Resume** from the "
                "sidebar to create your first resume."
            )


def my_resume_page():
    resume, response = _resume_response()

    st.caption(
        "📄 CANDIDATE WORKSPACE"
    )

    st.title(
        "My Resume"
    )

    st.write(
        "Create, review, and update the resume "
        "attached to your account."
    )

    st.divider()

    # ==========================================
    # API CHECK
    # ==========================================

    if response is None:
        st.error(
            "Unable to connect to API."
        )
        return

    if response.status_code not in (
        200,
        404,
    ):
        show_api_error(response)
        return

    # ==========================================
    # CREATE RESUME
    # ==========================================

    if resume is None:

        left, right = st.columns(
            [2, 1]
        )

        with left:
            with st.container(
                border=True
            ):
                st.subheader(
                    "➕ Create your resume"
                )

                st.caption(
                    "Paste or type your complete "
                    "professional resume below."
                )

                with st.form(
                    "create_my_resume"
                ):
                    resume_text = st.text_area(
                        "Resume text",
                        height=360,
                        placeholder=(
                            "Example:\n\n"
                            "Danish Ali\n"
                            "Python Backend Developer\n\n"
                            "Professional Summary:\n"
                            "Backend developer experienced "
                            "with FastAPI and SQLAlchemy.\n\n"
                            "Skills:\n"
                            "Python, FastAPI, SQLAlchemy, "
                            "PostgreSQL, Docker, Git"
                        ),
                    )

                    submitted = (
                        st.form_submit_button(
                            "📄 Create My Resume",
                            type="primary",
                            use_container_width=True,
                        )
                    )

                if submitted:

                    if (
                        len(
                            resume_text.strip()
                        )
                        < 10
                    ):
                        st.warning(
                            "Resume text must be "
                            "at least 10 characters."
                        )
                        return

                    create_response = (
                        create_my_resume(
                            resume_text.strip()
                        )
                    )

                    if (
                        create_response
                        is not None
                        and
                        create_response.status_code
                        == 201
                    ):
                        st.success(
                            "Resume created successfully."
                        )

                        st.rerun()

                    show_api_error(
                        create_response
                    )

        with right:
            with st.container(
                border=True
            ):
                st.subheader(
                    "💡 Resume tips"
                )

                st.write(
                    "✅ Add a professional summary"
                )

                st.write(
                    "✅ List your strongest skills"
                )

                st.write(
                    "✅ Include projects"
                )

                st.write(
                    "✅ Add work experience"
                )

                st.write(
                    "✅ Mention frameworks and tools"
                )

                st.write(
                    "✅ Keep information relevant"
                )

            with st.container(
                border=True
            ):
                st.subheader(
                    "✨ AI Search Tip"
                )

                st.caption(
                    "Administrators search candidates "
                    "based on skills mentioned in "
                    "your resume."
                )

                st.info(
                    "Mention technologies you actually "
                    "know, such as FastAPI, Docker, "
                    "PostgreSQL, Git, or AWS."
                )

        return

    # ==========================================
    # EXISTING RESUME
    # ==========================================

    top1, top2, top3 = st.columns(
        3
    )

    with top1:
        with st.container(
            border=True
        ):
            st.metric(
                "📄 Resume Status",
                "Active",
            )

    with top2:
        with st.container(
            border=True
        ):
            st.metric(
                "👤 Candidate",
                resume["full_name"],
            )

    with top3:
        with st.container(
            border=True
        ):
            st.metric(
                "🔑 Username",
                st.session_state.username,
            )

    st.success(
        "✅ Your resume is available to "
        "administrators and AI Candidate Search."
    )

    st.write("")

    # ==========================================
    # VIEW / EDIT TABS
    # ==========================================

    tab1, tab2 = st.tabs(
        [
            "👁️ View Resume",
            "✏️ Edit Resume",
        ]
    )

    with tab1:
        with st.container(
            border=True
        ):
            st.markdown(
                f"### 👤 {resume['full_name']}"
            )

            st.caption(
                resume["email"]
            )

            st.text_area(
                "Current resume",
                value=resume[
                    "resume_text"
                ],
                height=350,
                disabled=True,
                key="current_resume_view",
            )

    with tab2:
        with st.container(
            border=True
        ):
            st.markdown(
                "### ✏️ Update Resume"
            )

            st.caption(
                "Edit the existing resume "
                "and save your changes."
            )

            with st.form(
                "update_my_resume"
            ):
                updated_text = (
                    st.text_area(
                        "Edit resume text",
                        value=resume[
                            "resume_text"
                        ],
                        height=350,
                    )
                )

                save = (
                    st.form_submit_button(
                        "💾 Save Changes",
                        type="primary",
                        use_container_width=True,
                    )
                )

            if save:

                if (
                    len(
                        updated_text.strip()
                    )
                    < 10
                ):
                    st.warning(
                        "Resume text must be "
                        "at least 10 characters."
                    )
                    return

                update_response = (
                    update_my_resume(
                        updated_text.strip()
                    )
                )

                if (
                    update_response
                    is not None
                    and
                    update_response.status_code
                    == 200
                ):
                    st.success(
                        "Resume updated successfully."
                    )

                    st.rerun()

                show_api_error(
                    update_response
                )