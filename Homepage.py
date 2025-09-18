import streamlit as st

# Title
st.markdown(
    "<h1 style='text-align:center; color:#4CAF50;'>Inflow Performance Curve (IPR) Calculation</h1>",
    unsafe_allow_html=True
)

# Intro
intro = '''
This project focuses on analyzing **Inflow Performance Relationships (IPR)** for oil and gas reservoirs using different methods such as **Vogel, Fetkovich, Laminar-Inertial-Turbulent (LIT), and Pseudo-pressure** approaches.  
IPR provides a crucial relationship between reservoir pressure and well production rate, helping engineers estimate well deliverability under varying conditions.  

With CSV inputs or sample data, this tool automates IPR calculations, plots performance curves, and compares methods, offering a practical solution for production optimization and reservoir management.
'''
st.markdown(intro)

st.divider()

# Two Columns for Options
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div style="background-color:#f9f9f9; border-radius:12px; padding:20px; min-height:200px; 
                    box-shadow:0px 2px 6px rgba(0,0,0,0.1); text-align:center;">
            <h3 style="color:green;">Oil Reservoir</h3>
            <p style="color:black;">IPR Calculation using Constant J Approach, Vogel's and Fetkovich's IPR equations.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<div style='text-align:center; margin-top:15px;'>", unsafe_allow_html=True)
    st.page_link("pages/2_Oil_Reservoir.py", label="👉 Click Here")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown(
        """
        <div style="background-color:#f9f9f9; border-radius:12px; padding:20px; min-height:200px; 
                    box-shadow:0px 2px 6px rgba(0,0,0,0.1); text-align:center;">
            <h3 style="color:red;">Gas Reservoir</h3>
            <p style="color:black;">IPR Calculation using Simplified Back-pressure Equation and Laminar-Inertial-Turbulent (LIT) methods.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("<div style='text-align:center; margin-top:15px;'>", unsafe_allow_html=True)
    st.page_link("pages/1_Gas_Reservoir.py", label="👉 Click Here")
    st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# Footer with LinkedIn links
st.markdown(
    """
    <div style="text-align:center; padding:10px; margin-top:30px; font-size:16px; color:gray;">
        🚀 Made with ❤️ by 
        <a href="https://www.linkedin.com/in/kayashth1" target="_blank" style="text-decoration:none; color:#4CAF50;"><b>Yash</b></a>
        and 
        <a href="https://www.linkedin.com/in/prem-mehtre-78b525244/" target="_blank" style="text-decoration:none; color:#4CAF50;"><b>Prem</b></a> 
    </div>
    """,
    unsafe_allow_html=True
)
