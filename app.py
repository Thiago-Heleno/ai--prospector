import streamlit as st
import subprocess
import threading
import time
import sys
import os
import pandas as pd
from groq import Groq

# --- Constants ---
CSV_FILE = 'leads.csv'

# --- Groq Setup ---
try:
    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key:
        client = Groq(api_key=groq_api_key)
        groq_available = True
    else:
        groq_available = False
except Exception as e:
    st.error(f"Failed to initialize Groq client: {e}", icon="🔥")
    groq_available = False

# --- Session State Initialization ---
defaults = {
    'raw_query': "",
    'generated_query': "",
    'final_query': "",
    'logs': [],
    'running': False,
    'proc': None,
    'refresh_trigger': False,
    'initial_load_done': False
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- Helper Functions ---
def read_log_output(proc, log_list):
    """Reads stdout from the subprocess in a separate thread."""
    try:
        for line in iter(proc.stdout.readline, ''):
            log_list.append(line.strip())
        proc.stdout.close()
        proc.wait()
    except Exception as e:
        log_list.append(f"[Log Thread Error] {e}")

def display_leads(container):
    """Reads leads.csv and displays it in the provided Streamlit container."""
    if os.path.exists(CSV_FILE):
        try:
            if os.path.getsize(CSV_FILE) > 0:
                df = pd.read_csv(CSV_FILE)
                if not df.empty:
                    container.dataframe(df, use_container_width=True)
                else:
                    container.info("Leads file is empty.")
            else:
                container.info("Leads file is empty.")
        except pd.errors.EmptyDataError:
            container.info("Leads file is empty.")
        except Exception as e:
            container.error(f"Error reading leads.csv: {e}", icon="📄")
    else:
        container.info("No leads file found yet. Run the prospector first.")

# --- Streamlit UI ---
st.set_page_config(page_title="Instagram Lead Prospector", layout="wide")
# Removed custom CSS for hiding deploy button as config.toml handles it
st.title("📸 Instagram Lead Prospector")

# App Description
st.markdown("""
This tool helps you find Instagram leads by searching Google.
1.  Optionally describe your desired leads to generate a Google query using AI (requires Groq API key).
2.  Refine or enter your final Google Search query (remember to include `site:instagram.com`).
3.  Start the prospector to run the search and scrape profiles.
4.  Monitor the progress in the log and view results in the table below. You can stop the crawler anytime.
""")
st.divider()

# --- Main Layout Columns ---
col1, col2 = st.columns(2)

with col1:
    # --- Step 1: Generate Query ---
    st.subheader("1. Generate Search Query (Optional)")
    raw_query_input = st.text_input(
        "Describe the leads you want to find:",
        value=st.session_state.raw_query,
        key="raw_query_widget",
        placeholder="e.g., coffee shops in San Francisco",
        on_change=lambda: setattr(st.session_state, 'raw_query', st.session_state.raw_query_widget)
    )

    if not groq_available:
        st.warning("Groq API key (GROQ_API_KEY) not found. Query generation disabled.", icon="⚠️")

    if st.button("✨ Generate Google Query", key="generate_button", disabled=not groq_available or st.session_state.running):
        if st.session_state.raw_query:
            st.session_state.logs.append("Generating Google query with Groq...")
            st.info("Generating Google query with Groq...")
            try:
                with st.spinner("Asking Groq..."):
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {
                                "role": "system",
                                "content": """Generate an effective Google Search query string specifically for finding Instagram profiles based on the user's description. The query MUST include `site:instagram.com`. Use relevant keywords and structure it for Google Search. Return ONLY the generated query string, nothing else."""
                            },
                            {
                                "role": "user",
                                "content": f"Generate a Google search query string to find Instagram profiles based on this description: {st.session_state.raw_query}",
                            }
                        ],
                        model="llama3-70b-8192",
                    )
                generated = chat_completion.choices[0].message.content.strip().replace('"', '')
                st.session_state.generated_query = generated
                st.session_state.final_query = generated
                st.session_state.logs.append(f"Generated Query: {generated}")
                st.rerun()
            except Exception as e:
                st.error(f"Groq query generation failed: {e}", icon="🔥")
                st.session_state.logs.append(f"Error generating query: {e}")
        else:
            st.warning("Please enter a description for the leads.", icon="⚠️")

    if st.session_state.generated_query:
        st.caption("Generated Query:")
        st.code(st.session_state.generated_query, language=None)

    # --- Step 2: Final Query ---
    st.subheader("2. Final Google Query")
    final_query_input = st.text_area(
        "Enter or modify the Google Search Query to use:",
        value=st.session_state.final_query,
        height=100,
        key="final_query_widget",
        help='Use `site:instagram.com` and relevant keywords. Example: `site:instagram.com AND "graphic designer" AND "London"`',
        on_change=lambda: setattr(st.session_state, 'final_query', st.session_state.final_query_widget)
    )

    # --- Step 3: Start / Stop Prospecting ---
    st.subheader("3. Start / Stop Prospecting")
    btn_col1, btn_col2 = st.columns(2) # Columns for buttons

    with btn_col1:
        if st.button("🚀 Start Prospecting", key="start_button", disabled=st.session_state.running, type="primary", use_container_width=True):
            if st.session_state.final_query:
                st.session_state.running = True
                st.session_state.logs = ["Starting crawler..."]
                st.info(f"🚀 Starting crawler for query: '{st.session_state.final_query}'...")
                try:
                    cmd = [sys.executable, 'crawl.py', st.session_state.final_query]
                    env = os.environ.copy()
                    env['PYTHONIOENCODING'] = 'utf-8'
                    st.session_state.proc = subprocess.Popen(
                        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                        text=True, encoding='utf-8', bufsize=1, env=env, creationflags=subprocess.CREATE_NO_WINDOW # Hide console window on Windows
                    )
                    log_thread = threading.Thread(
                        target=read_log_output,
                        args=(st.session_state.proc, st.session_state.logs),
                        daemon=True
                    )
                    log_thread.start()
                    st.rerun()
                except FileNotFoundError:
                    st.error("Error: 'crawl.py' not found.", icon="❌")
                    st.session_state.running = False
                    st.session_state.logs.append("Error: crawl.py not found.")
                except Exception as e:
                    st.error(f"Failed to start crawler process: {e}", icon="❌")
                    st.session_state.running = False
                    st.session_state.logs.append(f"Error starting crawler: {e}")
            else:
                st.warning("Please enter a final query before starting.", icon="⚠️")

    with btn_col2:
        if st.button("🛑 Stop Crawler", key="stop_button", disabled=not st.session_state.running, use_container_width=True):
            if st.session_state.proc:
                try:
                    st.session_state.logs.append("🛑 Stop requested by user. Terminating crawler...")
                    st.session_state.proc.terminate() # Send termination signal
                    st.warning("Crawler stop requested. Please wait a moment...")
                    # Give a moment for termination signal to be processed before clearing state
                    time.sleep(1)
                    st.session_state.proc.poll() # Check if terminated
                except Exception as e:
                    st.error(f"Error trying to stop crawler: {e}")
                finally:
                    # Ensure state is reset even if terminate fails slightly
                    st.session_state.running = False
                    st.session_state.proc = None
                    st.session_state.logs.append("Crawler process terminated or stop attempted.")
                    st.rerun() # Update UI

    # Display status message below buttons
    if st.session_state.running:
        st.info("Crawler is running...")
    # Add message if stopped by user? (Handled by rerun and running=False)

