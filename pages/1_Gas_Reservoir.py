import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import linregress
import pandas as pd

st.page_link("Homepage.py", label="Go back to Homepage")
st.title("Gas Reservoir")

st.subheader("Gas Inflow Performance Relationship : ")


# Load sample data from local CSV
def load_sample_data():
    return pd.read_csv("./gas_well_data.csv")   # apne folder me sample_data.csv rakhna


# Function to collect input data
def collect_data():
    st.header("Upload CSV File or Use Sample Data:")
    option = st.radio("Choose Data Source:", ["Upload CSV", "Use Sample Data"])

    data = None
    if option == "Upload CSV":
        input_file = st.file_uploader("Upload File:", type=["csv"])
        if input_file is not None:
            df = pd.read_csv(input_file)
            data = pd.DataFrame(df)
            data.reset_index(drop=True, inplace=True)
            data.index = data.index + 1
            data.index.name = "S.No."
            st.write("Uploaded Data:")
            st.dataframe(data)

    else:
        data = load_sample_data()
        st.write("Sample Data Loaded:")
        data.reset_index(drop=True, inplace=True)
        data.index = data.index + 1
        data.index.name = "S.No."
        st.dataframe(data)
    return data


# 1. Simplified Backpressure
def simplified_backpressure(data):
    Pwf = data.iloc[:, 0].values
    Qg = data.iloc[:, 2].values
    Pr = max(Pwf)

    dp2 = (Pr**2 - Pwf**2)
    mask = (Qg > 0) & (dp2 > 0)

    log_dp2 = np.log(dp2[mask])
    log_Qg = np.log(Qg[mask])
    slope, intercept, _, _, _ = linregress(log_dp2, log_Qg)
    n = slope
    C = np.exp(intercept)

    pwf_range = np.linspace(Pr, 0, 20)
    Qg_pred = C * (Pr**2 - pwf_range**2)**n
    AOF = Qg_pred[-1]

    result_df = pd.DataFrame({
        "Pwf (psia)": np.round(pwf_range, 2),
        "Qg (Backpressure) (Mscf/day)": np.round(Qg_pred, 2)
    })

    return pwf_range, Qg_pred, AOF, C, n, result_df


# 2. LIT Pressure-Squared
def lit_pressure_squared(data):
    Pwf = data.iloc[:, 0].values
    Qg = data.iloc[:, 2].values
    Pr = max(Pwf)

    dp2 = (Pr**2 - Pwf**2)
    mask = (Qg > 0) & (dp2 > 0)

    X = Qg[mask]
    Y = dp2[mask] / Qg[mask]
    slope, intercept, _, _, _ = linregress(X, Y)
    a, b = intercept, slope

    pwf_range = np.linspace(Pr, 0, 20)
    dp2_range = Pr**2 - pwf_range**2

    Qg_pred = (-a + np.sqrt(a**2 + 4*b*dp2_range)) / (2*b)
    AOF = Qg_pred[-1]

    result_df = pd.DataFrame({
        "Pwf (psia)": np.round(pwf_range, 2),
        "Qg (LIT-Pressure²) (Mscf/day)": np.round(Qg_pred, 2)
    })

    return pwf_range, Qg_pred, AOF, a, b, result_df


# 3. LIT Pressure-Approximation
def lit_pressure_approx(data):
    Pwf = data.iloc[:, 0].values
    Qg = data.iloc[:, 2].values
    Pr = max(Pwf)

    dP = (Pr - Pwf)
    mask = (Qg > 0) & (dP > 0)

    X = Qg[mask]
    Y = dP[mask] / Qg[mask]
    slope, intercept, _, _, _ = linregress(X, Y)
    a1, b1 = intercept, slope

    pwf_range = np.linspace(Pr, 0, 20)
    dp_range = Pr - pwf_range

    Qg_pred = (-a1 + np.sqrt(a1**2 + 4*b1*dp_range)) / (2*b1)
    AOF = Qg_pred[-1]

    result_df = pd.DataFrame({
        "Pwf (psia)": np.round(pwf_range, 2),
        "Qg (LIT-Pressure Approx) (Mscf/day)": np.round(Qg_pred, 2)
    })

    return pwf_range, Qg_pred, AOF, a1, b1, result_df


# 4. LIT Pseudopressure Method
def lit_pseudopressure(data):
    Pwf = data.iloc[:, 0].values     # flowing pressure
    mp = data.iloc[:, 1].values      # pseudopressure m(p)
    Qg = data.iloc[:, 2].values      # gas rate

    psi_r = np.max(mp)
    k = psi_r / (np.max(Pwf) ** 2)

    pwf_range = np.linspace(np.max(Pwf), 0, 20)
    mp_range = k * (pwf_range ** 2)

    dpsi = psi_r - mp
    mask = (Qg > 0) & (dpsi > 0)

    X = Qg[mask]
    Y = dpsi[mask] / Qg[mask]
    slope, intercept, _, _, _ = linregress(X, Y)
    a2, b2 = intercept, slope

    dpsi_range = psi_r - mp_range
    Qg_pred = (-a2 + np.sqrt(a2**2 + 4 * b2 * dpsi_range)) / (2 * b2)
    AOF = Qg_pred[-1]

    result_df = pd.DataFrame({
        "Pwf (psia)": np.round(pwf_range, 2),
        "m(p)": np.round(mp_range, 2),
        "Qg (Pseudo-pressure) (Mscf/day)": np.round(Qg_pred, 2)
    })

    return pwf_range, Qg_pred, AOF, a2, b2, result_df


