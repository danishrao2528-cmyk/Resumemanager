import streamlit as st

from api import (
    analyze_resume,
    create_resume,
    delete_resume,
    get_all_resumes,
    get_resume,
    show_api_error,
    update_resume,
)


def show_all_resumes():

    st.title("All Resumes")

    response = get_all_resumes()

    if response is None:
        st.error("Unable to connect to API.")
        return

    if response.status_code != 200:
        show_api_error(response)
        return

    resumes = response.json()

    if not resumes:
        st.info("No resumes found.")
        return

    st.success(
        f"{len(resumes)} resume(s) found."
    )

    for resume in resumes:

        title = (
            f"{resume['candidate_name']} "
            f"- ID {resume['id']}"
        )

        with st.expander(title):

            st.write(
                f"**Email:** {resume['email']}"
            )

            st.write(
                "**Resume Text:**"
            )

            st.write(
                resume["resume_text"]
            )


def create_resume_page():

    st.title("Add Resume")

    with st.form(
        "create_resume_form"
    ):

        candidate_name = st.text_input(
            "Candidate Name"
        )

        email = st.text_input(
            "Email"
        )

        resume_text = st.text_area(
            "Resume Text",
            height=250,
        )

        submit = st.form_submit_button(
            "Create Resume",
            type="primary",
        )


    if not submit:
        return


    if (
        not candidate_name
        or not email
        or not resume_text
    ):

        st.warning(
            "All fields are required."
        )

        return


    payload = {
        "candidate_name": candidate_name,
        "email": email,
        "resume_text": resume_text,
    }


    response = create_resume(
        payload
    )


    if response is None:

        st.error(
            "Unable to connect to API."
        )

        return


    if response.status_code == 201:

        result = response.json()

        st.success(
            "Resume created successfully."
        )

        st.write(
            f"Resume ID: {result['id']}"
        )

    else:

        show_api_error(response)


def search_resume_page():

    st.title("Find Resume")

    resume_id = st.number_input(
        "Resume ID",
        min_value=1,
        step=1,
    )


    if not st.button(
        "Search",
        type="primary",
    ):
        return


    response = get_resume(
        resume_id
    )


    if response is None:

        st.error(
            "Unable to connect to API."
        )

        return


    if response.status_code != 200:

        show_api_error(response)
        return


    resume = response.json()


    with st.container(
        border=True
    ):

        st.subheader(
            resume["candidate_name"]
        )

        st.write(
            f"**ID:** {resume['id']}"
        )

        st.write(
            f"**Email:** {resume['email']}"
        )

        st.write(
            resume["resume_text"]
        )


def update_resume_page():

    st.title(
        "Update Resume"
    )

    resume_id = st.number_input(
        "Resume ID",
        min_value=1,
        step=1,
        key="update_id",
    )


    if st.button(
        "Load Resume"
    ):

        response = get_resume(
            resume_id
        )

        if response is None:

            st.error(
                "Unable to connect to API."
            )

        elif response.status_code == 200:

            st.session_state.update_resume = (
                response.json()
            )

        else:

            show_api_error(
                response
            )


    resume = st.session_state.get(
        "update_resume"
    )


    if not resume:
        return


    with st.form(
        "update_resume_form"
    ):

        candidate_name = st.text_input(
            "Candidate Name",
            value=resume["candidate_name"],
        )

        email = st.text_input(
            "Email",
            value=resume["email"],
        )

        resume_text = st.text_area(
            "Resume Text",
            value=resume["resume_text"],
            height=250,
        )

        submit = st.form_submit_button(
            "Update Resume",
            type="primary",
        )


    if not submit:
        return


    payload = {
        "candidate_name": candidate_name,
        "email": email,
        "resume_text": resume_text,
    }


    response = update_resume(
        resume_id,
        payload,
    )


    if response is None:

        st.error(
            "Unable to connect to API."
        )

    elif response.status_code == 200:

        st.success(
            "Resume updated successfully."
        )

        st.session_state.update_resume = (
            response.json()
        )

    else:

        show_api_error(
            response
        )


def delete_resume_page():

    st.title(
        "Delete Resume"
    )

    st.warning(
        "This action permanently deletes the resume."
    )

    resume_id = st.number_input(
        "Resume ID",
        min_value=1,
        step=1,
        key="delete_id",
    )

    confirm = st.checkbox(
        "I confirm this deletion."
    )


    if not st.button(
        "Delete Resume",
        type="primary",
    ):

        return


    if not confirm:

        st.warning(
            "Confirm the deletion first."
        )

        return


    response = delete_resume(
        resume_id
    )


    if response is None:

        st.error(
            "Unable to connect to API."
        )

    elif response.status_code == 204:

        st.success(
            "Resume deleted successfully."
        )

    else:

        show_api_error(
            response
        )


def ai_analysis_page():

    st.title(
        "AI Resume Analysis"
    )

    resume_id = st.number_input(
        "Resume ID",
        min_value=1,
        step=1,
        key="analysis_id",
    )


    if not st.button(
        "Analyze Resume",
        type="primary",
    ):

        return


    with st.spinner(
        "Analyzing resume..."
    ):

        response = analyze_resume(
            resume_id
        )


    if response is None:

        st.error(
            "Unable to connect to API."
        )

        return


    if response.status_code != 200:

        show_api_error(response)

        return


    result = response.json()

    analysis = result.get(
        "analysis",
        {},
    )


    st.success(
        "Analysis completed."
    )


    st.subheader(
        result.get(
            "candidate_name",
            "Candidate",
        )
    )


    if not isinstance(
        analysis,
        dict,
    ):

        st.write(
            analysis
        )

        return


    score = analysis.get(
        "score",
        "N/A",
    )


    st.metric(
        "ATS Score",
        f"{score}/100",
    )


    col1, col2 = st.columns(2)


    with col1:

        st.subheader(
            "Strengths"
        )

        for item in analysis.get(
            "strengths",
            [],
        ):

            st.write(
                f"- {item}"
            )


    with col2:

        st.subheader(
            "Missing Skills"
        )

        for item in analysis.get(
            "missing_skills",
            [],
        ):

            st.write(
                f"- {item}"
            )


    st.subheader(
        "Summary"
    )

    st.info(
        analysis.get(
            "summary",
            "No summary returned.",
        )
    )