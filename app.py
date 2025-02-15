import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import os
import json
import uuid

if not firebase_admin._apps:
    CredentialCertificate = os.environ.get('CREDENTIALCERTIFICATE')
    firebase_credentials_dict = json.loads(CredentialCertificate)
    cred = credentials.Certificate(firebase_credentials_dict)  # Replace with your Firebase credentials file
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://ecommerceimg-6ecf3-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

# Fetch job domains from Firebasee
def fetch_job_domains():
    job_domains = []
    jobs_ref = db.reference("jobs").get()
    if jobs_ref:
        for company_name, jobs in jobs_ref.items():
            for job_id, job_details in jobs.items():
                domain = job_details['domain'].lower()
                if domain not in job_domains:
                    job_domains.append(domain)
    return job_domains

# Initialize session state
if 'user_state' not in st.session_state:
    st.session_state.user_state = {'step': -1, 'role': None, 'job_action': None, 'phone_number': None, 'selected_job': None}
if 'responses' not in st.session_state:
    st.session_state.responses = {}
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'inside' not in st.session_state:
    st.session_state.inside = 0
if 'all_jobs' not in st.session_state:
    st.session_state.all_jobs = []


# Streamlit app
def main():
    st.title("Job Portal Chatbot")
    st.write("Welcome to the Job Portal! 📱 Please enter your phone number to start.")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User input for phone number
    if st.session_state.user_state['step'] == -1:
        if "show_phone_input" not in st.session_state:
            st.session_state.show_phone_input = True

        if st.session_state.show_phone_input:
            if prompt := st.chat_input("📱Enter your phone number to start"):
                st.session_state.user_state['phone_number'] = prompt
                st.session_state.user_state['step'] = 0
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.session_state.messages.append({"role": "bot", "content": "👥 Are you an employer or an employee? (Type 'employer' or 'employee')"})
                st.session_state.show_phone_input = False  # Disable this input field
                st.rerun()

    # Role selection
    elif st.session_state.user_state['step'] == 0:
        if "show_role_input" not in st.session_state:
            st.session_state.show_role_input = True

        if st.session_state.show_role_input:
            if prompt := st.chat_input("👥 Type 'employer' or 'employee'"):
                if prompt.lower() in ["employer", "employee"]:
                    st.session_state.user_state['role'] = prompt.lower()
                    st.session_state.user_state['step'] = 1
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    if prompt.lower() == "employer":
                        st.session_state.messages.append({"role": "bot", "content": "Do you want to post a new job or manage existing ones? (Type 'post' or 'manage')"})
                    else:
                        st.session_state.messages.append({"role": "bot", "content": "Do you want to apply for a new job or manage applied ones? (Type 'apply' or 'manage')"})
                    st.session_state.show_role_input = False  # Disable this input field
                    st.rerun()
                else:
                    st.session_state.messages.append({"role": "bot", "content": "Invalid input. Please type 'employer' or 'employee'."})
                    st.rerun()

    # Employer flow
    elif st.session_state.user_state['step'] == 1 and st.session_state.user_state['role'] == "employer":
        if "show_employer_action_input" not in st.session_state:
            st.session_state.show_employer_action_input = True

        if st.session_state.show_employer_action_input:
            if prompt := st.chat_input("💼 Type 'post' or 'manage'"):
                if prompt.lower() == "post":
                    st.session_state.user_state['job_action'] = "post"
                    st.session_state.user_state['step'] = 2
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    st.session_state.messages.append({"role": "bot", "content": "Please fill out the job posting form."})
                    st.session_state.show_employer_action_input = False  # Disable this input field
                    st.rerun()
                elif prompt.lower() == "manage":
                    st.session_state.user_state['job_action'] = "manage"
                    st.session_state.user_state['step'] = 2
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    st.session_state.messages.append({"role": "bot", "content": "Fetching your posted jobs..."})
                    st.session_state.show_employer_action_input = False  # Disable this input field
                    st.rerun()
                else:
                    st.session_state.messages.append({"role": "bot", "content": "Invalid input. Please type 'post' or 'manage'."})
                    st.rerun()

    # Employee flow
    elif st.session_state.user_state['step'] == 1 and st.session_state.user_state['role'] == "employee":
        if "show_employee_action_input" not in st.session_state:
            st.session_state.show_employee_action_input = True

        if st.session_state.show_employee_action_input:
            if prompt := st.chat_input("💼 Type 'apply' or 'manage'"):
                if prompt.lower() == "apply":
                    st.session_state.user_state['job_action'] = "apply"
                    st.session_state.user_state['step'] = 2
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    st.session_state.messages.append({"role": "bot", "content": "Please fill out the job application form."})
                    st.session_state.show_employee_action_input = False  # Disable this input field
                    st.rerun()
                elif prompt.lower() == "manage":
                    st.session_state.user_state['job_action'] = "manage"
                    st.session_state.user_state['step'] = 2
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    st.session_state.messages.append({"role": "bot", "content": "🔍 Fetching your applied jobs..."})
                    st.session_state.show_employee_action_input = False  # Disable this input field
                    st.rerun()
                else:
                    st.session_state.messages.append({"role": "bot", "content": "Invalid input. Please type 'apply' or 'manage'."})
                    st.rerun()

    # Manage posted jobs for employer
    if st.session_state.user_state['step'] == 2 and st.session_state.user_state['role'] == "employer" and st.session_state.user_state['job_action'] == "manage":
        employer_number = st.session_state.user_state['phone_number']
        jobs_ref = db.reference("jobs").get()
        all_jobs = []  # Initialize all_jobs here
        if jobs_ref:
            for company_name, jobs in jobs_ref.items():
                for job_id, job_details in jobs.items():
                    if job_details.get("employer_number") == employer_number:
                        all_jobs.append((company_name, job_id, job_details))

        if not all_jobs:
            st.session_state.messages.append({"role": "bot", "content": "You haven't posted any jobs yet."})
            st.session_state.user_state['step'] = -1  # Restart from the beginning
            st.rerun()
        else:
            if st.session_state.inside == 0:
                st.session_state.all_jobs = all_jobs
                job_list = ""
                for idx, (company_name, job_id, job_details) in enumerate(all_jobs, start=1):
                    job_list += f"{idx}) Company Name: {company_name}, Job Role: {job_details['role']}\n"
                
                st.session_state.messages.append({"role": "bot", "content": f"Here are your posted jobs:\n{job_list}"})
                st.session_state.messages.append({"role": "bot", "content": "🔢 Please select a job by its serial number:"})
                st.session_state.inside += 1
                st.rerun()

            if "show_job_selection_input" not in st.session_state:
                st.session_state.show_job_selection_input = True

            if st.session_state.show_job_selection_input:
                if prompt := st.chat_input("🔢 Enter the serial number of the job"):
                    st.session_state.messages.append({"role": "user", "content": prompt})
                    try:
                        selected_index = int(prompt.strip()) - 1
                        if 0 <= selected_index < len(st.session_state.all_jobs):  # Ensure all_jobs is defined
                            st.session_state.user_state['selected_job'] = st.session_state.all_jobs[selected_index]
                            st.session_state.user_state['step'] = 3
                            st.session_state.show_job_selection_input = False  # Disable this input field
                            st.session_state.inside = 0
                            st.rerun()
                        else:
                            st.session_state.messages.append({"role": "bot", "content": "Invalid selection. Please try again."})
                            st.rerun()
                    except ValueError:
                        st.session_state.messages.append({"role": "bot", "content": "Please enter a valid number."})
                        st.rerun()

    # Job management options for employer
    if st.session_state.user_state['step'] == 3 and st.session_state.user_state['role'] == "employer":
        company_name, job_id, job_details = st.session_state.user_state['selected_job']

        if st.session_state.inside == 0:
            st.session_state.messages.append({"role": "bot", "content": f"Selected job: {job_details['role']} at {company_name}"})
            st.session_state.messages.append({"role": "bot", "content": "Please select an option:\n1) View applicant details\n2) Stop accepting applications\n3) Restart accepting applications"})
            st.session_state.inside += 1
            st.rerun()

        if "show_job_management_input" not in st.session_state:
            st.session_state.show_job_management_input = True

        if st.session_state.show_job_management_input:
            if prompt := st.chat_input("🔢 Enter 1, 2, or 3"):
                st.session_state.messages.append({"role": "user", "content": prompt})
                if prompt.strip() == "1":
                    # View applicant details
                    applicants = job_details.get("applicants", {})
                    if not applicants:
                        st.session_state.messages.append({"role": "bot", "content": "No applicants have applied for this role yet."})
                    else:
                        formatted_applicants_list = ""
                        for idx, (applicant_id, applicant_details) in enumerate(applicants.items()):
                            name = applicant_details.get("name", "N/A")
                            employee_number = applicant_details.get("employee_number", "N/A")
                            skills = applicant_details.get("skills", "N/A")
                            formatted_applicants_list += (f"{idx + 1}) Name: {name} ||"
                                                        f"   Employee Number: {employee_number} ||"
                                                        f"   Skills: {skills}\n\n")
                        st.session_state.messages.append({"role": "bot", "content": f"Here are the applicant details:\n{formatted_applicants_list.strip()}"})
                    st.session_state.user_state['step'] = -1  # Restart from the beginning
                    st.session_state.show_job_management_input = False  # Disable this input field
                    st.session_state.inside = 0
                    st.rerun()

                elif prompt.strip() == "2":
                    # Stop accepting applications
                    job_details_ref = db.reference(f"jobs/{company_name}/{job_id}")
                    job_details_ref.update({"accepting_applications": False})
                    st.session_state.messages.append({"role": "bot", "content": f"Applications for the role '{job_details['role']}' at '{company_name}' are now closed."})
                    st.session_state.user_state['step'] = -1  # Restart from the beginning
                    st.session_state.show_job_management_input = False  # Disable this input field
                    st.session_state.inside = 0
                    st.rerun()

                elif prompt.strip() == "3":
                    # Restart accepting applications
                    job_details_ref = db.reference(f"jobs/{company_name}/{job_id}")
                    job_details_ref.update({"accepting_applications": True})
                    st.session_state.messages.append({"role": "bot", "content": f"Applications for the role '{job_details['role']}' at '{company_name}' are now open."})
                    st.session_state.user_state['step'] = -1  # Restart from the beginning
                    st.session_state.show_job_management_input = False  # Disable this input field
                    st.session_state.inside = 0
                    st.rerun()

                else:
                    st.session_state.messages.append({"role": "bot", "content": "Invalid input. Please enter 1, 2, or 3."})
                    st.rerun()

    # Job posting form for employer
    if st.session_state.user_state['step'] == 2 and st.session_state.user_state['role'] == "employer" and st.session_state.user_state['job_action'] == "post":
        with st.form("job_post_form"):
            st.subheader("📝 Job Posting Form")
            company_name = st.text_input("🏢 Company Name")
            location = st.text_input("📍 Location")
            salary = st.text_input("💰 Salary")
            domain = st.selectbox("🔧 Job Domain", fetch_job_domains())
            role = st.text_input("👔 Job Role")
            openings = st.number_input("👥 Number of Openings", min_value=1)
            submit_button = st.form_submit_button("📤 Post Job")

            if submit_button:
                job_data = {
                    "company": company_name.lower(),
                    "location": location.lower(),
                    "employer_number": st.session_state.user_state['phone_number'],
                    "salary": salary,
                    "domain": domain.lower(),
                    "role": role.lower(),
                    "openings": openings,
                    "accepting_applications": True,
                    "applicants": {}
                }
                db.reference(f"jobs/{company_name}").push(job_data)
                st.session_state.messages.append({"role": "bot", "content": "Job posted successfully!"})
                st.session_state.user_state['step'] = -1  # Restart from the beginning
                st.session_state.user_state['role'] = None
                st.session_state.user_state['job_action'] = None
                st.rerun()

    # Job application form for employee
    if st.session_state.user_state['step'] == 2 and st.session_state.user_state['role'] == "employee" and st.session_state.user_state['job_action'] == "apply":
        # Step 1: Collect employee details
        if "show_employee_form" not in st.session_state:
            st.session_state.show_employee_form = True

        if st.session_state.show_employee_form:
            with st.form("job_application_form"):
                st.write("📝 Job Application Form")
                name = st.text_input("Name")
                skills = st.text_input("Skills (comma-separated)")
                preferred_location = st.text_input("📍Preferred Location")
                domain = st.selectbox("🔧 Job Domain", fetch_job_domains())
                submit_button = st.form_submit_button("📤Submit")

                if submit_button:
                    # Save employee data
                    st.session_state.employee_data = {
                        "name": name,
                        "employee_number": st.session_state.user_state['phone_number'],
                        "skills": skills,
                        "location": preferred_location,
                        "job_domain": domain
                    }
                    st.session_state.show_employee_form = False  # Disable the form
                    st.session_state.messages.append({"role": "bot", "content": "🔍 Fetching matching jobs..."})
                    st.session_state.show_matching_jobs = True
                    st.session_state.show_job_selection_input = True

                    st.rerun()

        # Step 2: Fetch and display matching jobs
        if "show_matching_jobs" not in st.session_state:
            st.session_state.show_matching_jobs = False

        if st.session_state.show_matching_jobs:
            # Fetch jobs from Firebase
            jobs_ref = db.reference("jobs").get()
            st.session_state.available_jobs = []  # Store available jobs in session state
            if jobs_ref:
                for company_name, jobs in jobs_ref.items():
                    for job_id, job_details in jobs.items():
                        if job_details.get("accepting_applications", False) and \
                        job_details["location"] == st.session_state.employee_data["location"] and \
                        job_details["domain"] == st.session_state.employee_data["job_domain"]:
                            st.session_state.available_jobs.append((company_name, job_id, job_details))

            if not st.session_state.available_jobs:
                st.session_state.messages.append({"role": "bot", "content": "No matching jobs found for your criteria. Thanks for visiting us!"})
                st.session_state.user_state['step'] = -1  # Restart from the beginning
                st.rerun()
            else:
                # Display matching jobs
                job_list = ""
                for idx, (company_name, _, job_details) in enumerate(st.session_state.available_jobs, start=1):
                    job_list += (f"{idx}) Company Name: {company_name}, Job Role: {job_details['role']}, "
                                f"Job Domain: {job_details['domain']}, Salary: {job_details['salary']}\n")
                st.session_state.messages.append({"role": "bot", "content": f"Matching jobs:\n{job_list}"})
                st.session_state.messages.append({"role": "bot", "content": "🔢 Select a job by its serial number to apply:"})
                st.session_state.show_matching_jobs = False  # Disable this step
                st.rerun()

        # Step 3: Handle job selection and application
        if "show_job_selection_input" not in st.session_state:
            st.session_state.show_job_selection_input = False

        if st.session_state.show_job_selection_input:
            if prompt := st.chat_input("🔢 Enter the serial number of the job"):
                try:
                    selected_index = int(prompt.strip()) - 1
                    if 0 <= selected_index < len(st.session_state.available_jobs):  # Access available_jobs from session state
                        selected_job = st.session_state.available_jobs[selected_index]
                        company_name, job_id, job_details = selected_job

                        # Check if the employee has already applied
                        job_applicants_ref = db.reference(f"jobs/{company_name}/{job_id}/applicants")
                        existing_applicants = job_applicants_ref.get()
                        already_applied = False

                        if existing_applicants:
                            for applicant_key, applicant in existing_applicants.items():
                                if applicant.get("employee_number") == st.session_state.employee_data["employee_number"]:
                                    already_applied = True
                                    break

                        if already_applied:
                            st.session_state.messages.append({"role": "bot", "content": "You have already applied for this role. "
                                                                                        "You shall receive a callback if the recruiter finds you a perfect match. "
                                                                                        "Thank you for choosing us!"})
                        else:
                            # Push employee data to Firebase
                            job_applicants_ref.push(st.session_state.employee_data)
                            st.session_state.messages.append({"role": "bot", "content": "Yayy! You have successfully applied for this job! "
                                                                                        "Thank you for using our platform."})

                        st.session_state.user_state['step'] = -1  # Restart from the beginning
                        st.session_state.show_job_selection_input = False  # Disable this input field
                        st.rerun()
                    else:
                        st.session_state.messages.append({"role": "bot", "content": "Invalid selection. Please try again."})
                        st.rerun()
                except ValueError:
                    st.session_state.messages.append({"role": "bot", "content": "Please enter a valid number."})
                    st.rerun()

    if st.session_state.user_state['step'] == 2 and st.session_state.user_state['role'] == "employee" and st.session_state.user_state['job_action'] == "manage":
    # Step 1: Fetch applied jobs
        if "show_applied_jobs" not in st.session_state:
            st.session_state.show_applied_jobs = True

        if st.session_state.show_applied_jobs:
            # Fetch jobs from Firebase
            jobs_ref = db.reference("jobs").get()
            applied_jobs = []
            if jobs_ref:
                for company_name, jobs in jobs_ref.items():
                    for job_id, job_details in jobs.items():
                        applicants = job_details.get("applicants", {})
                        if isinstance(applicants, dict):  # Ensure applicants is a dictionary
                            for applicant_id, applicant in applicants.items():
                                if applicant.get("employee_number") == st.session_state.user_state['phone_number']:
                                    applied_jobs.append((company_name, job_id, job_details))

            if not applied_jobs:
                st.session_state.messages.append({"role": "bot", "content": "You haven't applied to any jobs yet. Thanks for visiting us!"})
                st.session_state.user_state['step'] = -1  # Restart from the beginning
                st.session_state.show_applied_jobs = False  # Disable this step
                st.rerun()
            else:
                # Display applied jobs
                job_list = ""
                for idx, (company_name, _, job_details) in enumerate(applied_jobs, start=1):
                    job_list += (f"{idx}) Company Name: {company_name}, Job Role: {job_details['role']}, "
                                f"Job Domain: {job_details['domain']}, Location: {job_details['location']}, "
                                f"Salary: {job_details['salary']}\n")
                st.session_state.messages.append({"role": "bot", "content": f"Your applied jobs:\n{job_list}"})
                st.session_state.messages.append({"role": "bot", "content": "🔢 Select a job by its serial number to manage:"})
                st.session_state.show_applied_jobs = False  # Disable this step
                st.session_state.applied_jobs = applied_jobs  # Store applied jobs in session state
                st.session_state.show_job_selection_input = True
                st.rerun()

        # Step 2: Handle job selection
        if "show_job_selection_input" not in st.session_state:
            st.session_state.show_job_selection_input = False

        if st.session_state.show_job_selection_input:
            if prompt := st.chat_input("🔢 Enter the serial number of the job"):
                st.session_state.messages.append({"role": "user", "content": prompt})
                try:
                    selected_index = int(prompt.strip()) - 1
                    if 0 <= selected_index < len(st.session_state.applied_jobs):  # Access applied_jobs from session state
                        selected_job = st.session_state.applied_jobs[selected_index]
                        company_name, job_id, job_details = selected_job

                        st.session_state.messages.append({"role": "bot", "content": "What would you like to do next?"})
                        st.session_state.messages.append({"role": "bot", "content": "1) View job details\n2) Withdraw application"})
                        st.session_state.show_job_selection_input = False  # Disable this input field
                        st.session_state.show_job_management_input = True
                        st.session_state.selected_job = selected_job  # Store selected job in session state
                        st.rerun()
                    else:
                        st.session_state.messages.append({"role": "bot", "content": "Invalid selection. Please try again."})
                        st.rerun()
                except ValueError:
                    st.session_state.messages.append({"role": "bot", "content": "Please enter a valid number."})
                    st.rerun()

        # Step 3: Handle job management options
        if "show_job_management_input" not in st.session_state:
            st.session_state.show_job_management_input = False

        if st.session_state.show_job_management_input:
            if prompt := st.chat_input("Enter 1 or 2"):
                st.session_state.messages.append({"role": "user", "content": prompt})
                if prompt.strip() == "1":
                    # View job details
                    company_name, job_id, job_details = st.session_state.selected_job
                    st.session_state.messages.append({"role": "bot", "content": f"Job Details:\nCompany Name: {company_name} ||"
                                                                            f"Job Role: {job_details['role']} ||"
                                                                            f"Job Domain: {job_details['domain']} ||"
                                                                            f"Location: {job_details['location']} ||"
                                                                            f"Salary: {job_details['salary']}"})
                    st.session_state.messages.append({"role": "bot", "content": "Thank you for choosing us!"})
                    st.session_state.user_state['step'] = -1  # Restart from the beginning
                    st.session_state.show_job_management_input = False  # Disable this input field
                    st.rerun()

                elif prompt.strip() == "2":
                    # Withdraw application
                    company_name, job_id, job_details = st.session_state.selected_job
                    job_applicants_ref = db.reference(f"jobs/{company_name}/{job_id}/applicants")
                    existing_applicants = job_applicants_ref.get()

                    if existing_applicants:
                        for applicant_key, applicant in existing_applicants.items():
                            if applicant.get("employee_number") == st.session_state.user_state['phone_number']:
                                job_applicants_ref.child(applicant_key).delete()
                                st.session_state.messages.append({"role": "bot", "content": "You have successfully withdrawn your application."})
                                st.session_state.messages.append({"role": "bot", "content": "Thank you for choosing us!"})
                                st.session_state.user_state['step'] = -1  # Restart from the beginning
                                st.session_state.show_job_management_input = False  # Disable this input field
                                st.rerun()
                                break

                else:
                    st.session_state.messages.append({"role": "bot", "content": "Invalid input. Please enter 1 or 2."})
                    st.rerun()
        
    if st.button("Exit"):
            st.session_state.user_state = {'step': -1, 'role': None, 'job_action': None, 'phone_number': None}
            st.session_state.messages.append({"role": "bot", "content": "Thank you for using our service! Goodbye!"})
            st.rerun()

if __name__ == "__main__":
    main()
