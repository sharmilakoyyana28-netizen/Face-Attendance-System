import streamlit as st
import cv2
import os
import numpy as np
from datetime import datetime
import pandas as pd

# --- CONFIG ---
ADMIN_PASSWORD = "sharmila123"  # change your password here
FACE_DATA = "faces_data"
ATTENDANCE_FILE = "attendance.csv"

st.set_page_config(page_title="Face Attendance", layout="centered")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# --- TABS (MUST BE AFTER import st) ---
tab1, tab2, tab3 = st.tabs(["Register", "Attendance", "Sheet"])

# ========== TAB 1 - REGISTER WITH PASSWORD ==========
with tab1:
    st.header("Register New Face (Admin Only)")
    
    if not st.session_state.authenticated:
        pwd = st.text_input("Enter Admin Password", type="password")
        if st.button("Unlock"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.success("Unlocked babe! Now you can register")
                st.rerun()
            else:
                st.error("Wrong password!")
    else:
        st.success("Admin unlocked 🔓")
        name = st.text_input("Name")
        roll = st.text_input("Roll Number")
        
        # YOUR EXISTING TAKE PHOTO + REGISTER CODE HERE
        # (keep your camera code inside this else block)
        
        st.write("--- Put your Take Photo and Register Face buttons here ---")
        
        if st.button("Lock Again"):
            st.session_state.authenticated = False
            st.rerun()

# ========== TAB 2 & 3 - YOUR EXISTING CODE ==========
with tab2:
    st.header("Mark Attendance")
    # your attendance code

with tab3:
    st.header("Attendance Sheet")
    # your sheet code
