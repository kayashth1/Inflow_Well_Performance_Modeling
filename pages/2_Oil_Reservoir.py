import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import pandas as pd

if st.button("Go back to Homepage"):
   st.switch_page("Homepage.py")

st.title("Oil Reservoir")

st.header("Vogel Reservoir Model:")
st.write("Vogel's IPR quadratic equation is defined as: ")

st.latex(r''' \frac{Q}{AOF}= 1-0.2\frac{Pwf}{Pws}-0.8\left(\frac{Pwf}{Pws}\right)^{2}''')
st.latex(r'''(Q= AOF \cdot \left[1-0.2\frac{Pwf}{Pws}-0.8\left(\frac{Pwf}{Pws}\right)^{2}\right]''')

#DATA COLLECT KARO (INPUT):-
def collect_data():
  st.subheader("Enter the following values:")
  Pb = float(st.text_input("Enter Bubble Point Pressure:", "0"))
  Pws = float(st.text_input("Enter Stabilized Reservoir Pressure:", "0"))

  Pwf = float(st.text_input("Enter Flowing Pressure 1:", "0",key="Pwf"))
  if Pwf > Pws:
    st.error("❌ Flowing Pressure (Pwf) cannot be greater than Stabilized Reservoir Pressure (Pws).")
  Qwf = float(st.text_input("Enter Flow rate at above flowing pressure 1:", "0",key="Qwf"))
  
  if Pws<Pb:
      Pwf1 = float(st.text_input("Enter Flowing Pressure 2:", "0",key="Pwf1"))
      if Pwf1 > Pws:
          st.error("❌ Flowing Pressure (Pwf) cannot be greater than Stabilized Reservoir Pressure (Pws).")
      Qwf1 = float(st.text_input("Enter Flow rate at above flowing pressure 2:", "0",key="Qwf1"))
  else:
      Pwf1=0
      Qwf1=0
  data=pd.DataFrame([{
      "Pb (bar)":Pb,
      "Pws (bar)": Pws,
      "Pwf (bar)": Pwf,
      "Rate (m3/d)": Qwf,
      "Pwf (bar)1": Pwf1,
      "Rate (m3/d)1": Qwf1
  }])
  return data

def generate_pressure_points(Pws,end, num_points=10):
    return np.linspace(Pws, end, num_points).tolist()

st.divider()

#Get Q_max:
def return_Qmax(Qwf,Pwf,Pws):
   Qmax=(Qwf/(1 - 0.2 * (Pwf / Pws) - 0.8 * (Pwf / Pws)**2))
   return Qmax

# Vogel IPR curve equation:
def curve_IPR_Vogel(Pwf, Pws, Qmax):
    return Qmax * (1 - 0.2 * (Pwf / Pws) - 0.8 * (Pwf / Pws)**2)

#Find Productivity Index: 
def Productivity_Index(Qwf,Pws,Pwf):
    J=(Qwf/(Pws-Pwf))
    return J
# Constant J approach IPR curve equation:
def curve_IPR_constJ(J,Pws,Pwf):
    return J*(Pws-Pwf)

def undersaturated1(Qob,J,Pb,Pwf):
    Q=Qob+(((J*Pb)/1.8)*(1 - 0.2 * (Pwf / Pb) - 0.8 * (Pwf / Pb)**2))
    return Q

def Calc_J(Qwf,Pws,Pb,Pwf):
    J=Qwf/((Pws-Pb)+((Pb/1.8)*(1 - 0.2 * (Pwf / Pb) - 0.8 * (Pwf / Pb)**2)))
    return J

#Function for Fekovich (ISME IMPROVEMENT KR SKTE H -WITH LINEAR REGRESSION ON BEST FIT LINE ON 4 DATA INPUTS POINTS)
def fetkovich(Pwf,Qwf,Pwf1,Qwf1,Pws):
    n=float(np.log(Qwf1/Qwf)/np.log((Pws**2-Pwf1**2)/(Pws**2-Pwf**2)))
    c=(Qwf/((Pws**2-Pwf**2)**n))
    return n,c

#Fetkvich ka Q ka function h:
def curve_fetkovich(n,c,Pwf,Pws):
    return c*((Pws**2-Pwf**2)**n)