with col2:
    # --- Step 4: Crawler Log ---
    st.subheader("4. Crawler Log")
    log_placeholder = st.empty()
    log_placeholder.text_area(
        "Log Output",
        value="\n".join(st.session_state.logs),
        height=350,
        key="log_area_display"
    )

    # --- Step 5: Leads Found ---
    st.subheader("5. Leads Found")
    if st.button("🔄 Refresh Leads", key="refresh_button", disabled=st.session_state.running):
        st.session_state.refresh_trigger = True
        st.rerun()

    leads_container = st.empty()

# --- Process Monitoring & Auto-Refresh Logic (outside columns) ---
if st.session_state.running:
    if st.session_state.proc and st.session_state.proc.poll() is not None: # Check if process finished
        st.session_state.running = False
        st.session_state.proc = None
        st.session_state.logs.append("Crawler process finished.")
        st.session_state.refresh_trigger = True # Trigger refresh after finish
        st.success("Crawler finished!")
        st.rerun()
    else:
        # Periodic rerun to update logs while running
        time.sleep(1) # Reduce frequency slightly
        try:
            st.rerun()
        except st.errors.RerunException:
             # Expected exception when rerun is called, ignore it
             pass
        except Exception as e:
             # Catch other potential errors during rerun
             print(f"Error during periodic rerun: {e}")


# Handle refresh trigger (manual or automatic)
if st.session_state.refresh_trigger:
    display_leads(leads_container)
    st.session_state.refresh_trigger = False # Reset trigger

# Initial display of leads on first load
if not st.session_state.initial_load_done:
     display_leads(leads_container)
     st.session_state.initial_load_done = True

# --- About Section ---
st.divider()
with st.expander("About"):
    st.markdown("""
        **Instagram Lead Prospector v0.1**

        This tool uses Google Search and AI (Groq for query generation, Gemini for data extraction via `crawl4ai`)
        to find and extract information from Instagram profiles based on your search criteria.

        *   **Note:** Web scraping can be unreliable due to website changes or anti-bot measures.
        *   Requires `GROQ_API_KEY` and `GEMINI_API_KEY` environment variables.
        *   Created by [Thiago Heleno](https://github.com/Thiago-Heleno).
    """)
