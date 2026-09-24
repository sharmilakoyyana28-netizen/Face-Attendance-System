# At the very top of app.py - CHANGE THIS PASSWORD
ADMIN_PASSWORD = "sharmila123"  # <-- change to your own password

# Then in your Register tab section, add this:

tab1, tab2, tab3 = st.tabs(["Register", "Attendance", "Sheet"])

with tab1:
    st.header("Register New Face (Admin Only)")
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        pwd = st.text_input("Enter Admin Password to add students", type="password")
        if st.button("Unlock"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.success("Unlocked! Now you can register")
                st.rerun()
            else:
                st.error("Wrong password babe!")
    else:
        # YOUR EXISTING REGISTER CODE GOES HERE
        # (Take Photo, Register Face buttons)
        
        if st.button("Lock Again"):
            st.session_state.authenticated = False
            st.rerun()