#YE MAIN FUNCTION H:-
def main():
    data = collect_data()
    if (data[["Pb (bar)", "Pws (bar)", "Pwf (bar)", "Rate (m3/d)"]].sum().sum() == 0):
        st.warning("⚠️ Please enter the data to proceed!")
        return
    
    else:
        Pws = data["Pws (bar)"].iloc[0]
        Pwf = data["Pwf (bar)"].iloc[0]
        Qwf = data["Rate (m3/d)"].iloc[0]
        Pb = data["Pb (bar)"].iloc[0]
        Pwf1 = data["Pwf (bar)1"].iloc[0]
        Qwf1 = data["Rate (m3/d)1"].iloc[0]

    # YE SARA VOGEL'S, CONSTANT J APPROACH AND FETKOVICH EQUATION (ONLY FOR SATURATED RESERVOIR):-
        if Pws<Pb:
            Pressure_points=generate_pressure_points(Pws,0)
            n,c=fetkovich(Pwf,Qwf,Pwf1,Qwf1,Pws)
            Qmax=return_Qmax(Qwf,Pwf,Pws)   
            
            
            st.subheader("Reservoir is Saturated Reservoir.")
            st.write(f"Performance Coefficient C is : {c:.2f}")
            st.write(f"Fetkovich Exponent n is : {n:.2f}")
            Vogels_Q_values = [curve_IPR_Vogel(i, Pws, Qmax) for i in Pressure_points]
            J = Productivity_Index(Qwf, Pws, Pwf)
            ConstantJ_Qvalues = [curve_IPR_constJ(J, Pws, i) for i in Pressure_points]

            Fetkovich_Q_values=[curve_fetkovich(n,c,i,Pws) for i in Pressure_points]         

            st.write(f"Calculated Absolute Open Potential(AOF) from Constant J approach IPR Equation : {ConstantJ_Qvalues[-1]:.2f} m³/d") 
            st.write(f"Calculated Absolute Open Potential(AOF) from Vogel's IPR Equation : {Vogels_Q_values[-1]:.2f} m³/d") 
            st.write(f"Calculated Absolute Open Potential(AOF) from Fetkovich's IPR Equation : {Fetkovich_Q_values[-1]:.2f} m³/d") 

            Qmax=max(ConstantJ_Qvalues[-1],Vogels_Q_values[-1],Fetkovich_Q_values[-1])
            # Create table with serial numbers
            df = pd.DataFrame({
                "Pwf (bar)": Pressure_points,
                "Vogel's Q (m³/d)": Vogels_Q_values,
                "Constant J approach Q (m³/d)": ConstantJ_Qvalues,
                "Fetkovich_Q_values Q (m³/d)":Fetkovich_Q_values
            })

            # Add Serial Number starting from 1
            df.index = df.index + 1
            df.index.name = "S.No"

            st.subheader("Comparison Table")
            st.dataframe(df)

            # Plotting both curves
            plt.figure(figsize=(10, 7))
            plt.plot( df["Constant J approach Q (m³/d)"],df["Pwf (bar)"], marker="s", label="Constant J IPR")
            plt.plot(df["Vogel's Q (m³/d)"],df["Pwf (bar)"] , marker="o", label="Vogel's IPR")
            plt.plot(df["Fetkovich_Q_values Q (m³/d)"],df["Pwf (bar)"],  marker="v", label="Fetkovich_Q_values")
            plt.xlabel("Flow Rate (m³/d)")
            plt.ylabel("Flowing Pressure (Pwf) [bar]")
            plt.title("IPR Curve Comparison: Vogel vs Constant J vs Fetkovich")
            plt.grid(True)
            plt.legend()
            plt.ylim(0,Pws+100)
            try:
                plt.set_xlim(0, Qmax + 100)
            except:
                    st.write("") 

            plt.xlim(left=0)
            plt.ylim(bottom=0)
            st.pyplot(plt)
        else:
            st.subheader("Reservoir is Unsaturated Reservoir.")

            Pressure_points_Pwsto_Pb=generate_pressure_points(Pws,Pb)
            Pressure_points_Pbto_0=generate_pressure_points(Pb,0)[1:]

            if Pwf>Pb :
                J=Productivity_Index(Qwf,Pws,Pwf)
                st.write(f"Productivity Index : {J:2f}")
                Qob=J*(Pws-Pb)
                # Vogel:-
                st.write(f"Flow rate at Bubble Point Pressure : {Qob:.2f}")
                Q_above_Pb=[curve_IPR_constJ(J,Pws,i) for i in Pressure_points_Pwsto_Pb]
                Q_below_Pb=[undersaturated1(Qob,J,Pb,i) for i in Pressure_points_Pbto_0]
                Qmax=undersaturated1(Qob,J,Pb,0)
                        
                

                All_Pressure_points=Pressure_points_Pwsto_Pb+Pressure_points_Pbto_0
                All_Q_values=Q_above_Pb+Q_below_Pb

                # Fetkovich:-
                Q_below_Pb1=[(J*( (Pws-Pb) + (1/(2*Pb))*(Pb**2-i**2) )) for i in Pressure_points_Pbto_0]
                All_Q_values1=Q_above_Pb+Q_below_Pb1
                Qmax1=All_Q_values1[-1]

                st.write(f"Calculated Absolute Open Potential(AOF) according to Vogel's IPR Equation : {Qmax:.2f} m³/d")  # fix here
                st.write(f"Calculated Absolute Open Potential(AOF) according to Fetkovich's IPR Equation : {Qmax1:.2f} m³/d")  # fix here

                df=pd.DataFrame({
                    "Pwf (bar)":All_Pressure_points,
                    "Vogel's Q (m³/d)":All_Q_values,
                    "Fetkovich's Q (m³/d)":All_Q_values1
                })
                df.index = df.index + 1
                df.index.name = "S.No"
                st.dataframe( df.style.set_table_styles(
                        [{'selector': 'td', 'props': [('text-align', 'center'),('justify-content','center')]},
                        {'selector': 'th', 'props': [('text-align', 'center'),('justify-content','center')]}]
                    ).set_properties(**{'text-align': 'center'}))
                

                plt.figure(figsize=(10,7))
                plt.plot( df["Vogel's Q (m³/d)"],df["Pwf (bar)"], marker="o", label="Vogel's IPR")
                plt.plot( df["Fetkovich's Q (m³/d)"],df["Pwf (bar)"], marker="p", label="Fetkovich's IPR")
                plt.xlabel("Flow Rate (m³/d)")
                plt.ylabel("Flowing Pressure (Pwf) [bar]")
                plt.title("IPR Curve")
                plt.grid(True)
                plt.legend()
                try:
                    plt.set_xlim(0, Qmax + 100)
                except:
                    st.write("")

                plt.ylim(0,Pws+100)
                plt.axhline(y=Pb, color="red", linestyle="--", label="Bubble Point (Pb)")
                plt.text(Qmax*0.5, Pb+200, "Undersaturated Reservoir Region", color="green", fontsize=10, ha="center")
                plt.text(Qmax*0.5, Pb-200, "Saturated Reservoir Region", color="blue", fontsize=10, ha="center")
                plt.xlim(left=0)
                plt.ylim(bottom=0)
                st.pyplot(plt)
            else:
                J=Calc_J(Qwf,Pws,Pb,Pwf)
                J1=Productivity_Index(Qwf,Pws,Pwf)
                st.write(f"Vogels's productivity Index : {J:.2f}")
                st.write(f"Fetkovich's productivity Index : {J1:.2f}")
                # Vogel
                Qob=J*(Pws-Pb)
                st.write(f"Flow rate at Bubble Point Pressure using Vogel's Equation : {Qob:.2f} m³/d")

                Pressure_points_Pwsto_Pb=generate_pressure_points(Pws,Pb)
                Pressure_points_Pbto_0=generate_pressure_points(Pb,0)[1:]

                Q_above_Pb=[(J*(Pws-i)) for i in Pressure_points_Pwsto_Pb]
                Q_below_Pb=[(Qob + ((J*Pb)/1.8)*(1 - 0.2*(i/Pb) - 0.8*(i/Pb)**2)) for i in Pressure_points_Pbto_0]
                
                All_Pressure_points=Pressure_points_Pwsto_Pb+Pressure_points_Pbto_0
                All_Q_values=Q_above_Pb+Q_below_Pb

            # Fetkovich
                Qob1=J1*(Pws-Pb)
                st.write(f"Flow rate at Bubble Point Pressure using Fetkovich's Equation : {Qob1:.2f} m³/d")
                Q_above_Pb1=[(J1*(Pws-i)) for i in Pressure_points_Pwsto_Pb]
                Q_below_Pb1=[(J1*( (Pws-Pb) + (1/(2*Pb))*(Pb**2-i**2) )) for i in Pressure_points_Pbto_0]
                All_Q_values1=Q_above_Pb1+Q_below_Pb1

                Qmax=All_Q_values[-1]
                Qmax1=All_Q_values1[-1]
                st.write(f"Calculated Absolute Open Potential(AOF) from Vogel's IPR : {Qmax:.2f} m³/d") 
                st.write(f"Calculated Absolute Open Potential(AOF) from Fetkovich's IPR : {Qmax1:.2f} m³/d") 

                df=pd.DataFrame({
                    "Pwf (bar)":All_Pressure_points,
                    "Vogel's Q (m³/d)":All_Q_values,
                    "Fetkovich's Q (m³/d)":All_Q_values1
                })
                df.index = df.index + 1
                df.index.name = "S.No"
                st.dataframe( df.style.set_table_styles(
                        [{'selector': 'td', 'props': [('text-align', 'center'),('justify-content','center')]},
                        {'selector': 'th', 'props': [('text-align', 'center'),('justify-content','center')]}]
                    ).set_properties(**{'text-align': 'center'}))
                
                Qmaxt=max(All_Q_values[-1],All_Q_values1[-1])
                plt.figure(figsize=(10,7))
                plt.plot( df["Vogel's Q (m³/d)"],df["Pwf (bar)"], marker="o", label="Vogel's IPR")
                plt.plot( df["Fetkovich's Q (m³/d)"],df["Pwf (bar)"], marker="p", label="Fetkovich IPR")
                plt.xlabel("Flow Rate (m³/d)")
                plt.ylabel("Flowing Pressure (Pwf) [bar]")
                plt.title("IPR Curve")
                plt.grid(True)
                plt.legend()
                try:
                    plt.set_xlim(0, Qmaxt + 100)
                except:
                    st.write("")

                plt.ylim(0,Pws+100)
                plt.axhline(y=Pb, color="red", linestyle="--", label="Bubble Point (Pb)")
                plt.text(Qmaxt*0.5, Pb+200, "Undersaturated Reservoir Region", color="green", fontsize=10, ha="center")
                plt.text(Qmaxt*0.5, Pb-200, "Saturated Reservoir Region", color="blue", fontsize=10, ha="center")

                plt.xlim(left=0)
                plt.ylim(bottom=0)
                st.pyplot(plt)

if __name__ == "__main__":
    main()
