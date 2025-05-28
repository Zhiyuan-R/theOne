"""
Streamlit frontend for theOne dating app
"""
import streamlit as st
import requests
import json
from typing import Optional
import os

# Configuration
API_BASE_URL = "http://localhost:8000/api"

# Initialize session state
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None


def make_api_request(endpoint: str, method: str = "GET", data: dict = None, files: dict = None, auth_required: bool = True):
    """Make API request with authentication"""
    headers = {}
    if auth_required and st.session_state.access_token:
        headers["Authorization"] = f"Bearer {st.session_state.access_token}"

    url = f"{API_BASE_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            if files:
                response = requests.post(url, headers=headers, data=data, files=files)
            else:
                headers["Content-Type"] = "application/json"
                response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            headers["Content-Type"] = "application/json"
            response = requests.put(url, headers=headers, json=data)

        return response
    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return None


def login_page():
    """Login/Register page"""
    st.title("🌟 theOne - AI-Powered Dating")
    st.subheader("Welcome to the future of dating!")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            if email and password:
                # Prepare form data for OAuth2 (must be sent as form data, not JSON)
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/auth/login",
                        data={
                            "username": email,  # OAuth2 uses 'username' field
                            "password": password
                        }
                    )

                    if response.status_code == 200:
                        token_data = response.json()
                        st.session_state.access_token = token_data["access_token"]
                        st.session_state.user_email = email
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Login failed. Please check your credentials.")
                except Exception as e:
                    st.error(f"Login error: {e}")
            else:
                st.error("Please enter both email and password.")

    with tab2:
        st.subheader("Register")
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password")

        if st.button("Register"):
            if reg_email and reg_password and reg_confirm_password:
                if reg_password != reg_confirm_password:
                    st.error("Passwords don't match!")
                else:
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/auth/register",
                            json={
                                "email": reg_email,
                                "password": reg_password
                            }
                        )

                        if response.status_code == 200:
                            st.success("Registration successful! Please login.")
                        else:
                            st.error("Registration failed. Email might already be registered.")
                    except Exception as e:
                        st.error(f"Registration error: {e}")
            else:
                st.error("Please fill in all fields.")


def profile_page():
    """Profile creation/management page"""
    st.title("📸 Your Profile")

    # Check if profile exists
    response = make_api_request("/profiles/me", "GET")
    has_profile = response and response.status_code == 200

    if has_profile:
        profile_data = response.json()
        st.success("✅ Profile created!")
        st.write(f"**Description:** {profile_data['description']}")
        st.write(f"**Photos:** {len(profile_data['photos'])} uploaded")
        if profile_data.get('audio_clip_path'):
            st.write("🎵 Audio clip uploaded")

        # Option to update description
        st.subheader("Update Profile")
        new_description = st.text_area("Update your description:", value=profile_data['description'])
        if st.button("Update Description"):
            update_data = {"description": new_description}
            response = make_api_request("/profiles/me", "PUT", data=update_data)
            if response and response.status_code == 200:
                st.success("Profile updated!")
                st.rerun()
    else:
        st.info("Create your profile to get started!")

        # Profile creation form
        st.subheader("Create Your Profile")
        description = st.text_area(
            "Tell us about yourself:",
            placeholder="I'm an introverted bookworm who loves rainy cafes and deep talks...",
            height=100
        )

        photos = st.file_uploader(
            "Upload 1-5 photos:",
            type=['jpg', 'jpeg', 'png', 'webp'],
            accept_multiple_files=True
        )

        audio_clip = st.file_uploader(
            "Optional: Upload a voice clip:",
            type=['mp3', 'wav', 'm4a']
        )

        if st.button("Create Profile"):
            if description and photos and 1 <= len(photos) <= 5:
                # Prepare files for upload
                files = {}
                for i, photo in enumerate(photos):
                    files[f'photos'] = photo

                form_data = {"description": description}

                if audio_clip:
                    files['audio_clip'] = audio_clip

                # Note: This is a simplified version. In practice, you'd need to handle
                # multiple file uploads properly with the requests library
                st.info("Profile creation functionality needs to be implemented with proper file handling.")
                st.info("For now, please use the API directly or implement file upload handling.")
            else:
                st.error("Please provide a description and 1-5 photos.")


