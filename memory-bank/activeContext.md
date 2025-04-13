# Active Context: AI Prospector (Initialization)

## Current Focus

The primary focus is implementing the core feature changes requested:

1.  Modify `app.py` to run `crawl.py` using `subprocess` instead of `threading`.
2.  Integrate AI-powered query generation using the Groq API into `app.py`.
3.  Add a real-time logging console to `app.py` to display output from the `crawl.py` subprocess.
4.  Add functionality to `app.py` to read and display the contents of `leads.csv` using Pandas and Streamlit's dataframe component.
5.  Ensure the Streamlit UI is structured intuitively across these new steps (Query Gen -> Final Query -> Start -> Log -> Results).

## Recent Changes

- Memory Bank initialized with core files (`projectbrief.md`, `productContext.md`, `techContext.md`, `systemPatterns.md`).

## Next Steps

1.  Create `memory-bank/progress.md`.
2.  Create the `.clinerules` file.
3.  Check `requirements.txt` for `pandas` and `groq`, adding them if missing.
4.  Implement the planned modifications to `app.py`.
5.  Update Memory Bank files (especially `progress.md` and `activeContext.md`) after implementation.

## Active Decisions & Considerations

- Using `subprocess.Popen` for running `crawl.py`.
- Using `threading.Thread` for non-blocking reading of the subprocess logs.
- Using `st.session_state` for managing UI state, logs, and the subprocess.
- Structuring the UI into logical steps (1-5).
- Making AI query generation optional and dependent on the `GROQ_API_KEY`.
- Using `sys.executable` to ensure environment consistency for the subprocess.
- Adding a "Refresh Leads" button and also refreshing automatically upon crawler completion.