def main():
    data = collect_data()

    if data is not None and not data.empty:
        # Methods
        pwf_bp, qg_bp, AOF_bp, C, n, df_bp = simplified_backpressure(data)
        st.write("### Simplified Backpressure Method")
        st.latex(rf"Q_g = {C:.3e} \cdot (P_r^2 - P_{{wf}}^2)^{{{n:.3f}}}")
        st.write(f"**AOF (Back-Pressure): {AOF_bp:.2f} Mscf/day**")

        pwf_lit, qg_lit, AOF_lit, a, b, df_lit = lit_pressure_squared(data)
        st.write("### LIT Pressure-Squared Method")
        st.latex(rf"(P_r^2 - P_{{wf}}^2) = {a:.2f} Q_g + {b:.5f} Q_g^2")
        st.write(f"**AOF (LIT-Pressure²): {AOF_lit:.2f} Mscf/day**")

        pwf_litp, qg_litp, AOF_litp, a1, b1, df_litp = lit_pressure_approx(data)
        st.write("### LIT Pressure-Approximation Method")
        st.latex(rf"(P_r - P_{{wf}}) = {a1:.4f} Q_g + {b1:.5f} Q_g^2")
        st.write(f"**AOF (LIT-Pressure Approx): {AOF_litp:.2f} Mscf/day**")

        pwf_psi, qg_psi, AOF_psi, a2, b2, df_psi = lit_pseudopressure(data)
        st.write("### LIT Pseudopressure Method")
        st.latex(rf"(\psi_r - \psi_{{wf}}) = {a2:.2f} Q_g + {b2:.4f} Q_g^2")
        st.write(f"**AOF (Pseudo-pressure): {AOF_psi:.2f} Mscf/day**")

        # Comparison Table
        result_df = pd.concat([
            df_bp,
            df_lit["Qg (LIT-Pressure²) (Mscf/day)"],
            df_litp["Qg (LIT-Pressure Approx) (Mscf/day)"],
            df_psi["Qg (Pseudo-pressure) (Mscf/day)"]
        ], axis=1)
        result_df.reset_index(drop=True, inplace=True)
        result_df.index = result_df.index + 1
        result_df.index.name = "S.No."

        st.write("### IPR Values Table (Comparison of 4 Methods)")
        st.dataframe(result_df)

        # Error Table (compared with pseudo-pressure)
        error_df = pd.DataFrame({
            "Method": ["Back-Pressure", "LIT Pressure²", "LIT Pressure Approx"],
            "Error (%)": [
                  round(np.mean(np.abs((df_bp["Qg (Backpressure) (Mscf/day)"] - df_psi["Qg (Pseudo-pressure) (Mscf/day)"]) / df_psi["Qg (Pseudo-pressure) (Mscf/day)"]) * 100)),
                  round(np.mean(np.abs((df_lit["Qg (LIT-Pressure²) (Mscf/day)"] - df_psi["Qg (Pseudo-pressure) (Mscf/day)"]) / df_psi["Qg (Pseudo-pressure) (Mscf/day)"]) * 100)),
                  round(np.mean(np.abs((df_litp["Qg (LIT-Pressure Approx) (Mscf/day)"] - df_psi["Qg (Pseudo-pressure) (Mscf/day)"]) / df_psi["Qg (Pseudo-pressure) (Mscf/day)"]) * 100))
            ]
        })
        error_df.reset_index(drop=True, inplace=True)
        error_df.index = error_df.index + 1
        error_df.index.name = "S.No."

        st.write("### Error Table (Compared with Pseudo-pressure Method)")
        st.dataframe(error_df)

        # Plot
        fig, ax = plt.subplots()
        ax.plot(qg_bp, pwf_bp, "-o", label="Back-Pressure")
        ax.plot(qg_lit, pwf_lit, "-s", label="LIT Pressure²")
        ax.plot(qg_litp, pwf_litp, "-^", label="LIT Pressure Approx")
        ax.plot(qg_psi, pwf_psi, "-d", label="Pseudo-pressure")
        ax.set_xlabel("Qg (Mscf/day)")
        ax.set_ylabel("Pwf or Ψwf")
        ax.set_title("Gas IPR Comparison (4 Methods)")
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.legend()
        plt.xlim(left=0)
        plt.ylim(bottom=0)
        st.pyplot(fig)

    else:
        st.write("No data provided.")


if __name__ == "__main__":
    main()
