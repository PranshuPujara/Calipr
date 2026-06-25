import sys
import re

def main():
    with open("hf_space_clone/app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Fix 1 & 10: Banner clarification
    old_banner = """<div style="background: rgba(14, 161, 88, 0.08); border: 1px solid rgba(14, 161, 88, 0.25); border-radius: 12px; color: #0c7540; padding: 15px; margin-bottom: 24px; font-weight:600; font-family:Inter,sans-serif;">
        ✅ Ranking Complete — {st.session_state.run_runtime}s · Evaluated {st.session_state.total_candidates_evaluated:,} candidates
    </div>"""
    new_banner = """<div style="background: rgba(14, 161, 88, 0.08); border: 1px solid rgba(14, 161, 88, 0.25); border-radius: 12px; color: #0c7540; padding: 15px; margin-bottom: 12px; font-weight:600; font-family:Inter,sans-serif;">
        ✅ Ranking Complete — {st.session_state.run_runtime}s · Evaluated {st.session_state.total_candidates_evaluated:,} candidates
    </div>
    <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.25); border-radius: 12px; color: #b45309; padding: 12px 15px; margin-bottom: 24px; font-weight:500; font-family:Inter,sans-serif; font-size: 13px;">
        ⚠️ <strong>Note:</strong> Sample pool contains general candidates. Run with full 106K dataset for accurate ML engineer ranking.
    </div>"""
    content = content.replace(old_banner, new_banner)

    # Fix 2: Dropdown / Left List mismatch.
    # The left column list uses row["title"].
    # Let's ensure candidate_row takes title and detail panel takes title too. (Already does).
    # Wait, in parse_resume_offline:
    old_titles = 'titles = ["backend engineer", "frontend engineer", "fullstack engineer", "full stack engineer",\n              "data scientist", "data engineer", "machine learning engineer", "devops engineer",\n              "software engineer", "product manager", "ui/ux designer"]'
    new_titles = 'titles = ["backend engineer", "frontend engineer", "fullstack engineer", "full stack engineer",\n              "data scientist", "data engineer", "machine learning engineer", "devops engineer",\n              "software engineer", "product manager", "project manager", "ui/ux designer"]'
    content = content.replace(old_titles, new_titles)

    # Fix 3: Radar Chart margins
    old_radar = "polar=dict(\n            bgcolor='rgba(0,0,0,0)',"
    new_radar = "margin=dict(l=60, r=60, t=60, b=60),\n        polar=dict(\n            bgcolor='rgba(0,0,0,0)',"
    content = content.replace(old_radar, new_radar)

    # Fix 4: Phase Card padding
    old_phase = """/* PIPELINE PHASE CARD */
.phase-card {
    background: rgba(255, 255, 255, 0.75) !important;
    border: 1px solid #e4e2e2 !important;
    border-radius: 12px !important;
    padding: 24px !important;"""
    new_phase = """/* PIPELINE PHASE CARD */
.phase-card {
    background: rgba(255, 255, 255, 0.75) !important;
    border: 1px solid #e4e2e2 !important;
    border-radius: 12px !important;
    padding: 16px !important;"""
    content = content.replace(old_phase, new_phase)

    # Fix 5: Fourth stat card cutoff & Fix 10: Hero section stats size
    old_stat = """/* STAT CARD */
.stat-card {
    background: #FFFFFF !important;
    border: 1px solid #e4e2e2 !important;
    border-radius: 12px !important;
    padding: 20px !important;
    text-align: center;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
}
.stat-number {
    font-size: 28px !important;
    font-weight: 800 !important;"""
    new_stat = """/* STAT CARD */
.stat-card {
    background: #FFFFFF !important;
    border: 1px solid #e4e2e2 !important;
    border-radius: 12px !important;
    padding: 16px !important;
    text-align: center;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
}
.stat-number {
    font-size: 32px !important;
    font-weight: 800 !important;"""
    content = content.replace(old_stat, new_stat)

    # Fix 6: Move CSV Button to top
    csv_btn_code = """
        if st.session_state.scored_candidates:
            # Generate CSV for download
            import pandas as pd
            df = pd.DataFrame([{
                'Rank': i+1,
                'Candidate ID': c['candidate_id'],
                'Name': c['name'],
                'Title': c['title'],
                'Final Score': c['score'],
                'Semantic Fit': c['s1_sem'],
                'Skills Match': c['s2_skl'],
                'Career': c['s3_car'],
                'Behavioral': c['s4_beh'],
                'Domain': c['s5_dom']
            } for i, c in enumerate(st.session_state.scored_candidates)])
            csv_data = df.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="Download Top 100 Shortlist CSV",
                data=csv_data,
                file_name="calipr_submission.csv",
                mime="text/csv",
                use_container_width=True
            )"""
    content = content.replace(csv_btn_code, "")
    
    csv_injection = """
    left_col, right_col = st.columns([1, 1.4])
    """
    new_csv_injection = csv_btn_code + "\n" + csv_injection
    content = content.replace(csv_injection, new_csv_injection)

    # Fix 7: Score bar colors
    old_score_bar = """def score_bar(label: str, value: float):
    color_map = {
        'high': '#0ea158',   # green
        'mid':  '#cf8d13',   # amber
        'low':  '#4A90FF',   # coral
    }
    fill_color = color_map['high'] if value >= 0.75 else color_map['mid'] if value >= 0.50 else color_map['low']"""
    new_score_bar = """def score_bar(label: str, value: float):
    if "Semantic" in label:
        fill_color = "#4A90FF"
    elif "Skills" in label:
        fill_color = "#00D4AA"
    elif "Career" in label:
        fill_color = "#7C6EFF"
    elif "Behavioral" in label:
        fill_color = "#F59E0B"
    elif "Domain" in label:
        fill_color = "#EF4444"
    else:
        fill_color = "#4A90FF" """
    content = content.replace(old_score_bar, new_score_bar)

    # Rank Badge Color (Amber for 9-15) -> Black
    old_rank_class = """    rank_class = "top3" if rank <= 3 else "" """
    new_rank_class = """    rank_class = "top3" if rank <= 3 else "top10" if rank <= 10 else "top_rest" """
    content = content.replace(old_rank_class, new_rank_class)

    old_badge_css = """.rank-badge {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background: #f7f3f0;
    color: #a69888;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 13px;
    font-family: 'Fragment Mono', monospace;
}
.rank-badge.top3 {
    background: #1a1615;
    color: #FFFFFF;
}"""
    new_badge_css = """.rank-badge {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    background: #f7f3f0;
    color: #a69888;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 13px;
    font-family: 'Fragment Mono', monospace;
}
.rank-badge.top3 {
    background: linear-gradient(135deg, #FFD700, #FDB931);
    color: #1a1615;
}
.rank-badge.top10 {
    background: #1a1615;
    color: #FFFFFF;
}
.rank-badge.top_rest {
    background: #e4e2e2;
    color: #757170;
}"""
    content = content.replace(old_badge_css, new_badge_css)

    # Fix 8 & 9: Work Experience Expander & timeline overflow
    old_timeline_start = """        st.markdown('<div class="section-label">Work Experience Timeline</div>', unsafe_allow_html=True)
        timeline_html = "<div style='position: relative; padding-left: 20px; border-left: 2px solid #e4e2e2; margin-top: 15px; margin-left: 10px;'>"
        for job in selected_cand['_profile'].get('career_history', []):"""
    new_timeline_start = """        st.markdown('<div class="section-label">Work Experience Timeline</div>', unsafe_allow_html=True)
        timeline_html = "<div style='position: relative; padding-left: 20px; border-left: 2px solid #e4e2e2; margin-top: 15px; margin-left: 10px; overflow: hidden; word-wrap: break-word; max-width: 100%;'>"
        for job in selected_cand['_profile'].get('career_history', []):"""
    content = content.replace(old_timeline_start, new_timeline_start)

    old_timeline_end = """        timeline_html += "</div>"
        st.markdown(timeline_html, unsafe_allow_html=True)"""
    new_timeline_end = """        timeline_html += "</div>"
        with st.expander("View Work History"):
            st.markdown(timeline_html, unsafe_allow_html=True)"""
    content = content.replace(old_timeline_end, new_timeline_end)

    with open("hf_space_clone/app.py", "w", encoding="utf-8") as f:
        f.write(content)
        
    print("Replacements done in hf_space_clone/app.py")

if __name__ == "__main__":
    main()
