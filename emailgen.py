import streamlit as st
import sqlite3
from ml_backend import ml_backend
import base64

_left, mid, _right = st.columns([2, 6, 2]) 
with mid:
    with open("C:/Users/ASUS/Documents/Lab Manuals/Minor Project/Project Code/logo.gif", "rb") as f:
        encoded_gif = base64.b64encode(f.read()).decode("utf-8")
    st.markdown(f'<p style="text-align: center;"><img width="300" src="data:image/gif;base64,{encoded_gif}"></p>', unsafe_allow_html=True)


conn = sqlite3.connect('credentials.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                password TEXT
            )''')
conn.commit()

st.sidebar.title("ComposeNow")
st.sidebar.write("Instant Creation, Seamless Communication")


st.sidebar.markdown("# Help")
st.sidebar.write("If you need any assistance or have questions, please reach out to our support team at composenow@gmail.com.")
st.sidebar.markdown("# Privacy")
st.sidebar.write("Your privacy is important to us. Here are some key points:")
st.sidebar.write("- We do not collect or store any personal data.")
st.sidebar.write("- The content you generate using the Automatic Email Generator is not stored or shared with any third parties.")
st.sidebar.write("- We employ industry-standard security measures to protect your information.")
st.sidebar.write("- For more information, please review our [Privacy Policy](https://www.example.com/privacy).")



st.title("ComposeNow")
st.header("Instant Creation, Seamless Communication")
st.markdown("Generate professional emails with ease.")
st.markdown("Save time and effort in crafting emails.")
st.markdown("Get instant email suggestions and drafts.")

if 'sign_up_info' not in st.session_state:
    st.session_state['sign_up_info'] = {}

if 'is_signed_up' not in st.session_state:
    st.title("Sign Up")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")

    if st.button("Sign Up", key="signup_button"):
        
        if password == confirm_password:
            
            c.execute("SELECT * FROM users WHERE email=?", (email,))
            existing_user = c.fetchone()
            if existing_user:
                st.error("Email already exists. Please use a different email.")
            else:
                
                c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
                conn.commit()
                st.session_state['sign_up_info']['email'] = email
                st.session_state['sign_up_info']['password'] = password
                st.session_state['is_signed_up'] = True
                st.success("Sign up successful! Please proceed to login.")
        else:
            st.error("Passwords do not match!")


if 'is_signed_up' in st.session_state and not st.session_state.get('is_logged_in', False):
    st.title("Log In")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Log In", key="login_button"):
        
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()
        if user and user[1] == password:
            st.session_state['is_logged_in'] = True
            st.success("Login successful! You can now generate emails.")
        else:
            st.error("Invalid email or password!")

# Direct login option for existing users
if not st.session_state.get('is_logged_in', False):
    st.title("Direct Login (Existing Users)")

    # Fetch all email addresses from the database
    c.execute("SELECT email FROM users")
    emails = [row[0] for row in c.fetchall()]

    existing_email = st.selectbox("Select your email", options=emails, key="direct_login_email")
    existing_password = st.text_input("Password", type="password", key="direct_login_password")

    if st.button("Log In (Existing User)", key="direct_login_button"):
        # Perform login validation
        c.execute("SELECT * FROM users WHERE email=?", (existing_email,))
        user = c.fetchone()
        if user and user[1] == existing_password:
            st.session_state['is_logged_in'] = True
            st.success("Login successful! You can now generate emails.")
        else:
            st.error("Invalid email or password!")

# Generate email page
if st.session_state.get('is_logged_in', False):
    st.title("Generate Email")

    backend = ml_backend()

    with st.form(key="form"):
        prompt = st.text_input("Describe the kind of email you want to be written.", key="email_prompt")
        st.text(f"(Example: Write me a professional-sounding email to my boss)")

        start = st.text_input("Begin writing the first few or several words of your email:", key="email_start")

        slider = st.slider("How many characters do you want your email to be? ", min_value=100, max_value=750, key="email_length")
        st.text("(A typical email is usually 100-500 characters)")

        submit_button = st.form_submit_button(label='Generate Email')

        if submit_button:
            with st.spinner("Generating Email..."):
                output = backend.generate_email(prompt, start)
            st.markdown("# Email Output:")
            st.subheader(start + output)

            st.markdown("__")

            st.subheader("You can press the Generate Email Button again if you're unhappy with the model's output")

            st.markdown("__")

            st.markdown("# Send Your Email Now")

            url = "https://mail.google.com/mail/?view=cm&fs=1&to=&su=&body=" + backend.replace_spaces_with_pluses(start + output)

            st.markdown("[Click me to send the email]({})".format(url))

# Close the database connection
conn.close()
