"""
Natural Language Query Processor for GIS Operations
"""
import re
from typing import Dict, List, Optional
from langchain.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline


class GISQueryProcessor:
    """Process natural language queries for GIS operations"""

    def __init__(self, model_name: str = "mistralai/Mistral-7B-Instruct-v0.1"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.llm_pipeline = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the language model"""
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype="auto",
                device_map="auto"
            )

            # Create pipeline
            pipe = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                max_new_tokens=512,
                temperature=0.1
            )

            self.llm_pipeline = HuggingFacePipeline(pipeline=pipe)

        except Exception as e:
            print(f"Error initializing model: {e}")
            # Fallback to mock processor for development
            self.llm_pipeline = None

    def parse_query(self, query: str) -> Dict:
        """Parse natural language query into structured format"""

        # GIS operation patterns
        patterns = {
            'spatial_operations': [
                r'within\s+(\d+(?:\.\d+)?)\s*(km|m|miles?)',
                r'near|close to|around',
                r'intersect|overlap|contain',
                r'buffer|distance'
            ],
            'objects': [
                r'school[s]?', r'hospital[s]?', r'park[s]?', r'road[s]?',
                r'building[s]?', r'river[s]?', r'forest[s]?', r'city|cities'
            ],
            'locations': [
                r'Mumbai', r'Delhi', r'Bangalore', r'Chennai', r'Kolkata',
                r'India', r'district', r'state', r'village'
            ],
            'analysis_types': [
                r'calculate|compute', r'identify|find', r'generate|create',
                r'classify|categorize', r'density', r'area', r'count'
            ]
        }

        # Extract components
        result = {
            'original_query': query,
            'spatial_operation': self._extract_spatial_operation(query, patterns),
            'target_objects': self._extract_objects(query, patterns),
            'location': self._extract_location(query, patterns),
            'analysis_type': self._extract_analysis_type(query, patterns),
            'parameters': self._extract_parameters(query)
        }

        return result

    def generate_workflow(self, parsed_query: Dict) -> Dict:
        """Generate GIS workflow from parsed query"""

        if self.llm_pipeline:
            return self._generate_ai_workflow(parsed_query)
        else:
            return self._generate_template_workflow(parsed_query)

    def _generate_ai_workflow(self, parsed_query: Dict) -> Dict:
        """Generate workflow using AI model"""

        prompt_template = PromptTemplate(
            input_variables=["query", "components"],
            template="""
            Convert this GIS query into a step-by-step workflow:

            Query: {query}
            Parsed Components: {components}

            Generate a workflow with these steps:
            1. Data acquisition
            2. Preprocessing
            3. Spatial operations
            4. Analysis
            5. Output generation

            Workflow:
            """
        )

        prompt = prompt_template.format(
            query=parsed_query['original_query'],
            components=str(parsed_query)
        )

        try:
            response = self.llm_pipeline(prompt)
            return self._parse_workflow_response(response)
        except Exception as e:
            print(f"AI workflow generation failed: {e}")
            return self._generate_template_workflow(parsed_query)

    def _generate_template_workflow(self, parsed_query: Dict) -> Dict:
        """Generate workflow using template-based approach"""

        workflow = {
            'steps': [],
            'tools': [],
            'data_sources': [],
            'estimated_time': '2-5 minutes'
        }

        # Step 1: Data acquisition
        if 'school' in parsed_query['target_objects']:
            workflow['steps'].append({
                'step': 1,
                'action': 'Acquire school location data',
                'tool': 'OSM Overpass API',
                'parameters': {'amenity': 'school', 'location': parsed_query['location']}
            })
            workflow['data_sources'].append('OpenStreetMap')

        if 'hospital' in parsed_query['target_objects']:
            workflow['steps'].append({
                'step': 2,
                'action': 'Acquire hospital location data',
                'tool': 'OSM Overpass API',
                'parameters': {'amenity': 'hospital', 'location': parsed_query['location']}
            })

        # Step 2: Spatial operation
        if 'within' in parsed_query['spatial_operation']:
            distance = parsed_query['parameters'].get('distance', '1km')
            workflow['steps'].append({
                'step': 3,
                'action': f'Create {distance} buffer around hospitals',
                'tool': 'GeoPandas',
                'parameters': {'distance': distance, 'unit': 'km'}
            })

            workflow['steps'].append({
                'step': 4,
                'action': 'Find schools within buffer zones',
                'tool': 'PostGIS',
                'parameters': {'operation': 'spatial_intersect'}
            })

        # Step 3: Analysis and output
        workflow['steps'].append({
            'step': 5,
            'action': 'Generate result map and statistics',
            'tool': 'QGIS + Folium',
            'parameters': {'output_format': ['map', 'geojson', 'csv']}
        })

        workflow['tools'] = ['OSM API', 'GeoPandas', 'PostGIS', 'QGIS', 'Folium']

        return workflow

    def _extract_spatial_operation(self, query: str, patterns: Dict) -> str:
        """Extract spatial operation from query"""
        for pattern in patterns['spatial_operations']:
            if re.search(pattern, query, re.IGNORECASE):
                return pattern
        return 'proximity'

    def _extract_objects(self, query: str, patterns: Dict) -> List[str]:
        """Extract target objects from query"""
        objects = []
        for pattern in patterns['objects']:
            if re.search(pattern, query, re.IGNORECASE):
                objects.append(pattern.replace('[s]?', '').replace('\\', ''))
        return objects

    def _extract_location(self, query: str, patterns: Dict) -> str:
        """Extract location from query"""
        for pattern in patterns['locations']:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group()
        return 'India'

    def _extract_analysis_type(self, query: str, patterns: Dict) -> str:
        """Extract analysis type from query"""
        for pattern in patterns['analysis_types']:
            if re.search(pattern, query, re.IGNORECASE):
                return pattern
        return 'find'

    def _extract_parameters(self, query: str) -> Dict:
        """Extract numerical parameters from query"""
        params = {}

        # Extract distance
        distance_match = re.search(r'(\d+(?:\.\d+)?)\s*(km|m|miles?)', query, re.IGNORECASE)
        if distance_match:
            params['distance'] = distance_match.group(1)
            params['unit'] = distance_match.group(2)

        return params

    def _parse_workflow_response(self, response: str) -> Dict:
        """Parse AI model response into structured workflow"""
        # Implementation for parsing AI response
        # This would parse the model's text output into structured format
        return {'steps': [], 'tools': [], 'data_sources': []}


# Example usage
if __name__ == "__main__":
    processor = GISQueryProcessor()

    query = "Find all schools within 1km of hospitals in Mumbai"
    parsed = processor.parse_query(query)
    workflow = processor.generate_workflow(parsed)

    print("Parsed Query:", parsed)
    print("Generated Workflow:", workflow)