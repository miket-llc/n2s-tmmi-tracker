"""
Enhanced TMMi Progression Dashboard Component

This component provides comprehensive analysis of an organization's readiness
to progress to the next TMMi maturity level, including:
- Current level vs. target level readiness
- Process area breakdown with TMMi bands
- Gap analysis with specific action recommendations
- Generic goal compliance
- Evidence coverage analysis
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict
from src.models.database import TMMiQuestion, AssessmentAnswer
from src.utils.scoring import generate_progression_dashboard_data


def render_progression_dashboard(questions: List[TMMiQuestion], answers: List[AssessmentAnswer]):
    """Render the enhanced TMMi progression dashboard"""
    
    st.header("TMMi Progression Analysis")
    st.markdown("Comprehensive analysis of readiness for the next maturity level")
    
    # Generate progression data
    progression_data = generate_progression_dashboard_data(questions, answers)
    
    # Top-level progression metrics
    render_progression_metrics(progression_data)
    
    # Main dashboard content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        render_next_level_readiness(progression_data)
        render_process_area_progression(progression_data)
        render_gap_analysis_enhanced(progression_data)
    
    with col2:
        render_gating_status(progression_data)
        render_generic_goals_panel(progression_data)
        render_evidence_coverage_enhanced(progression_data)
    
    # Download capabilities
    render_download_section(progression_data)


def render_progression_metrics(progression_data: Dict):
    """Render top-level progression metrics"""
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        current_level = progression_data["current_level"]
        level_names = {1: "Initial", 2: "Managed", 3: "Defined", 4: "Measured", 5: "Optimized"}
        level_name = level_names.get(current_level, "Unknown")
        st.metric(
            "Current Level", 
            f"Level {current_level}: {level_name}",
            help=f"Currently achieved TMMi maturity level"
        )
    
    with col2:
        next_level = progression_data["next_level"]
        if next_level <= 5:
            next_level_name = level_names.get(next_level, "Unknown")
            st.metric(
                "Target Level",
                f"Level {next_level}: {next_level_name}",
                help=f"Next TMMi level to achieve"
            )
        else:
            st.metric("Target Level", "Maximum Achieved", help="Already at highest TMMi level")
    
    with col3:
        readiness = progression_data["conservative_readiness"]
        readiness_color = "normal"
        if readiness >= 75:
            readiness_color = "normal"
        elif readiness >= 50:
            readiness_color = "off"
        else:
            readiness_color = "inverse"
        
        st.metric(
            "Readiness to Next Level",
            f"{readiness:.1f}%",
            delta=f"{readiness - 50:.1f}% from minimum",
            delta_color=readiness_color,
            help="Conservative readiness percentage for next level"
        )
    
    with col4:
        gap_count = progression_data["gap_count"]
        high_priority = len(progression_data["high_priority_gaps"])
        st.metric(
            "Total Gaps",
            gap_count,
            delta=f"{high_priority} high priority",
            delta_color="inverse" if high_priority > 0 else "normal",
            help="Total gaps identified for improvement"
        )
    
    with col5:
        gating_status = progression_data["gating_status"]
        status_color = "normal" if gating_status == "Eligible" else "inverse"
        st.metric(
            "Certification Status",
            gating_status,
            help="Eligibility for formal TMMi certification to next level"
        )


def render_next_level_readiness(progression_data: Dict):
    """Render detailed next level readiness analysis"""
    
    st.markdown("### Next Level Readiness Analysis")
    
    next_level = progression_data["next_level"]
    if next_level > 5:
        st.success("🎉 Congratulations! You have achieved the highest TMMi maturity level.")
        return
    
    target_pas = progression_data["target_process_areas"]
    
    if not target_pas:
        st.info("No process areas found for the target level.")
        return
    
    # Create readiness chart
    pa_names = list(target_pas.keys())
    readiness_values = [target_pas[pa]["attainment_percentage"] for pa in pa_names]
    bands = [target_pas[pa]["band"] for pa in pa_names]
    
    # Color coding for bands
    band_colors = {"F": "#00cc44", "L": "#88cc00", "P": "#ffcc00", "N": "#ff4444"}
    colors = [band_colors.get(band, "#cccccc") for band in bands]
    
    # Create horizontal bar chart
    df = pd.DataFrame({
        "Process Area": pa_names,
        "Readiness %": readiness_values,
        "Band": bands
    })
    
    fig = px.bar(
        df,
        x="Readiness %",
        y="Process Area",
        orientation="h",
        color="Band",
        color_discrete_map=band_colors,
        title=f"Process Area Readiness for Level {next_level}",
        range_color=[0, 100]
    )
    
    fig.update_layout(
        height=max(300, len(pa_names) * 40),
        xaxis=dict(range=[0, 100]),
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Band legend
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("**F (Fully):** 85-100%")
    with col2:
        st.markdown("**L (Largely):** 50-85%")
    with col3:
        st.markdown("**P (Partially):** 15-50%")
    with col4:
        st.markdown("**N (Not):** 0-15%")


def render_process_area_progression(progression_data: Dict):
    """Render process area progression with evidence coverage"""
    
    st.markdown("### Process Area Progression & Evidence")
    
    process_areas = progression_data["process_areas"]
    evidence_coverage = progression_data["evidence_coverage_by_pa"]
    
    if not process_areas:
        st.info("No process area data available.")
        return
    
    # Prepare data for visualization
    pa_data = []
    for pa_name, pa_info in process_areas.items():
        evidence_pct = evidence_coverage.get(pa_name, {}).get("percentage", 0)
        pa_data.append({
            "Process Area": pa_name,
            "Level": pa_info["level"],
            "Attainment %": pa_info["attainment_percentage"],
            "Band": pa_info["band"],
            "Evidence %": evidence_pct,
            "Risk": "High Risk" if pa_info["band"] == "F" and evidence_pct < 50 else "Normal"
        })
    
    df = pd.DataFrame(pa_data)
    
    # Sort by level and attainment
    df = df.sort_values(["Level", "Attainment %"], ascending=[True, False])
    
    # Create scatter plot: Attainment vs Evidence with level and band
    fig = px.scatter(
        df,
        x="Attainment %",
        y="Evidence %",
        color="Band",
        size="Level",
        hover_data=["Process Area", "Risk"],
        title="Process Area Attainment vs Evidence Coverage",
        color_discrete_map={"F": "#00cc44", "L": "#88cc00", "P": "#ffcc00", "N": "#ff4444"}
    )
    
    # Add risk zones
    fig.add_hline(y=50, line_dash="dash", line_color="red", 
                  annotation_text="Evidence Risk Threshold")
    fig.add_vline(x=85, line_dash="dash", line_color="green", 
                  annotation_text="Full Achievement Threshold")
    
    fig.update_layout(
        height=500,
        xaxis=dict(range=[0, 100]),
        yaxis=dict(range=[0, 100])
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # High risk assertions
    high_risk = progression_data["high_risk_assertions"]
    if high_risk:
        st.warning(f"⚠️ **High Risk Assertions:** The following process areas show full achievement but have low evidence coverage: {', '.join(high_risk)}")


def render_gating_status(progression_data: Dict):
    """Render gating status for next level certification"""
    
    st.markdown("### Certification Eligibility")
    
    gating_status = progression_data["gating_status"]
    gating_reason = progression_data["gating_reason"]
    
    if gating_status == "Eligible":
        st.success("✅ **Eligible for Level Certification**")
        st.info("All process areas at the target level meet minimum requirements (≥50% attainment)")
    else:
        st.error("❌ **Not Eligible for Level Certification**")
        st.warning(f"**Reason:** {gating_reason}")
    
    # Requirements checklist
    st.markdown("**Requirements for Next Level:**")
    
    target_pas = progression_data["target_process_areas"]
    if target_pas:
        for pa_name, pa_data in target_pas.items():
            attainment = pa_data["attainment_percentage"]
            band = pa_data["band"]
            
            if attainment >= 50:
                st.success(f"✓ {pa_name}: {attainment:.1f}% ({band})")
            else:
                st.error(f"✗ {pa_name}: {attainment:.1f}% ({band})")
    
    # Generic goals requirement
    generic_goals = progression_data["generic_goals"]
    if generic_goals:
        st.markdown("**Generic Goals Status:**")
        for gg_name, gg_data in generic_goals.items():
            if gg_data["status"] == "Met":
                st.success(f"✓ {gg_name}: Met")
            else:
                st.error(f"✗ {gg_name}: Not Met ({gg_data['attainment_percentage']:.1f}%)")


def render_generic_goals_panel(progression_data: Dict):
    """Render generic goals compliance panel"""
    
    st.markdown("### Generic Goals Compliance")
    
    generic_goals = progression_data["generic_goals"]
    
    if not generic_goals:
        st.info("No generic goals data available.")
        return
    
    # Create generic goals checklist
    for gg_name, gg_data in generic_goals.items():
        with st.expander(f"{gg_name} - {gg_data['status']}", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Attainment", f"{gg_data['attainment_percentage']:.1f}%")
                st.metric("Band", gg_data["band"])
            
            with col2:
                st.metric("Questions", gg_data["question_count"])
                st.metric("Evidence", f"{gg_data['evidence_coverage']:.1f}%")
            
            # Progress bar
            progress = gg_data["attainment_percentage"] / 100
            st.progress(progress)
            
            if gg_data["status"] == "Met":
                st.success(f"✅ {gg_name} requirements satisfied")
            else:
                st.warning(f"⚠️ {gg_name} requires improvement to meet 85% threshold")


def render_evidence_coverage_enhanced(progression_data: Dict):
    """Render enhanced evidence coverage analysis"""
    
    st.markdown("### Evidence Coverage Analysis")
    
    evidence_coverage = progression_data["evidence_coverage"]
    evidence_by_pa = progression_data["evidence_coverage_by_pa"]
    
    # Overall evidence coverage
    overall_pct = evidence_coverage["percentage"]
    st.metric(
        "Overall Evidence Coverage",
        f"{overall_pct:.1f}%",
        help="Percentage of all answers with supporting evidence"
    )
    
    # Evidence coverage by process area
    if evidence_by_pa:
        pa_names = list(evidence_by_pa.keys())
        evidence_values = [evidence_by_pa[pa]["percentage"] for pa in pa_names]
        
        # Create horizontal bar chart
        df = pd.DataFrame({
            "Process Area": pa_names,
            "Evidence %": evidence_values
        })
        
        fig = px.bar(
            df,
            x="Evidence %",
            y="Process Area",
            orientation="h",
            title="Evidence Coverage by Process Area",
            color="Evidence %",
            color_continuous_scale="RdYlGn",
            range_color=[0, 100]
        )
        
        fig.update_layout(
            height=max(300, len(pa_names) * 30),
            xaxis=dict(range=[0, 100]),
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Evidence quality indicators
    st.markdown("**Evidence Quality Indicators:**")
    
    if overall_pct >= 80:
        st.success("✅ Excellent evidence coverage")
    elif overall_pct >= 60:
        st.info("ℹ️ Good evidence coverage")
    elif overall_pct >= 40:
        st.warning("⚠️ Moderate evidence coverage - consider adding more evidence")
    else:
        st.error("❌ Low evidence coverage - high risk of audit findings")


def render_gap_analysis_enhanced(progression_data: Dict):
    """Render enhanced gap analysis with SP/SG mapping"""
    
    st.markdown("### Enhanced Gap Analysis")
    
    gaps = progression_data["gaps"]
    
    if not gaps:
        st.success("🎉 No gaps identified! All requirements are met.")
        return
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        priority_filter = st.selectbox("Priority", options=["All", "High", "Medium", "Low"], index=0)
    
    with col2:
        level_filter = st.selectbox("Level", options=["All"] + [f"Level {i}" for i in range(2, 6)], index=0)
    
    with col3:
        band_filter = st.selectbox("Band", options=["All", "N", "P", "L", "F"], index=0)
    
    # Apply filters
    filtered_gaps = gaps.copy()
    
    if priority_filter != "All":
        filtered_gaps = [g for g in filtered_gaps if g["importance"] == priority_filter]
    
    if level_filter != "All":
        level_num = int(level_filter.split()[1])
        filtered_gaps = [g for g in filtered_gaps if g["level"] == level_num]
    
    if band_filter != "All":
        filtered_gaps = [g for g in filtered_gaps if g["sp_band"] == band_filter]
    
    st.markdown(f"**Found {len(filtered_gaps)} gap(s) requiring attention:**")
    
    # Display gaps in expandable sections
    for i, gap in enumerate(filtered_gaps, 1):
        with st.expander(f"Gap {i}: {gap['process_area']} - {gap['specific_practice'] or 'General'}", expanded=False):
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Question:** {gap['question']}")
                st.markdown(f"**Current Answer:** {gap['current_answer']}")
                
                if gap["specific_goal"]:
                    st.markdown(f"**Specific Goal:** {gap['specific_goal']}")
                
                if gap["specific_practice"]:
                    st.markdown(f"**Specific Practice:** {gap['specific_practice']}")
                
                if gap["comment"]:
                    st.markdown(f"**Comment:** {gap['comment']}")
                
                if gap["evidence_url"]:
                    st.markdown(f"**Evidence:** [Link]({gap['evidence_url']})")
            
            with col2:
                priority_class = f"status-{gap['importance'].lower()}"
                st.markdown(
                    f'<span class="{priority_class}">Priority: {gap["importance"]}</span>', 
                    unsafe_allow_html=True
                )
                
                st.markdown(f"**Level:** {gap['level']}")
                st.markdown(f"**SP Band:** {gap['sp_band']} ({gap['sp_attainment']:.1f}%)")
                
                if gap["sg_attainment"] > 0:
                    st.markdown(f"**SG Band:** {gap['sg_band']} ({gap['sg_attainment']:.1f}%)")
            
            # Action recommendation
            st.markdown("**Action to Close Gap:**")
            st.info(gap["action_to_close"])
            
            if gap["reference_url"]:
                st.markdown(f"[Reference Documentation]({gap['reference_url']})")


def render_download_section(progression_data: Dict):
    """Render download section for gap analysis and progression data"""
    
    st.markdown("### Download & Export")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gap analysis CSV
        if progression_data["gaps"]:
            gaps_df = pd.DataFrame(progression_data["gaps"])
            
            # Select columns for export
            export_columns = [
                "process_area", "specific_goal", "specific_practice", "question", 
                "current_answer", "importance", "level", "sp_attainment", "sp_band",
                "action_to_close", "evidence_url"
            ]
            
            # Filter to available columns
            available_columns = [col for col in export_columns if col in gaps_df.columns]
            export_df = gaps_df[available_columns]
            
            csv_data = export_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Gap Analysis (CSV)",
                data=csv_data,
                file_name=f"tmmi_gap_analysis_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        # Process area summary CSV
        if progression_data["process_areas"]:
            pa_data = []
            for pa_name, pa_info in progression_data["process_areas"].items():
                evidence_pct = progression_data["evidence_coverage_by_pa"].get(pa_name, {}).get("percentage", 0)
                pa_data.append({
                    "Process Area": pa_name,
                    "Level": pa_info["level"],
                    "Attainment %": pa_info["attainment_percentage"],
                    "Band": pa_info["band"],
                    "Evidence %": evidence_pct,
                    "Specific Goals": pa_info.get("sg_count", 0)
                })
            
            pa_df = pd.DataFrame(pa_data)
            pa_csv = pa_df.to_csv(index=False)
            
            st.download_button(
                label="📥 Download Process Area Summary (CSV)",
                data=pa_csv,
                file_name=f"tmmi_process_areas_{pd.Timestamp.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    # Summary report
    st.markdown("**Summary Report:**")
    
    summary_text = f"""
    TMMi Progression Analysis Summary
    
    Current Level: {progression_data['current_level']}
    Target Level: {progression_data['next_level']}
    Readiness: {progression_data['conservative_readiness']:.1f}%
    Gating Status: {progression_data['gating_status']}
    
    Total Gaps: {progression_data['gap_count']}
    High Priority Gaps: {len(progression_data['high_priority_gaps'])}
    
    Evidence Coverage: {progression_data['evidence_coverage']['percentage']:.1f}%
    
    Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    st.text_area("Summary Report", summary_text, height=200)
    
    st.download_button(
        label="📥 Download Summary Report (TXT)",
        data=summary_text,
        file_name=f"tmmi_progression_summary_{pd.Timestamp.now().strftime('%Y%m%d')}.txt",
        mime="text/plain"
    )
