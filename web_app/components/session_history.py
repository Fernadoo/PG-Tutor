"""
Session History Component

Displays session history and analytics.
"""

import streamlit as st
import plotly.graph_objects as go
import json
from collections import defaultdict


def render_session_history():
    """Render the session history view."""
    if 'topic_history' not in st.session_state or not st.session_state.topic_history:
        st.info("No session history yet. Complete some questions to see your progress!")
        return
    
    topic_history = st.session_state.topic_history
    belief_history = st.session_state.get('belief_history', [])
    
    st.markdown("### 📜 Session History")
    
    # Create table data manually (without pandas)
    table_data = []
    for i, record in enumerate(topic_history, 1):
        status = '✓ Correct' if record['correct'] else '✗ Incorrect'
        table_data.append({
            'question_number': i,
            'topic': record['topic'],
            'level': record['level'],
            'status': status
        })
    
    # Display table
    st.table(table_data)
    
    # Statistics
    st.markdown("---")
    st.markdown("### 📊 Session Statistics")
    
    total = len(topic_history)
    correct = sum(1 for t in topic_history if t['correct'])
    accuracy = (correct / total * 100) if total > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Questions", total)
    with col2:
        st.metric("Correct Answers", correct)
    with col3:
        st.metric("Incorrect Answers", total - correct)
    with col4:
        st.metric("Accuracy", f"{accuracy:.1f}%")
    
    # Performance by level (without pandas)
    st.markdown("---")
    st.markdown("### 📈 Performance by Level")
    
    # Group by level manually
    level_stats = defaultdict(lambda: {'total': 0, 'correct': 0})
    for record in topic_history:
        level = record['level']
        level_stats[level]['total'] += 1
        if record['correct']:
            level_stats[level]['correct'] += 1
    
    # Convert to sorted lists
    levels = sorted(level_stats.keys())
    totals = [level_stats[l]['total'] for l in levels]
    corrects = [level_stats[l]['correct'] for l in levels]
    accuracies = [(level_stats[l]['correct'] / level_stats[l]['total'] * 100) if level_stats[l]['total'] > 0 else 0 for l in levels]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Total Questions',
        x=levels,
        y=totals,
        marker_color='#3498db',
        text=totals,
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        name='Correct',
        x=levels,
        y=corrects,
        marker_color='#2ecc71',
        text=corrects,
        textposition='outside'
    ))
    
    fig.update_layout(
        title='Questions and Correct Answers by Level',
        barmode='group',
        xaxis_title='Level',
        yaxis_title='Count',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Accuracy by level line chart
    fig2 = go.Figure()
    
    fig2.add_trace(go.Scatter(
        x=levels,
        y=accuracies,
        mode='lines+markers',
        name='Accuracy %',
        line=dict(color='#e74c3c', width=3),
        marker=dict(size=10)
    ))
    
    fig2.update_layout(
        title='Accuracy Percentage by Level',
        xaxis_title='Level',
        yaxis_title='Accuracy (%)',
        yaxis_range=[0, 100],
        height=400
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Export option
    st.markdown("---")
    st.markdown("### 💾 Export Data")
    
    if st.button("📥 Export Session Data"):
        # Prepare export data
        export_data = {
            'sessions': st.session_state.session_data.get('sessions', []),
            'topic_history': topic_history,
            'belief_history': [
                {
                    'topic': b['topic'],
                    'correct': b['correct'],
                    'lambda': b['belief']['expected_lambda'],
                    'alpha': b['belief']['alpha'],
                    'beta': b['belief']['beta']
                } for b in belief_history
            ]
        }
        
        # Convert to JSON using standard library
        json_str = json.dumps(export_data, indent=2, default=str)
        
        st.download_button(
            label="Download JSON",
            data=json_str,
            file_name=f"session_{st.session_state.session_data.get('timestamp', 'export')}.json",
            mime="application/json"
        )