def expectations_page():
    """Expectations/preferences page"""
    st.title("💭 Your Ideal Match")

    # Check if expectations exist
    response = make_api_request("/expectations/me", "GET")
    has_expectations = response and response.status_code == 200

    if has_expectations:
        expectations_data = response.json()
        st.success("✅ Expectations set!")
        st.write(f"**Description:** {expectations_data['description']}")
        st.write(f"**Example Images:** {len(expectations_data['example_images'])} uploaded")

        # Option to update
        st.subheader("Update Expectations")
        new_description = st.text_area("Update your ideal match description:", value=expectations_data['description'])
        if st.button("Update Expectations"):
            update_data = {"description": new_description}
            response = make_api_request("/expectations/me", "PUT", data=update_data)
            if response and response.status_code == 200:
                st.success("Expectations updated!")
                st.rerun()
    else:
        st.info("Set your expectations to help our AI find better matches!")

        # Expectations creation form
        st.subheader("Describe Your Ideal Match")
        description = st.text_area(
            "What are you looking for?",
            placeholder="Someone warm, adventurous, who loves dogs and slow mornings...",
            height=100
        )

        example_images = st.file_uploader(
            "Upload 1-5 example images that reflect your ideal match's vibe:",
            type=['jpg', 'jpeg', 'png', 'webp'],
            accept_multiple_files=True
        )

        if st.button("Set Expectations"):
            if description and example_images and 1 <= len(example_images) <= 5:
                st.info("Expectations creation functionality needs to be implemented with proper file handling.")
                st.info("For now, please use the API directly.")
            else:
                st.error("Please provide a description and 1-5 example images.")


def matches_page():
    """Matches viewing page"""
    st.title("💕 Your Matches")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("🔄 Generate New Matches"):
            with st.spinner("Finding your perfect matches..."):
                response = make_api_request("/matches/generate-daily-matches", "POST")
                if response and response.status_code == 200:
                    st.success("New matches generated!")
                    st.rerun()
                else:
                    st.error("Failed to generate matches. Make sure you have a profile and expectations set.")

    with col2:
        if st.button("📊 View Stats"):
            response = make_api_request("/matches/stats", "GET")
            if response and response.status_code == 200:
                stats = response.json()
                st.metric("Total Matches", stats["total_matches"])
                st.metric("Average Compatibility", f"{stats['average_compatibility_score']:.1%}")

    # Display matches
    st.subheader("Your Daily Matches")
    response = make_api_request("/matches/daily", "GET")

    if response and response.status_code == 200:
        matches = response.json()

        if matches:
            for match in matches:
                with st.expander(f"Match #{match['id']} - {match['compatibility_score']:.1%} compatibility"):
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Overall Score", f"{match['compatibility_score']:.1%}")
                    with col2:
                        st.metric("Text Similarity", f"{match['text_similarity_score']:.1%}")
                    with col3:
                        st.metric("Visual Compatibility", f"{match['visual_similarity_score']:.1%}")

                    if match.get('matched_user_profile'):
                        profile = match['matched_user_profile']
                        st.write(f"**About them:** {profile['description']}")

                    if not match['is_viewed']:
                        if st.button(f"Mark as Viewed", key=f"view_{match['id']}"):
                            response = make_api_request(f"/matches/{match['id']}/view", "PUT")
                            if response and response.status_code == 200:
                                st.success("Marked as viewed!")
                                st.rerun()
        else:
            st.info("No matches yet. Generate some matches to get started!")
    else:
        st.error("Failed to load matches.")


def main():
    """Main app logic"""
    if not st.session_state.access_token:
        login_page()
    else:
        # Sidebar navigation
        st.sidebar.title(f"Welcome, {st.session_state.user_email}!")

        page = st.sidebar.selectbox(
            "Navigate:",
            ["Profile", "Expectations", "Matches"]
        )

        if st.sidebar.button("Logout"):
            st.session_state.access_token = None
            st.session_state.user_email = None
            st.rerun()

        # Page routing
        if page == "Profile":
            profile_page()
        elif page == "Expectations":
            expectations_page()
        elif page == "Matches":
            matches_page()


if __name__ == "__main__":
    main()
