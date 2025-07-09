"""
Streamlit Frontend for GeoSpatial AI Assistant
"""
import streamlit as st
import requests
import json
import time
from typing import Dict, List
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="GeoSpatial AI Assistant",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if 'queries' not in st.session_state:
    st.session_state.queries = []
if 'current_execution' not in st.session_state:
    st.session_state.current_execution = None


def main():
    """Main application"""
    st.title("🌍 GeoSpatial AI Assistant")
    st.markdown("Convert natural language queries into GIS workflows and execute them automatically.")

    # Sidebar
    with st.sidebar:
        st.header("🛠️ Tools & Settings")

        # Model selection
        model_option = st.selectbox(
            "AI Model",
            ["Mistral-7B-Instruct", "LLaMA-3-8B", "Phi-2"],
            index=0
        )

        # Data sources
        st.subheader("📊 Data Sources")
        use_osm = st.checkbox("OpenStreetMap", value=True)
        use_bhoonidhi = st.checkbox("Bhoonidhi (Indian Govt)", value=True)
        use_stac = st.checkbox("STAC Satellite APIs", value=False)

        # GIS tools
        st.subheader("🗺️ GIS Tools")
        use_qgis = st.checkbox("QGIS", value=True)
        use_grass = st.checkbox("GRASS GIS", value=False)
        use_postgis = st.checkbox("PostGIS", value=True)

        st.divider()

        # Query history
        st.subheader("📝 Recent Queries")
        for i, query in enumerate(st.session_state.queries[-5:]):
            if st.button(f"Query {i + 1}: {query[:30]}...", key=f"history_{i}"):
                st.session_state.current_query = query

    # Main content area
    col1, col2 = st.columns([1, 1])

    with col1:
        st.header("💬 Natural Language Query")

        # Query input
        query_input = st.text_area(
            "Enter your GIS query in plain English:",
            placeholder="e.g., Find all schools within 1km of hospitals in Mumbai",
            height=100,
            value=st.session_state.get('current_query', '')
        )

        # Location context
        location_input = st.text_input(
            "Location (optional):",
            placeholder="e.g., Mumbai, Delhi, India"
        )

        # Action buttons
        col_btn1, col_btn2, col_btn3 = st.columns(3)

        with col_btn1:
            process_btn = st.button("🧠 Process Query", type="primary")

        with col_btn2:
            execute_btn = st.button("⚡ Execute Workflow", disabled=True)

        with col_btn3:
            st.button("📊 View Results")

        # Process query
        if process_btn and query_input:
            with st.spinner("Processing query with AI..."):
                response = process_query(query_input, location_input)
                if response:
                    st.session_state.current_response = response
                    st.session_state.queries.append(query_input)
                    st.success("Query processed successfully!")
                    st.rerun()

        # Display processed query
        if 'current_response' in st.session_state:
            st.subheader("🔍 Query Analysis")

            response = st.session_state.current_response

            # Parsed query details
            with st.expander("📋 Parsed Query Components", expanded=True):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write("**Target Objects:**")
                    st.write(response['parsed_query'].get('target_objects', []))
                    st.write("**Spatial Operation:**")
                    st.write(response['parsed_query'].get('spatial_operation', 'N/A'))

                with col_b:
                    st.write("**Location:**")
                    st.write(response['parsed_query'].get('location', 'N/A'))
                    st.write("**Analysis Type:**")
                    st.write(response['parsed_query'].get('analysis_type', 'N/A'))

    with col2:
        st.header("🔧 Generated Workflow")

        if 'current_response' in st.session_state:
            response = st.session_state.current_response
            workflow = response['workflow']

            # Workflow overview
            col_overview1, col_overview2, col_overview3 = st.columns(3)

            with col_overview1:
                st.metric("Steps", len(workflow.get('steps', [])))

            with col_overview2:
                st.metric("Tools", len(workflow.get('tools', [])))

            with col_overview3:
                st.metric("Est. Time", workflow.get('estimated_time', 'N/A'))

            # Workflow steps
            st.subheader("📝 Execution Steps")

            for step in workflow.get('steps', []):
                with st.expander(f"Step {step['step']}: {step['action']}", expanded=False):
                    col_step1, col_step2 = st.columns(2)

                    with col_step1:
                        st.write(f"**Tool:** {step['tool']}")
                        st.write(f"**Action:** {step['action']}")

                    with col_step2:
                        st.write("**Parameters:**")
                        st.json(step.get('parameters', {}))

            # Execute workflow
            if st.button("🚀 Execute Complete Workflow", type="primary"):
                with st.spinner("Executing GIS workflow..."):
                    execution_response = execute_workflow(response['query_id'], workflow)
                    if execution_response:
                        st.session_state.current_execution = execution_response
                        st.success("Workflow execution started!")
                        st.rerun()

        else:
            st.info("Enter a query in the left panel to generate a workflow.")

    # Execution monitoring
    if 'current_execution' in st.session_state and st.session_state.current_execution:
        st.header("⚙️ Execution Monitor")

        execution_id = st.session_state.current_execution['execution_id']

        # Auto-refresh execution status
        status_placeholder = st.empty()
        progress_placeholder = st.empty()

        with status_placeholder.container():
            status = get_execution_status(execution_id)
            if status:
                col_status1, col_status2 = st.columns(2)

                with col_status1:
                    st.write(f"**Status:** {status['status'].title()}")

                with col_status2:
                    if 'progress' in status:
                        progress_placeholder.progress(status['progress'] / 100)

                # Show results if completed
                if status['status'] == 'completed' and 'results' in status:
                    show_results(status['results'])

                # Auto-refresh if still executing
                if status['status'] == 'executing':
                    time.sleep(2)
                    st.rerun()

    # Map visualization area
    st.header("🗺️ Interactive Map")

    # Create default map
    m = folium.Map(
        location=[20.5937, 78.9629],  # Center of India
        zoom_start=5,
        tiles="OpenStreetMap"
    )

    # Add sample markers (replace with actual results)
    if 'current_execution' in st.session_state:
        # Add result markers to map
        sample_locations = [
            [19.0760, 72.8777, "Mumbai School"],
            [19.0896, 72.8656, "Mumbai Hospital"],
            [28.6139, 77.2090, "Delhi School"]
        ]

        for lat, lon, name in sample_locations:
            folium.Marker([lat, lon], popup=name).add_to(m)

    # Display map
    map_data = st_folium(m, width=700, height=400)


