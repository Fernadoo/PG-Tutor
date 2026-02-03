"""
Progress Chart Component

Visualizes Bayesian belief updates and learning progress.
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from scipy import stats


def render_progress_chart():
    """Render progress charts showing Bayesian belief evolution."""
    if 'belief_history' not in st.session_state or not st.session_state.belief_history:
        st.info("Complete questions to see your progress!")
        return
    
    teacher = st.session_state.get('teacher')
    if not teacher:
        return
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Lambda Estimate Over Time',
            'Current Posterior Distribution',
            'Accuracy by Topic',
            'Learning Trajectory'
        ),
        specs=[
            [{"type": "scatter"}, {"type": "histogram"}],
            [{"type": "bar"}, {"type": "scatter"}]
        ]
    )
    
    # Chart 1: Lambda evolution over time
    belief_history = st.session_state.belief_history
    x_vals = list(range(len(belief_history)))
    lambda_vals = [b['belief']['expected_lambda'] for b in belief_history]
    
    fig.add_trace(
        go.Scatter(
            x=x_vals,
            y=lambda_vals,
            mode='lines+markers',
            name='Knowledge Level (λ)',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8)
        ),
        row=1, col=1
    )
    
    # Add reference lines
    fig.add_hline(y=1.0, line_dash="dash", line_color="green", opacity=0.5, row=1, col=1)
    fig.add_hline(y=2.5, line_dash="dash", line_color="orange", opacity=0.5, row=1, col=1)
    fig.add_hline(y=4.0, line_dash="dash", line_color="red", opacity=0.5, row=1, col=1)
    
    # Chart 2: Posterior distribution
    bayesian_model = teacher.bayesian_model
    posterior_samples = bayesian_model.sample_lambda(10000)
    
    fig.add_trace(
        go.Histogram(
            x=posterior_samples,
            nbinsx=50,
            name='Posterior',
            marker_color='#2ca02c',
            opacity=0.7
        ),
        row=1, col=2
    )
    
    # Add vertical line for expected value
    expected_lambda = bayesian_model.get_expected_lambda()
    fig.add_vline(
        x=expected_lambda,
        line_dash="dash",
        line_color="red",
        annotation_text=f"E[λ] = {expected_lambda:.2f}",
        row=1, col=2
    )
    
    # Chart 3: Accuracy by topic
    topic_history = st.session_state.get('topic_history', [])
    if topic_history:
        topics = list(set([t['topic'] for t in topic_history]))
        correct_counts = []
        total_counts = []
        
        for topic_name in topics:
            topic_attempts = [t for t in topic_history if t['topic'] == topic_name]
            correct = sum(1 for t in topic_attempts if t['correct'])
            total = len(topic_attempts)
            correct_counts.append(correct)
            total_counts.append(total)
        
        accuracy_pct = [c/t*100 if t > 0 else 0 for c, t in zip(correct_counts, total_counts)]
        
        fig.add_trace(
            go.Bar(
                x=topics,
                y=accuracy_pct,
                name='Accuracy %',
                marker_color='#ff7f0e',
                text=[f"{c}/{t}" for c, t in zip(correct_counts, total_counts)],
                textposition='outside'
            ),
            row=2, col=1
        )
    
    # Chart 4: Learning trajectory (cumulative accuracy)
    if topic_history:
        cumulative_correct = []
        cumulative_total = []
        correct_so_far = 0
        
        for i, attempt in enumerate(topic_history):
            if attempt['correct']:
                correct_so_far += 1
            cumulative_correct.append(correct_so_far)
            cumulative_total.append(i + 1)
        
        cumulative_accuracy = [c/t*100 for c, t in zip(cumulative_correct, cumulative_total)]
        
        fig.add_trace(
            go.Scatter(
                x=list(range(len(cumulative_accuracy))),
                y=cumulative_accuracy,
                mode='lines',
                name='Cumulative Accuracy %',
                line=dict(color='#9467bd', width=2),
                fill='tozeroy'
            ),
            row=2, col=2
        )
    
    # Update layout
    fig.update_layout(
        height=700,
        showlegend=False,
        title_text="Learning Analytics Dashboard"
    )
    
    fig.update_xaxes(title_text="Question Number", row=1, col=1)
    fig.update_yaxes(title_text="Knowledge Level (λ)", row=1, col=1)
    fig.update_xaxes(title_text="λ Value", row=1, col=2)
    fig.update_yaxes(title_text="Density", row=1, col=2)
    fig.update_xaxes(title_text="Topic", tickangle=45, row=2, col=1)
    fig.update_yaxes(title_text="Accuracy (%)", row=2, col=1)
    fig.update_xaxes(title_text="Question Number", row=2, col=2)
    fig.update_yaxes(title_text="Cumulative Accuracy (%)", row=2, col=2)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show current belief stats
    current_belief = teacher.get_current_belief()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current λ", f"{current_belief['expected_lambda']:.2f}")
    with col2:
        st.metric("α (Shape)", f"{current_belief['alpha']:.2f}")
    with col3:
        st.metric("β (Rate)", f"{current_belief['beta']:.2f}")
    with col4:
        recommendation = teacher.get_recommendation()
        # Truncate long recommendations
        short_rec = recommendation[:50] + "..." if len(recommendation) > 50 else recommendation
        st.metric("Recommendation", short_rec)
