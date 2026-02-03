"""
Knowledge Graph Visualization Component

Visualizes the hierarchical topic structure.
"""

import streamlit as st
import networkx as nx
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def render_knowledge_graph():
    """Render the knowledge graph visualization."""
    if 'knowledge_graph' not in st.session_state:
        st.info("Start a session to view the knowledge graph!")
        return
    
    knowledge_graph = st.session_state.knowledge_graph
    
    # Create network graph
    G = nx.DiGraph()
    
    # Add nodes and edges
    for level in knowledge_graph.get_all_levels():
        topics = knowledge_graph.get_topics_at_level(level)
        for topic in topics:
            G.add_node(
                topic.name,
                level=topic.level,
                difficulty=topic.difficulty,
                color=get_level_color(topic.level)
            )
            
            # Add prerequisite edges
            for prereq in topic.prerequisites:
                G.add_edge(prereq, topic.name)
    
    # Create layout
    pos = nx.spring_layout(G, k=2, iterations=50)
    
    # Create edges
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    # Create nodes
    node_x = []
    node_y = []
    node_colors = []
    node_sizes = []
    node_labels = []
    node_hover = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        node_data = G.nodes[node]
        node_colors.append(node_data['color'])
        node_sizes.append(20 + node_data['difficulty'] * 30)
        node_labels.append(node)
        
        # Hover text
        hover_text = f"<b>{node}</b><br>"
        hover_text += f"Level: {node_data['level']}<br>"
        hover_text += f"Difficulty: {node_data['difficulty']:.2f}"
        node_hover.append(hover_text)
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        hovertext=node_hover,
        text=node_labels,
        textposition='top center',
        marker=dict(
            color=node_colors,
            size=node_sizes,
            line=dict(width=2, color='white')
        ),
        textfont=dict(size=10)
    )
    
    # Create figure
    fig = go.Figure(
        data=[edge_trace, node_trace]
    )
    
    fig.update_layout(
        title=dict(text='Knowledge Graph Structure', font=dict(size=16)),
        showlegend=False,
        hovermode='closest',
        margin=dict(b=20, l=5, r=5, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=600
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show legend
    st.markdown("### 📊 Legend")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown("🟢 **Level 0**\nBasic Concepts")
    with col2:
        st.markdown("🔵 **Level 1**\nElementary")
    with col3:
        st.markdown("🟡 **Level 2**\nIntermediate")
    with col4:
        st.markdown("🟠 **Level 3**\nAdvanced")
    with col5:
        st.markdown("🔴 **Level 4**\nExpert")
    
    # Show topic details
    st.markdown("---")
    st.markdown("### 📚 Topic Details")
    
    all_topics = []
    for level in sorted(knowledge_graph.get_all_levels()):
        topics = knowledge_graph.get_topics_at_level(level)
        for topic in topics:
            all_topics.append(topic)
    
    topic_names = [t.name for t in all_topics]
    selected_topic = st.selectbox("Select a topic to view details:", topic_names)
    
    if selected_topic:
        topic = knowledge_graph.get_topic_by_name(selected_topic)
        if topic:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Name:** {topic.name}")
                st.markdown(f"**Level:** {topic.level}")
                st.markdown(f"**Difficulty:** {topic.difficulty:.2f}/1.0")
            with col2:
                st.markdown("**Prerequisites:**")
                if topic.prerequisites:
                    for prereq in topic.prerequisites:
                        st.markdown(f"- {prereq}")
                else:
                    st.markdown("None (introductory topic)")
            
            st.markdown("**Content:**")
            st.info(topic.content)


def get_level_color(level):
    """Get color for a difficulty level."""
    colors = {
        0: '#2ecc71',  # Green - Basic
        1: '#3498db',  # Blue - Elementary
        2: '#f1c40f',  # Yellow - Intermediate
        3: '#e67e22',  # Orange - Advanced
        4: '#e74c3c',  # Red - Expert
    }
    return colors.get(level, '#95a5a6')