def process_query(query: str, location: str = None) -> Dict:
    """Process query via API"""
    try:
        payload = {
            "query": query,
            "location": location,
            "execute_immediately": False
        }

        response = requests.post(f"{API_BASE_URL}/api/query", json=payload)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None

    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to API. Please ensure the backend is running.")
        return None
    except Exception as e:
        st.error(f"Error processing query: {str(e)}")
        return None


def execute_workflow(query_id: str, workflow: Dict) -> Dict:
    """Execute workflow via API"""
    try:
        payload = {
            "query_id": query_id,
            "workflow": workflow
        }

        response = requests.post(f"{API_BASE_URL}/api/execute", json=payload)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Execution Error: {response.status_code}")
            return None

    except Exception as e:
        st.error(f"Error executing workflow: {str(e)}")
        return None


def get_execution_status(execution_id: str) -> Dict:
    """Get execution status via API"""
    try:
        response = requests.get(f"{API_BASE_URL}/api/status/{execution_id}")

        if response.status_code == 200:
            return response.json()
        else:
            return None

    except Exception as e:
        st.error(f"Error getting status: {str(e)}")
        return None


def show_results(results: Dict):
    """Display execution results"""
    st.subheader("📊 Execution Results")

    # Summary metrics
    if 'summary' in results:
        summary = results['summary']
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Features Found", summary.get('total_features', 0))

        with col2:
            st.metric("Processing Time", summary.get('processing_time', 'N/A'))

        with col3:
            st.metric("Data Sources", len(summary.get('data_sources_used', [])))

        with col4:
            st.metric("Operations", len(summary.get('operations_performed', [])))

    # Output files
    if 'output_files' in results:
        st.subheader("📁 Download Results")

        for file_info in results['output_files']:
            col_file1, col_file2, col_file3 = st.columns([2, 1, 1])

            with col_file1:
                st.write(f"**{file_info['type'].upper()}** - {file_info['size']}")

            with col_file2:
                st.button(f"📥 Download", key=f"download_{file_info['type']}")

            with col_file3:
                st.button(f"👁️ Preview", key=f"preview_{file_info['type']}")

    # Detailed results
    with st.expander("🔍 Detailed Results", expanded=False):
        st.json(results)


# Example queries section
st.sidebar.markdown("---")
st.sidebar.subheader("💡 Example Queries")

example_queries = [
    "Find all schools within 1km of hospitals in Mumbai",
    "Calculate population density by district using census data",
    "Identify flood-prone areas using elevation and rainfall data",
    "Generate land use classification from satellite imagery",
    "Locate all parks near metro stations in Delhi"
]

for i, example in enumerate(example_queries):
    if st.sidebar.button(f"📝 Use Example {i + 1}", key=f"example_{i}"):
        st.session_state.current_query = example
        st.rerun()

if __name__ == "__main__":
    main()