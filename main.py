import pandas as pd
import streamlit as st

from backend import (
    execute_sql,
    generate_sql,
    get_database_connection,
    get_database_schema,
)
from sql_validator import get_sql_operation


# -------------------- PAGE SETTINGS --------------------

st.set_page_config(
    page_title="QueryMind AI",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -------------------- SESSION STATE --------------------

DEFAULTS = {
    "page": "Home",
    "dark_mode": False,
    "question_input": "",
    "last_question": "",
    "last_sql": "",
    "last_result": None,
    "last_error": "",
    "pending_update_sql": "",
    "pending_update_question": "",
    "last_update_result": None,
    "update_cancelled": False,
    "query_history": [],
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -------------------- LIGHT / DARK THEME --------------------

LIGHT = {
    "PAGE": "#F5F8FF", "SIDEBAR": "#F8FAFF", "SURFACE": "#FFFFFF",
    "ALT": "#EEF4FF", "BORDER": "#DCE6F7", "TEXT": "#14264B",
    "MUTED": "#687A9D", "ACCENT": "#2167F5", "ACCENT_SOFT": "#DCEAFF",
    "SUCCESS": "#12B981", "DANGER": "#DC4C64", "INPUT": "#FFFFFF",
}
DARK = {
    "PAGE": "#10182B", "SIDEBAR": "#121E35", "SURFACE": "#182541",
    "ALT": "#202F4D", "BORDER": "#30415F", "TEXT": "#EEF3FF",
    "MUTED": "#A5B3CF", "ACCENT": "#6B9BFF", "ACCENT_SOFT": "#263D68",
    "SUCCESS": "#35D3A0", "DANGER": "#FF7188", "INPUT": "#1B2945",
}
COLORS = DARK if st.session_state.dark_mode else LIGHT

CSS = """
<style>
:root{--page:__PAGE__;--sidebar:__SIDEBAR__;--surface:__SURFACE__;--alt:__ALT__;--border:__BORDER__;--text:__TEXT__;--muted:__MUTED__;--accent:__ACCENT__;--accent-soft:__ACCENT_SOFT__;--success:__SUCCESS__;--danger:__DANGER__;--input:__INPUT__}
/* Remove Streamlit's fixed white header/toolbar so it cannot cover app controls. */
.stAppHeader, header[data-testid="stHeader"], [data-testid="stHeader"]{
    display:none !important;
    height:0 !important;
    min-height:0 !important;
    background:transparent !important;
    border:0 !important;
    box-shadow:none !important;
}
[data-testid="stToolbar"], [data-testid="stDecoration"]{
    display:none !important;
}
.stApp,[data-testid="stAppViewContainer"]{background:linear-gradient(125deg,var(--page),var(--surface));color:var(--text)}
.block-container{max-width:1280px;padding-top:1rem;padding-bottom:3rem}
section[data-testid="stSidebar"]{width:238px!important;min-width:238px!important}
[data-testid="stSidebar"]>div:first-child{background:var(--sidebar);border-right:1px solid var(--border)}
[data-testid="stSidebar"] .block-container{padding-top:1.5rem}
h1,h2,h3,h4,p,label,li{color:var(--text)}
h1{font-weight:800;letter-spacing:-.7px}
h2,h3{letter-spacing:-.3px}
[data-testid="stCaptionContainer"],.stCaption{color:var(--muted)!important}
.brand{display:flex;align-items:center;gap:12px;padding:8px 4px 20px}
.brand-icon{width:42px;height:42px;display:flex;align-items:center;justify-content:center;flex:none}
.brand-name{color:var(--text);font-size:18px;font-weight:800;line-height:1.2}
.brand-caption{color:var(--muted);font-size:11px;margin-top:5px}
[data-testid="stSidebar"] .stButton{margin:2px 0}
[data-testid="stSidebar"] .stButton button{min-height:41px;border-radius:10px;text-align:left;justify-content:flex-start;padding-left:13px;font-weight:600}
[data-testid="stSidebar"] .stButton button[kind="secondary"]{color:var(--text);background:transparent;border:1px solid transparent}
[data-testid="stSidebar"] .stButton button[kind="secondary"]:hover{color:var(--accent);background:var(--accent-soft)}
[data-testid="stSidebar"] .stButton button[kind="primary"]{color:var(--accent);background:var(--accent-soft);border:1px solid transparent}
.stTextInput input{min-height:48px;color:var(--text)!important;background:var(--input)!important;border:1px solid var(--border)!important;border-radius:12px!important}
.stTextInput input::placeholder{color:var(--muted)!important}
.stButton button,.stFormSubmitButton button{min-height:42px;border-radius:10px;font-weight:650}
.st-key-example_chips .stButton button{min-height:34px;background:var(--accent-soft);color:var(--text);border:0;border-radius:22px;font-size:12px;padding:0 8px}
.st-key-example_chips .stButton button:hover{color:var(--accent);border:1px solid var(--accent)}
.stFormSubmitButton button{min-height:48px;color:white!important;background:linear-gradient(100deg,#347EFF,#175DEB)!important;border:0!important;font-size:19px}
.stFormSubmitButton button:hover,.stButton button[kind="primary"]:hover{filter:brightness(1.06);box-shadow:0 5px 14px #2167f533}
[data-testid="stForm"]{background:var(--surface);border:1px solid var(--border);border-radius:15px;padding:10px 12px 2px;box-shadow:0 5px 18px #2753960f}
[data-testid="stVerticalBlockBorderWrapper"]{background:var(--surface);border-color:var(--border)!important;border-radius:16px!important;box-shadow:0 4px 16px #2753960b}
[data-testid="stDataFrame"]{border:1px solid var(--border);border-radius:10px}
.hero-title{color:var(--text);font-size:clamp(27px,3vw,36px);line-height:1.18;font-weight:800;letter-spacing:-1px;margin:8px 0 4px}
.hero-subtitle{color:var(--muted);font-size:16px;margin-top:0}
.hero-art{display:flex;justify-content:center;align-items:center;min-height:145px}
.eyebrow{color:var(--accent);font-size:11px;letter-spacing:1.5px;font-weight:800}
.status-line{display:flex;align-items:center;gap:10px;font-size:19px;font-weight:750;color:var(--text);margin:16px 0 4px}
.status-dot{width:12px;height:12px;border-radius:50%;display:inline-block;background:var(--success);box-shadow:0 0 0 4px #12b98124}
.status-dot.offline{background:var(--danger);box-shadow:0 0 0 4px #dc4c6424}
.feature-row{display:flex;align-items:center;gap:9px;color:var(--text);font-size:13px;margin:12px 0}
.feature-check{color:var(--success);font-weight:900;font-size:16px}
[data-testid="stToggle"] label{color:var(--muted)!important;font-size:12px}
hr{border-color:var(--border)!important}
@media(max-width:760px){.block-container{padding-left:1rem;padding-right:1rem}.hero-art{min-height:90px}}
</style>
"""

for name, color in COLORS.items():
    CSS = CSS.replace(f"__{name}__", color)
st.markdown(CSS, unsafe_allow_html=True)


# -------------------- DATABASE STATUS --------------------

@st.cache_data(ttl=30, show_spinner=False)
def check_database_status():
    """Return True only when a real MySQL connection can be opened."""
    connection = None
    try:
        connection = get_database_connection()
        return True
    except Exception:
        return False
    finally:
        if connection is not None:
            try:
                connection.close()
            except Exception:
                pass


@st.cache_data(ttl=60, show_spinner=False)
def load_schema():
    return get_database_schema()


database_connected = check_database_status()


# -------------------- ACTIONS --------------------

def go_to_page(page_name):
    st.session_state.page = page_name


def set_example_question(question):
    st.session_state.question_input = question


def clear_history():
    st.session_state.query_history = []


def clear_session_data():
    st.session_state.query_history = []
    st.session_state.last_question = ""
    st.session_state.last_sql = ""
    st.session_state.last_result = None
    st.session_state.last_error = ""
    st.session_state.pending_update_sql = ""
    st.session_state.pending_update_question = ""
    st.session_state.last_update_result = None
    st.session_state.update_cancelled = False
    st.session_state.question_input = ""


def save_history(question, sql, status):
    st.session_state.query_history.insert(0, {
        "Time": pd.Timestamp.now().strftime("%d %b %Y, %I:%M %p"),
        "Question": question,
        "Status": status,
        "SQL": sql,
    })
    st.session_state.query_history = st.session_state.query_history[:50]


def confirm_pending_update():
    """Run the pending UPDATE only after the user presses Confirm."""
    sql = st.session_state.pending_update_sql
    question = st.session_state.pending_update_question

    try:
        success, result = execute_sql(sql, confirm_update=True)
        if success:
            affected_rows = result.get("affected_rows", 0)
            st.session_state.last_update_result = affected_rows
            st.session_state.last_error = ""
            save_history(question, sql, f"Updated ({affected_rows} rows)")
        else:
            st.session_state.last_error = str(result)
            save_history(question, sql, "Failed")
    except Exception as error:
        st.session_state.last_error = f"Update failed: {error}"
        save_history(question, sql, "Failed")

    st.session_state.pending_update_sql = ""
    st.session_state.pending_update_question = ""


def cancel_pending_update():
    """Cancel a pending UPDATE without changing the database."""
    save_history(
        st.session_state.pending_update_question,
        st.session_state.pending_update_sql,
        "Cancelled",
    )
    st.session_state.pending_update_sql = ""
    st.session_state.pending_update_question = ""
    st.session_state.last_sql = ""
    st.session_state.update_cancelled = True


def run_query():
    """Generate SQL; run SELECT directly and hold UPDATE for confirmation."""
    question = st.session_state.question_input.strip()
    st.session_state.last_question = question
    st.session_state.last_sql = ""
    st.session_state.last_result = None
    st.session_state.last_error = ""
    st.session_state.pending_update_sql = ""
    st.session_state.pending_update_question = ""
    st.session_state.last_update_result = None
    st.session_state.update_cancelled = False

    if not question:
        st.session_state.last_error = "Please enter a question first."
        return

    try:
        with st.spinner("QueryMind AI is preparing your SQL query..."):
            generated = generate_sql(question)

        if not isinstance(generated, tuple) or len(generated) != 2:
            raise ValueError("SQL generation returned an unexpected response.")

        success, sql_or_error = generated
        if not success:
            st.session_state.last_error = str(sql_or_error)
            save_history(question, "", "Failed")
            return

        sql = str(sql_or_error)
        st.session_state.last_sql = sql
        operation = get_sql_operation(sql)

        if operation == "UPDATE":
            st.session_state.pending_update_sql = sql
            st.session_state.pending_update_question = question
            return

        if operation != "SELECT":
            st.session_state.last_error = "Only SELECT and conditional UPDATE queries are supported."
            save_history(question, sql, "Failed")
            return

        with st.spinner("Running the query on MySQL..."):
            executed = execute_sql(sql)

        if not isinstance(executed, tuple) or len(executed) != 2:
            raise ValueError("Database execution returned an unexpected response.")

        success, result_or_error = executed
        if not success:
            st.session_state.last_error = str(result_or_error)
            save_history(question, sql, "Failed")
            return

        result = result_or_error
        if (not isinstance(result, dict)
                or not isinstance(result.get("columns"), (list, tuple))
                or not isinstance(result.get("rows"), (list, tuple))):
            raise ValueError("The database returned results in an unexpected format.")

        st.session_state.last_result = result
        save_history(question, sql, "Success")

    except Exception as error:
        st.session_state.last_error = f"Something went wrong: {error}"
        save_history(question, st.session_state.last_sql, "Failed")

# -------------------- SIDEBAR --------------------

with st.sidebar:
    st.markdown(
        '<div class="brand"><div class="brand-icon"><svg width="38" height="38" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg"><ellipse cx="20" cy="9" rx="14" ry="5.5" fill="#8FC8FF" stroke="#2878ED" stroke-width="1.8"/><path d="M6 9V29C6 32 12.3 35 20 35C27.7 35 34 32 34 29V9" fill="#3989F2"/><path d="M6 16C6 19 12.3 22 20 22C27.7 22 34 19 34 16M6 23C6 26 12.3 29 20 29C27.7 29 34 26 34 23" stroke="#E5F2FF" stroke-width="1.8"/><path d="M6 9C6 12 12.3 15 20 15C27.7 15 34 12 34 9" stroke="#E5F2FF" stroke-width="1.8"/></svg></div><div>'
        '<div class="brand-name">QueryMind AI</div>'
        '<div class="brand-caption">Natural Language Database Assistant</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )
    st.divider()

    for label, page in [
        ("⌂   Home", "Home"),
        ("⌕   Ask Database", "Ask Database"),
        ("◷   History", "History"),
        ("▦   Schema", "Schema"),
        ("⚙   Settings", "Settings"),
    ]:
        st.button(
            label,
            key=f"nav_{page}",
            type="primary" if st.session_state.page == page else "secondary",
            use_container_width=True,
            on_click=go_to_page,
            args=(page,),
        )

    st.divider()
    if database_connected:
        st.markdown(
            '<div style="background:var(--alt);border:1px solid var(--border);border-radius:12px;padding:10px 12px">'
            '<div class="status-line"><span class="status-dot"></span>'
            '<span style="font-size:13px">Database Connected</span></div></div>',
            unsafe_allow_html=True,
        )
        st.caption("MySQL Database")
    else:
        st.markdown(
            '<div style="background:var(--alt);border:1px solid var(--border);border-radius:12px;padding:10px 12px">'
            '<div class="status-line"><span class="status-dot offline"></span>'
            '<span style="font-size:13px">Not Connected</span></div></div>',
            unsafe_allow_html=True,
        )
        st.caption("Check MySQL and .env settings")
    st.divider()
    st.caption("Powered by Gemini AI · MySQL")


# -------------------- TOP BAR / THEME SWITCH --------------------

_, theme_column, user_column = st.columns([8, 1.5, 0.5])
with theme_column:
    st.toggle("Dark mode", key="dark_mode")
with user_column:
    st.markdown(
        '<div style="background:#2167F5;color:white;border-radius:50%;width:30px;'
        'height:30px;display:flex;align-items:center;justify-content:center;'
        'font-weight:800;margin:5px auto">Q</div>',
        unsafe_allow_html=True,
    )


# -------------------- QUERY FORM AND EXAMPLES --------------------

def render_query_form():
    with st.form("query_form", clear_on_submit=False):
        input_column, button_column = st.columns([8, 0.8])
        with input_column:
            st.text_input(
                "Your question",
                placeholder="Type your question in natural language...",
                label_visibility="collapsed",
                key="question_input",
            )
        with button_column:
            submitted = st.form_submit_button(
                "➜", use_container_width=True,
                help="Generate SQL and view database results",
            )
    if submitted:
        run_query()


def render_examples():
    st.markdown("**Try asking:**")
    examples = [
        "Show all customers", "Top 5 products",
        "Total sales by month", "Count orders",
    ]
    with st.container(key="example_chips"):
        columns = st.columns(4)
        for index, question in enumerate(examples):
            with columns[index]:
                st.button(
                    f"✧  {question}", key=f"example_{index}",
                    use_container_width=True, on_click=set_example_question,
                    args=(question,),
                )


def render_query_output():
    if st.session_state.last_error:
        st.error(st.session_state.last_error)

    if st.session_state.update_cancelled:
        st.info("Update cancelled. No database changes were made.")

    if st.session_state.pending_update_sql:
        with st.container(border=True):
            st.markdown("### Review database update")
            st.warning(
                "This request will change existing records. "
                "Review the SQL before confirming."
            )
            st.code(st.session_state.pending_update_sql, language="sql")

            confirm_column, cancel_column = st.columns(2)

            with confirm_column:
                st.button(
                    "Confirm & Update Database",
                    key="confirm_database_update",
                    type="primary",
                    use_container_width=True,
                    on_click=confirm_pending_update,
                )

            with cancel_column:
                st.button(
                    "Cancel Update",
                    key="cancel_database_update",
                    use_container_width=True,
                    on_click=cancel_pending_update,
                )
        return

    if st.session_state.last_update_result is not None:
        affected_rows = st.session_state.last_update_result

        if affected_rows:
            st.success(
                f"Update completed. {affected_rows} row(s) affected."
            )
        else:
            st.info(
                "Update completed, but no matching rows were changed."
            )

        with st.container(border=True):
            st.markdown("### Executed UPDATE")
            st.code(st.session_state.last_sql, language="sql")
        return

    if st.session_state.last_result is not None:
        result = st.session_state.last_result
        rows = result["rows"]
        columns = result["columns"]

        st.markdown("## Query Results")
        st.caption(f"Question: {st.session_state.last_question}")

        result_column, sql_column = st.columns([1.55, 1])

        with result_column:
            with st.container(border=True):
                st.markdown("### Results from MySQL")
                st.metric("Rows returned", len(rows))

                if rows:
                    dataframe = pd.DataFrame(
                        rows,
                        columns=columns,
                    )
                    st.table(dataframe)
                else:
                    st.info(
                        "The query ran successfully, "
                        "but no records were found."
                    )

        with sql_column:
            with st.container(border=True):
                st.markdown("### SQL Preview")
                st.code(st.session_state.last_sql, language="sql")
                st.caption(
                    "Generated by Gemini AI and validated before execution."
                )

    elif st.session_state.last_sql:
        with st.container(border=True):
            st.markdown("### Generated SQL")
            st.code(st.session_state.last_sql, language="sql")

# -------------------- HOME PAGE --------------------

if st.session_state.page == "Home":
    hero_text, hero_art = st.columns([3.2, 1.2], vertical_alignment="center")
    with hero_text:
        st.markdown('<div class="eyebrow">YOUR DATABASE, IN SIMPLE LANGUAGE</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-title">Welcome to QueryMind AI</div>', unsafe_allow_html=True)
        st.markdown('<div class="hero-subtitle">Simple. Smart. Powerful.</div>', unsafe_allow_html=True)

    with hero_art:
        st.markdown(
            """
            <div class="hero-art">
              <svg width="176" height="150" viewBox="0 0 176 150" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="87" cy="76" r="64" fill="#4C91FF" fill-opacity=".07"/>
                <circle cx="28" cy="35" r="3" fill="#75B5FF"/><circle cx="145" cy="27" r="4" fill="#75B5FF"/>
                <ellipse cx="77" cy="42" rx="31" ry="12" fill="#9CCBFF" stroke="#3788F5" stroke-width="2"/>
                <path d="M46 42V91C46 98 60 104 77 104C94 104 108 98 108 91V42" fill="#4C98F7"/>
                <path d="M46 58C46 65 60 71 77 71C94 71 108 65 108 58M46 75C46 82 60 88 77 88C94 88 108 82 108 75" stroke="#D9ECFF" stroke-width="2"/>
                <ellipse cx="77" cy="42" rx="31" ry="12" fill="url(#dbTop)" stroke="#2E7CEB" stroke-width="2"/>
                <circle cx="119" cy="93" r="22" fill="#E8F3FF" stroke="#2778EF" stroke-width="7"/>
                <path d="M135 109L153 127" stroke="#2778EF" stroke-width="9" stroke-linecap="round"/>
                <defs><linearGradient id="dbTop" x1="46" y1="30" x2="108" y2="54" gradientUnits="userSpaceOnUse"><stop stop-color="#91C8FF"/><stop offset="1" stop-color="#2A75E8"/></linearGradient></defs>
              </svg>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    render_query_form()
    render_examples()
    render_query_output()
    st.write("")

    status_column, features_column = st.columns([1.45, 1])
    with status_column:
        with st.container(border=True):
            st.markdown("### ◈  Database Status")
            if database_connected:
                st.markdown('<div class="status-line"><span class="status-dot"></span>Connected</div>', unsafe_allow_html=True)
                st.caption("MySQL Database is reachable.")
            else:
                st.markdown('<div class="status-line"><span class="status-dot offline"></span>Not connected</div>', unsafe_allow_html=True)
                st.caption("Check that MySQL is running and your .venv/.env settings are correct.")

    with features_column:
        with st.container(border=True):
            st.markdown("### Our Features")
            st.markdown(
                '<div class="feature-row"><span class="feature-check">✓</span>Natural Language Questions</div>'
                '<div class="feature-row"><span class="feature-check">✓</span>AI-Powered SQL Generation</div>'
                '<div class="feature-row"><span class="feature-check">✓</span>SQL Validation and MySQL Results</div>',
                unsafe_allow_html=True,
            )


# -------------------- ASK DATABASE PAGE --------------------

elif st.session_state.page == "Ask Database":
    st.markdown('<div class="eyebrow">QUERY WORKSPACE</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Ask Your Database</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Write your question naturally. QueryMind AI will generate SQL and retrieve the matching records.</div>', unsafe_allow_html=True)
    st.write("")
    render_query_form()
    render_examples()
    render_query_output()


# -------------------- QUERY HISTORY PAGE --------------------

elif st.session_state.page == "History":
    st.markdown('<div class="eyebrow">YOUR RECENT ACTIVITY</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Query History</div>', unsafe_allow_html=True)
    st.caption("History is stored in this app session and is cleared when the session resets.")

    if st.session_state.query_history:
        history_dataframe = pd.DataFrame(st.session_state.query_history)
        st.dataframe(
            history_dataframe, use_container_width=True, hide_index=True,
            column_config={
                "SQL": st.column_config.TextColumn("Generated SQL", width="large"),
                "Question": st.column_config.TextColumn("Question", width="large"),
            },
        )
        st.button("Clear History", on_click=clear_history, type="secondary")
    else:
        st.info("No queries yet. Your successful and failed queries will appear here.")


# -------------------- DATABASE SCHEMA PAGE --------------------

elif st.session_state.page == "Schema":
    st.markdown('<div class="eyebrow">DATABASE STRUCTURE</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Database Schema</div>', unsafe_allow_html=True)
    st.caption("This view reads the actual table and column names from your connected MySQL database.")

    if st.button("↻  Refresh Schema", type="secondary"):
        load_schema.clear()

    with st.spinner("Reading database schema..."):
        schema_success, schema_or_error = load_schema()
    if schema_success:
        st.code(schema_or_error, language="text")
    else:
        st.error(schema_or_error)


# -------------------- SETTINGS PAGE --------------------

elif st.session_state.page == "Settings":
    st.markdown('<div class="eyebrow">PREFERENCES</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Settings</div>', unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("### Appearance")
        mode = "Dark" if st.session_state.dark_mode else "Light"
        st.write(f"Current appearance: **{mode} mode**")
        st.caption("Use the Dark mode switch in the top-right corner to change the interface theme.")

    with st.container(border=True):
        st.markdown("### Session Data")
        st.caption("Clear the query history and current result from this app session.")
        st.button("Clear Session Data", on_click=clear_session_data, type="secondary")

    with st.container(border=True):
        st.markdown("### About QueryMind AI")
        st.write("Ask questions about your existing MySQL database in everyday language. Gemini generates SQL, the validator checks it, and MySQL returns the actual results.")
        st.caption("Current execution mode: SELECT and confirmation-based UPDATE. INSERT is planned for a future version.")
