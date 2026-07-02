import streamlit as st
import numpy as np
import plotly.graph_objects as go
from utilities import read_file
from pdf_extraction import compute_xPDF, compute_ePDF

# Initialize session state variables
if 'sample_processor' not in st.session_state:
    st.session_state.sample_processor = None
if 'ref_processor' not in st.session_state:
    st.session_state.ref_processor = None


# Configure Streamlit page
st.set_page_config(
    page_title="scatt2PDF - Interactive GUI",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("Interactive PDF Extraction")

# Add CSS to style tab labels and reduce content font size
st.markdown("""
    <style>
        button[data-baseweb="tab"] {
            font-size: 16px !important;
            padding: 12px 24px !important;
        }
        .stTabs [data-baseweb="tab-list"] button {
            font-size: 16px;
        }
        /* Reduce font size in tab content */
        .stTabs [role="tabpanel"] {
            font-size: 13px;
        }
        /* Reduce markdown and other text */
        [role="tabpanel"] p {
            font-size: 13px !important;
        }
        /* Reduce heading sizes */
        [role="tabpanel"] h2 {
            font-size: 18px !important;
            margin-top: 1rem !important;
            margin-bottom: 0.5rem !important;
        }
        [role="tabpanel"] h3 {
            font-size: 15px !important;
            margin-top: 0.8rem !important;
            margin-bottom: 0.4rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

# Add stop button in sidebar
st.sidebar.markdown("---")
if st.sidebar.button("🛑 Stop App", type="secondary"):
    st.success("👋 Thanks for using scatt2PDF! Session ended.")
    st.stop()

# Create two tabs (Define Sample/Ref first, then PDF Extraction)
tab1, tab2 = st.tabs([" Define Sample and Reference", "📈 Extract xPDF"])

# ============================================================================
# TAB 1: DEFINE EXPERIMENT, SAMPLE AND REFERENCE DATA
# ============================================================================
with tab1:
    st.markdown("## ⚙️ Define Experiment")
    # menu déroulant pour type of radiation
    radiation_type = st.selectbox(
        "Select radiation type",
        options=["X-ray", "Electron"],
        index=0,
        help="Select the type of radiation used in the experiment."
    )
    
    # champs pour la longueur d'onde
    wavelength = st.number_input(
        "Wavelength (Å)",
        value=0.71073 if radiation_type == "X-ray" else 0.0251,
        step=0.01,
        format="%.5f",
        help="Enter the wavelength of the radiation in Angstroms (Å)."
    )

    st.markdown("#  Define Sample and Reference")
    # Menu déroulant pour le type de données
    data_unit = st.selectbox(
        "Select data unit",
        options=["tth", "q_nm", "q_A"],
        index=0,
        help="Select the unit of the data in the files: 'tth' for two-theta angles or 'q_nm' or 'q_A' for Q values."
    )
    col_sample, col_ref = st.columns(2)

    # ========== SAMPLE COLUMN ==========
    with col_sample:
        st.markdown("### 🔵 Sample")

        # --- 1. Upload files ---
        st.markdown("#### Upload Files")

        sample_file = st.file_uploader(
            "Sample data file",
            type=None,
            key="sample_image",
        )
        q_sample, I_sample = None, None
        if sample_file is not None:
            q_sample, I_sample = read_file(sample_file, wavelength=float(wavelength), unit=str(data_unit))

        # Plot data if available
        if q_sample is not None and I_sample is not None:
            fig_sample = go.Figure()
            fig_sample.add_trace(go.Scatter(
                x=q_sample, y=I_sample, mode='lines', name='Sample Data',
                line=dict(color='blue', width=2),
                hovertemplate='Q: %{x:.3f}<br>I: %{y:.3e}<extra></extra>'
            ))
            fig_sample.update_layout(
                title="Sample Data",
                xaxis_title=r"$q (\AA^{-1})$",
                yaxis_title="Intensity",
                hovermode='x unified',
                showlegend=True,
                legend=dict(x=0.7, y=0.95),
                height=400,
                margin=dict(l=60, r=40, t=60, b=50)
            )
            st.plotly_chart(fig_sample, use_container_width=True)
        

        
    # ========== REFERENCE COLUMN ==========
    with col_ref:
        st.markdown("### 🔴 Reference")

        # --- 1. Upload files ---
        st.markdown("#### Upload Files")

        ref_file = st.file_uploader(
            "Reference data file",
            type=None,
            key="ref_image",
        )
        q_ref, I_ref = None, None
        if ref_file is not None:
            q_ref, I_ref = read_file(ref_file, wavelength=float(wavelength), unit=str(data_unit))

        # Plot data if available
        if q_ref is not None and I_ref is not None:
            fig_ref = go.Figure()
            fig_ref.add_trace(go.Scatter(
                x=q_ref, y=I_ref, mode='lines', name='Reference Data',
                line=dict(color='red', width=2),
                hovertemplate='Q: %{x:.3f}<br>I: %{y:.3e}<extra></extra>'
            ))
            fig_ref.update_layout(
                title="Reference Data",
                xaxis_title=r"$q (\AA^{-1})$",
                yaxis_title="Intensity",
                hovermode='x unified',
                showlegend=True,
                legend=dict(x=0.7, y=0.95),
                height=400,
                margin=dict(l=60, r=40, t=60, b=50)
            )
            st.plotly_chart(fig_ref, use_container_width=True)

# ============================================================================
# TAB 2: PDF EXTRACTION
# ============================================================================
with tab2:
    st.markdown("# 📈 Extract xPDF")
    st.markdown("**Calculate the Pair Distribution Function (PDF) . Adjust parameters with interactive sliders.**")
    
    # Check if processors are defined
    if q_sample is None or I_sample is None:
        st.warning("⚠️ Please define sample and reference in the 'Define Sample and Reference' tab first")
        st.stop()
    
    # ========== DEFAULT VALUES ==========
    _default_bgscale = 1.0
    _default_qmin = 0.5
    _default_qmax = 16.6
    _default_qmaxinst = 16.6
    _default_rpoly = 0.9
    _default_lorch = True
    _default_composition = "Au"
    
    # ========== INPUT PARAMETERS SECTION ==========
    st.markdown("## 📋 Input Parameters")
    
    composition = st.text_input("Chemical composition", value=_default_composition, placeholder="e.g., Au, NaCl, Au3Cu")
    
    st.markdown("## ⚙️ Output Parameters")
    
    col_out1, col_out2 = st.columns(2)
    
    with col_out1:
        st.markdown("**R-space Range**")
        rmin = st.number_input("rmin (Å)", value=0.0, step=0.1)
        rmax = st.number_input("rmax (Å)", value=50.0, step=0.1)
    
    with col_out2:
        st.markdown("**Output File**")
        rstep = st.number_input("rstep (Å)", value=0.01, step=0.001)
        samplename = st.text_input("Sample name (optional)", value="", placeholder="Leave empty to use default filename")
        
        # Generate output_file based on samplename
        if samplename:
            output_file = f"{samplename}.gr"
        else:
            output_file = "xPDF_results.gr"
    
    # ========== PROCESSING SECTION ==========
    st.markdown("## 📊 PDF Calculation")
    if I_ref is not None and q_sample is not None and q_ref is not None:
        I_ref_interp = np.interp(q_sample, q_ref, I_ref)
    else:
        I_ref_interp = None
    
    # Processing button
    if st.button("Calculate PDF", type="primary"):
        
        
        try:
            
                
            
            # Store data in session state for interactive controls
            st.session_state.q_data = q_sample
            st.session_state.I_data = I_sample
            st.session_state.I_ref = I_ref_interp
            st.session_state.composition = composition
            st.session_state.rmin = rmin
            st.session_state.rmax = rmax
            st.session_state.rstep = rstep
            
            
            st.session_state.data_ready = True
            
        except Exception as e:
            st.error(f"❌ Error during data processing: {e}")
            import traceback
            st.error(traceback.format_exc())
    
    # Display interactive controls if data is ready
    if hasattr(st.session_state, 'data_ready') and st.session_state.data_ready:
        st.subheader("⚙️ Interactive Parameters")
        
        st.markdown("**Adjust these parameters to refine the PDF calculation:**")
        
        # Create two columns: left for controls, right for plots
        col_controls, col_plots = st.columns([1.2, 2.8], gap="large")
        
        q_max_data = float(np.max(st.session_state.q_data))
        
        # Put all sliders in LEFT column
        with col_controls:
            st.markdown("### 🎚️ Parameters")
            bgscale_int = st.slider("bgscale", 0.0, 2.5, _default_bgscale, 0.01, key="bgscale_slider")
            qmin_int = st.slider("qmin (Å⁻¹)", 0.1, q_max_data, _default_qmin, 0.1, key="qmin_slider")
            qmax_int = st.slider("qmax (Å⁻¹)", float(np.min(st.session_state.q_data)), q_max_data, _default_qmax, 0.1, key="qmax_slider")
            qmaxinst_int = st.slider("qmaxinst (Å⁻¹)", float(np.min(st.session_state.q_data)), q_max_data, _default_qmaxinst, 0.1, key="qmaxinst_slider")
            rpoly_int = st.slider("rpoly", 0.1, 10.0, _default_rpoly, 0.1, key="rpoly_slider")
            lorch_int = st.checkbox("Lorch window correction", value=_default_lorch, key="lorch_checkbox")
            
            st.markdown("---")
            st.markdown("### 📥 Download")
        
        # Call compute_xPDF with plot=False to get data only
        if radiation_type == "X-ray":
            r_pdf, G_pdf = compute_xPDF(
                q=st.session_state.q_data,
                Iexp=st.session_state.I_data,
                composition=st.session_state.composition,
                Iref=st.session_state.I_ref,
                bgscale=bgscale_int,
                qmin=qmin_int,
                qmax=qmax_int,
                qmaxinst=qmaxinst_int,
                rmin=st.session_state.rmin,
                rmax=st.session_state.rmax,
                rstep=st.session_state.rstep,
                rpoly=rpoly_int,
                Lorch=lorch_int,
                plot=False
            )
        elif radiation_type == "Electron":
            r_pdf, G_pdf = compute_ePDF(
                q=st.session_state.q_data,
                Iexp=st.session_state.I_data,
                composition=st.session_state.composition,
                Iref=st.session_state.I_ref,
                bgscale=bgscale_int,
                qmin=qmin_int,
                qmax=qmax_int,
                qmaxinst=qmaxinst_int,
                rmin=st.session_state.rmin,
                rmax=st.session_state.rmax,
                rstep=st.session_state.rstep,
                rpoly=rpoly_int,
                Lorch=lorch_int,
                plot=False
            )
        # Create CSV content for download before displaying plots
        output_data = np.column_stack((r_pdf, G_pdf))
        import io
        csv_buffer = io.StringIO()
        
        # Create header compatible with PDFGetX3/xpdfsuite format
        header = '[DEFAULT]\n\n'
        header += 'version = xpdfsuite 1.0\n\n'
        header += '#input and output specifications\n'
        header += 'dataformat = q_A\n'
        header += f'outputtype = gr\n\n'
        header += '#PDF calculation setup\n'
        header += 'mode = xrays\n'
        header += f'composition = {st.session_state.composition}\n'
        header += f'bgscale = {bgscale_int:.2f}\n'
        header += f'rpoly = {rpoly_int:.2f}\n'
        header += f'qmaxinst = {qmaxinst_int:.2f}\n'
        header += f'qmin = {qmin_int:.2f}\n'
        header += f'qmax = {qmax_int:.2f}\n'
        header += f'rmin = {st.session_state.rmin:.2f}\n'
        header += f'rmax = {st.session_state.rmax:.2f}\n'
        header += f'rstep = {st.session_state.rstep:.2f}\n\n'
        header += '# End of config --------------------------------------------------------------\n'
        header += '#### start data\n\n'
        header += '#S 1\n'
        header += '#L r(Å)  G(r)(Å^{-2})\n'
        
        csv_buffer.write(header)
        for r_val, g_val in zip(r_pdf, G_pdf):
            csv_buffer.write(f"{r_val:.6f} {g_val:.8f}\n")
        csv_content = csv_buffer.getvalue().encode('utf-8')
        
        # Import functions for intermediate calculations
        from pdf_extraction import (
            compute_avg_scattering_factor,
            compute_f2avg,
            fit_polynomial_background,
        )
        
        # Display plots in RIGHT column
        with col_plots:
            q = st.session_state.q_data
            Iexp_orig = st.session_state.I_data  # Original, unmodified
            I_ref = st.session_state.I_ref
            
            # Compute intermediate values
            qstep = q[1] - q[0]
            q_f2, f2avg = compute_f2avg(
                formula=st.session_state.composition,
                x_max=qmax_int,
                x_step=qstep,
                qvalues=True,
                xray=(radiation_type == "X-ray"),
            )
            q_f, favg = compute_avg_scattering_factor(
                formula=st.session_state.composition,
                x_max=qmax_int,
                x_step=qstep,
                qvalues=True,
                xray=(radiation_type == "X-ray"),
            )
            f2avg_interp = np.interp(q, q_f2, f2avg)
            favg_interp = np.interp(q, q_f, favg)
            favg2_interp = favg_interp**2
            
            # Modified intensity for plot 2
            Iexp_corrected = Iexp_orig.copy()
            if I_ref is not None:
                Iexp_corrected = Iexp_corrected - bgscale_int * I_ref

            finite = (
                np.isfinite(Iexp_corrected)
                & np.isfinite(f2avg_interp)
                & np.isfinite(favg2_interp)
                & (favg2_interp > 0)
            )
            mask_inf = finite & (q > 0.9 * qmax_int)
            if np.any(mask_inf):
                den = np.mean(Iexp_corrected[mask_inf])
                num = np.mean(f2avg_interp[mask_inf])
            else:
                den = np.mean(Iexp_corrected[finite])
                num = np.mean(f2avg_interp[finite])
            alpha = num / den if den != 0 else 1.0

            Sminus1 = (alpha * Iexp_corrected - f2avg_interp) / np.maximum(
                favg2_interp, np.finfo(float).eps
            )
            Fm = q * Sminus1
            
            background = fit_polynomial_background(
                q, Fm, rpoly=rpoly_int, qmin=qmin_int, qmax=qmaxinst_int
            )
            Fc = Fm - background
        
            # Create 3 separate figures with individual legends, maintaining original layout
            mask_plot = (q >= qmin_int) & (q <= qmax_int)
            
            # ===== FIGURE 1: Raw Intensities =====
            fig1 = go.Figure()
            
            q_plot1 = q.tolist()
            iexp_plot1 = Iexp_orig.tolist()
            
            fig1.add_trace(
                go.Scatter(x=q_plot1, y=iexp_plot1, mode='lines', name='Iexp (raw)',
                          line=dict(color='blue', width=2),
                          hovertemplate='Q: %{x:.3f}<br>I: %{y:.3e}<extra></extra>')
            )
            
            if I_ref is not None:
                I_ref_bgscaled = (bgscale_int * I_ref).tolist()
                fig1.add_trace(
                    go.Scatter(x=q_plot1, y=I_ref_bgscaled, mode='lines',
                              name=f'bgscale×Iref (scale={bgscale_int:.2f})',
                              line=dict(color='red', width=2),
                              hovertemplate='Q: %{x:.3f}<br>I: %{y:.3e}<extra></extra>')
                )
            
            # Calculate Y-axis limits based on data in [qmin, qmax]
            iexp_in_range = Iexp_orig[mask_plot]
            y_min_plot1 = np.min(iexp_in_range) if len(iexp_in_range) > 0 else 0
            y_max_plot1 = np.max(iexp_in_range) if len(iexp_in_range) > 0 else 1
            if I_ref is not None:
                iref_in_range = bgscale_int * I_ref[mask_plot]
                y_min_plot1 = min(y_min_plot1, np.min(iref_in_range))
                y_max_plot1 = max(y_max_plot1, np.max(iref_in_range))
            
            y_margin = 0.05 * (y_max_plot1 - y_min_plot1)
            
            fig1.update_layout(
                title="1. Raw Intensities (for bgscale adjustment)",
                xaxis_title="Q (Å⁻¹)",
                yaxis_title="Intensity",
                hovermode='x unified',
                showlegend=True,
                legend=dict(x=0.7, y=0.95),
                height=350,
                margin=dict(l=60, r=40, t=60, b=50)
            )
            fig1.update_xaxes(range=[qmin_int, qmax_int])
            fig1.update_yaxes(range=[y_min_plot1 - y_margin, y_max_plot1 + y_margin])
            
            # ===== FIGURE 2: Corrected Structure Factor =====
            fig2 = go.Figure()
            
            q_plot2 = q.tolist()
            fc_plot2 = Fc.tolist()
            
            fig2.add_trace(
                go.Scatter(x=q_plot2, y=fc_plot2, mode='lines', 
                          name=f'F(Q) (rpoly={rpoly_int:.2f})',
                          line=dict(color='darkblue', width=2),
                          hovertemplate='Q: %{x:.3f}<br>F(Q): %{y:.3e}<extra></extra>')
            )
            
            # Calculate Y-axis limits for F(Q) based on data in [qmin, qmax]
            fc_in_range = Fc[mask_plot]
            fc_valid = fc_in_range[np.isfinite(fc_in_range)]
            y_min_plot2 = np.min(fc_valid) if len(fc_valid) > 0 else 0
            y_max_plot2 = np.max(fc_valid) if len(fc_valid) > 0 else 1
            
            y_margin2 = 0.05 * (y_max_plot2 - y_min_plot2)
            
            fig2.update_layout(
                title="2. Corrected Structure Factor",
                xaxis_title="Q (Å⁻¹)",
                yaxis_title="F(Q)",
                hovermode='x unified',
                showlegend=True,
                legend=dict(x=0.7, y=0.95),
                height=350,
                margin=dict(l=60, r=40, t=60, b=50)
            )
            fig2.update_xaxes(range=[qmin_int, qmax_int])
            fig2.update_yaxes(range=[y_min_plot2 - y_margin2, y_max_plot2 + y_margin2])
            
            # Display first two figures side by side
            col_fig1, col_fig2 = st.columns(2)
            with col_fig1:
                st.plotly_chart(fig1, use_container_width=True)
            with col_fig2:
                st.plotly_chart(fig2, use_container_width=True)
            
            # ===== FIGURE 3: Radial Distribution Function =====
            fig3 = go.Figure()
            
            fig3.add_trace(
                go.Scatter(x=r_pdf, y=G_pdf, mode='lines', 
                          name=f'G(r) (rpoly={rpoly_int:.2f})',
                          line=dict(color='darkgreen', width=2),
                          hovertemplate='r: %{x:.3f}<br>G(r): %{y:.3e}<extra></extra>')
            )
            
            fig3.update_layout(
                title="3. Radial Distribution Function (PDF)",
                xaxis_title="r (Å)",
                yaxis_title="G(r)",
                hovermode='x unified',
                showlegend=True,
                legend=dict(x=0.7, y=0.95),
                height=350,
                margin=dict(l=60, r=40, t=60, b=50)
            )
            
            st.plotly_chart(fig3, use_container_width=True)
        
        # Put download button in LEFT column
        with col_controls:
            st.download_button(
                label="💾 Download PDF Results",
                data=csv_content,
                file_name=output_file,
                mime="text/plain"
            )

# Footer
st.markdown("---")
st.markdown("💡 **scatt2PDF** - Interactive interface for PDF analysis from X-ray/electron scattering data")
st.markdown("Developed by Nicolas Ratel-Ramond - LPCNO-CNRS - 2026")
