import sys

def main():
    with open("hf_space_clone/app.py", "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Modify candidate_row to add data-cand-idx
    old_def = """def candidate_row(rank: int, name: str, title: str, 
                  years: float, score: float, is_selected: bool = False):"""
    new_def = """def candidate_row(rank: int, name: str, title: str, 
                  years: float, score: float, is_selected: bool = False, cand_idx: int = 0):"""
    
    old_div = 'return f"""<div class="candidate-card {selected_class}">'
    new_div = 'return f"""<div class="candidate-card {selected_class}" data-cand-idx="{cand_idx}">'
    
    content = content.replace(old_def, new_def)
    content = content.replace(old_div, new_div)

    # 2. Modify the loop that calls candidate_row
    old_loop_call = 'cards_html += candidate_row(rank, row["name"], row["title"], row["experience"], row["score"], is_selected=is_sel)'
    new_loop_call = 'cards_html += candidate_row(rank, row["name"], row["title"], row["experience"], row["score"], is_selected=is_sel, cand_idx=rank-1)'
    
    content = content.replace(old_loop_call, new_loop_call)

    # 3. Replace st.selectbox with st.radio and hide it
    old_selectbox = """        # Interactive Selectbox
        selected_idx = st.selectbox(
            "Select Candidate to Inspect",
            options=range(len(scored_list)),
            format_func=lambda i: f"#{i+1} - {scored_list[i]['name']} ({scored_list[i]['score']:.3f})",
            label_visibility="collapsed"
        )"""
    new_radio = """        # Hidden Radio for Click Tunneling
        st.markdown('<div id="hide_next_radio"></div>', unsafe_allow_html=True)
        selected_idx = st.radio(
            "Select Candidate to Inspect",
            options=range(len(scored_list)),
            format_func=lambda i: f"#{i+1} - {scored_list[i]['name']}",
            label_visibility="collapsed"
        )
        st.markdown(\"\"\"<style>
        .element-container:has(#hide_next_radio) + .element-container {
            display: none !important;
        }
        </style>\"\"\", unsafe_allow_html=True)"""
    content = content.replace(old_selectbox, new_radio)

    # 4. Inject JS code immediately after rendering the cards
    old_render = """        st.markdown(cards_html, unsafe_allow_html=True)"""
    new_render = """        st.markdown(cards_html, unsafe_allow_html=True)
        
        import streamlit.components.v1 as components
        js_code = \"\"\"
        <script>
        const checkExist = setInterval(function() {
            const doc = window.parent.document;
            const marker = doc.querySelector('#hide_next_radio');
            const cards = doc.querySelectorAll('.candidate-card');
            
            if (marker && cards.length > 0) {
                clearInterval(checkExist);
                
                const radioContainer = marker.closest('.element-container').nextElementSibling;
                if (!radioContainer) return;
                
                const radios = radioContainer.querySelectorAll('input[type="radio"]');
                
                cards.forEach(card => {
                    // Prevent duplicate bindings
                    if (card.getAttribute('data-bound')) return;
                    card.setAttribute('data-bound', 'true');
                    
                    card.onclick = function() {
                        const idx = parseInt(this.getAttribute('data-cand-idx'));
                        if (radios.length > idx) {
                            radios[idx].click();
                        }
                    };
                });
            }
        }, 300);
        setTimeout(() => clearInterval(checkExist), 10000);
        </script>
        \"\"\"
        components.html(js_code, height=0, width=0)"""
    
    content = content.replace(old_render, new_render)

    with open("hf_space_clone/app.py", "w", encoding="utf-8") as f:
        f.write(content)
        
    print("Replacements done in hf_space_clone/app.py")

if __name__ == "__main__":
    main()
