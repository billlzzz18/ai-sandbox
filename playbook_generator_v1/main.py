import google.generativeai as genai
import os
import json
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

from google.generativeai.types import Tool

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("Please set the GEMINI_API_KEY environment variable.")

genai.configure(api_key=GEMINI_API_KEY)

# Define the base model
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config={"temperature": 0.1}
)

print("Gemini API configured successfully.")
print(f"Model {model.model_name} ready.")

# Mock storage
session_memory: Dict[str, str] = {}
file_system_mock: Dict[str, Dict[str, Any]] = {}
playbook_storage: Dict[str, List[Dict[str, Any]]] = {}

# Tool Functions (Mock implementations)
def Tool_Think_And_Plan(goal: str, context: str, constraints: List[str]) -> Dict[str, Any]:
    """
    Tool for thinking, planning, and analyzing before taking action.
    AI is forced to call this first.
    """
    print(f"--- [TOOL CALL: Think_And_Plan] ---")
    print(f"GOAL: {goal}")
    print(f"CONTEXT: {context[:100]}...")
    print(f"CONSTRAINTS: {constraints}")
    
    mock_plan = {
        "reasoning": f"AI is analyzing goal '{goal}' under constraints {constraints}",
        "step_by_step_plan": [
            "Step 1: Understand dependencies based on context.",
            "Step 2: Identify which tools are needed.",
            "Step 3: Define output artifacts."
        ]
    }
    print("---------------------------------------")
    return mock_plan

def Memory_Write(key: str, value: str) -> Dict[str, Any]:
    """Write data to session memory."""
    print(f"--- [TOOL CALL: Memory_Write] ---")
    session_memory[key] = value
    print(f"OK: Wrote '{key}' to memory")
    print("-----------------------------------")
    return {"status": "success", "key": key}

def Memory_Read(key: str) -> Dict[str, Any]:
    """Read data from session memory."""
    print(f"--- [TOOL CALL: Memory_Read] ---")
    value = session_memory.get(key, None)
    if value:
        print(f"OK: Read '{key}' from memory (Value: {value[:50]}...)")
    else:
        print(f"WARN: Key '{key}' not found in memory")
    print("----------------------------------")
    return {"key": key, "value": value}

def File_Write(path: str, content: str, template_id: str) -> Dict[str, Any]:
    """
    Write content to a file using a specified template.
    """
    print(f"--- [TOOL CALL: File_Write] ---")
    print(f"PATH: {path}")
    print(f"TEMPLATE_ID: {template_id}")

    if template_id == "Template_Bl1nk_Canvas_v1":
        print("DETECTED: Canvas JSON")
        try:
            json.loads(content)
            print("STATUS: Valid JSON")
            print(f"CONTENT:\n{content}")
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in Canvas content! {e}")
            return {"status": "error", "message": str(e)}

    elif template_id == "Template_Markdown_Report_v1":
        print("DETECTED: Markdown Report")
        print(f"CONTENT (Preview):\n{content[:200]}...")

    elif template_id == "Template_Python_Script_v1":
        print("DETECTED: Python Script")
        print(f"CONTENT (Preview):\n{content[:200]}...")

    else:
        print(f"DETECTED: Generic File ({template_id})")
        print(f"CONTENT (Preview):\n{content[:200]}...")

    # Write to actual file system
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ FILE WRITTEN: {path}")
    except Exception as e:
        print(f"❌ FILE WRITE ERROR: {e}")
        return {"status": "error", "message": str(e)}

    file_system_mock[path] = {"content": content, "template": template_id}
    print("-------------------------------")
    return {"status": "success", "path": path}

def File_Read(path: str) -> Dict[str, Any]:
    """Read file content (mock)."""
    print(f"--- [TOOL CALL: File_Read] ---")
    data = file_system_mock.get(path, None)
    if data:
        print(f"OK: Read '{path}'")
        return {"status": "success", "content": data['content'], "template": data['template']}
    else:
        print(f"ERROR: File '{path}' not found")
        return {"status": "error", "message": f"File not found: {path}"}

def Knowledge_Base_Search(query: str, knowledge_base_id: str = "default") -> Dict[str, Any]:
    """Search knowledge base (RAG mock)."""
    print(f"--- [TOOL CALL: Knowledge_Base_Search] ---")
    print(f"QUERY: {query}")
    print(f"KB_ID: {knowledge_base_id}")
    mock_chunks = [
        {"source": "doc1.pdf", "chunk": f"Mock data related to '{query}'..."},
        {"source": "doc2.md", "chunk": f"Another piece of data for '{query}'..."},
    ]
    print(f"OK: Found {len(mock_chunks)} chunks")
    print("----------------------------------------")
    return {"status": "success", "chunks": mock_chunks}

def Data_Table_Search(json_data: str, query_logic: str) -> Dict[str, Any]:
    """Search JSON table data (mock)."""
    print(f"--- [TOOL CALL: Data_Table_Search] ---")
    print(f"QUERY_LOGIC: {query_logic}")
    try:
        data_len = len(json.loads(json_data))
        print(f"OK: Searching mock table ({data_len} rows)")
        mock_results = [
            {"row_index": 120, "error_type": "Mismatch", "details": "..."},
            {"row_index": 750, "error_type": "NullValue", "details": "..."},
        ]
        print(f"OK: Found {len(mock_results)} matching items (fast)")
        print("--------------------------------------")
        return {"status": "success", "matching_rows": mock_results}
    except Exception as e:
        print(f"ERROR: Cannot parse JSON data: {e}")
        return {"status": "error", "message": str(e)}

def Code_Runner_Python(code: str, allowed_libraries: List[str]) -> Dict[str, Any]:
    """Run Python code in sandbox (mock)."""
    print(f"--- [TOOL CALL: Code_Runner_Python] ---")
    print(f"ALLOWED_LIBS: {allowed_libraries}")
    print(f"CODE_TO_RUN:\n{code}")
    mock_result = {"simulation_output": "Data processed", "artifacts_generated": ["/tmp/graph.png"]}
    print(f"OK: (Mock) Code executed successfully")
    print("---------------------------------------")
    return {"status": "success", "result": mock_result, "logs": "Running simulation...\nDone."}

def Template_Save_As_Playbook(playbook_name: str, tool_call_sequence: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Save successful tool call sequence as playbook (mock)."""
    print(f"--- [TOOL CALL: Template_Save_As_Playbook] ---")
    playbook_storage[playbook_name] = tool_call_sequence
    new_template_id = f"PLAYBOOK_{playbook_name.upper()}"
    print(f"OK: Saved playbook '{playbook_name}' ({len(tool_call_sequence)} steps)")
    print(f"NEW_TEMPLATE_ID: {new_template_id}")
    print("----------------------------------------------")
    return {"status": "success", "new_template_id": new_template_id}

# Available tools dict for manual calling
available_tools = {
    "Tool_Think_And_Plan": Tool_Think_And_Plan,
    "Memory_Write": Memory_Write,
    "Memory_Read": Memory_Read,
    "File_Write": File_Write,
    "File_Read": File_Read,
    "Knowledge_Base_Search": Knowledge_Base_Search,
    "Data_Table_Search": Data_Table_Search,
    "Code_Runner_Python": Code_Runner_Python,
    "Template_Save_As_Playbook": Template_Save_As_Playbook,
}

# Define Tool schemas for Gemini function calling
from google.generativeai import protos
from google.generativeai.types import Tool

def create_tool_schema(name: str, description: str, parameters: Dict[str, Any], required: List[str]) -> Tool:
    prop_schemas = {}
    for param_name, param_schema in parameters.items():
        if param_schema["type"] == "string":
            prop_schemas[param_name] = protos.Schema(type=protos.Type.STRING, description=param_schema.get("description", ""))
        elif param_schema["type"] == "array":
            items_type = param_schema["items"]["type"]
            if items_type == "string":
                prop_schemas[param_name] = protos.Schema(
                    type=protos.Type.ARRAY,
                    items=protos.Schema(type=protos.Type.STRING)
                )
            elif items_type == "object":
                prop_schemas[param_name] = protos.Schema(
                    type=protos.Type.ARRAY,
                    items=protos.Schema(
                        type=protos.Type.OBJECT,
                        properties={
                            "tool": protos.Schema(type=protos.Type.STRING),
                            "args": protos.Schema(type=protos.Type.OBJECT),
                            "result_preview": protos.Schema(type=protos.Type.STRING)
                        }
                    )
                )
        elif param_schema["type"] == "object":
            prop_schemas[param_name] = protos.Schema(type=protos.Type.OBJECT)

    params_schema = protos.Schema(
        type=protos.Type.OBJECT,
        properties=prop_schemas,
        required=required
    )

    func_decl = protos.FunctionDeclaration(
        name=name,
        description=description,
        parameters=params_schema
    )

    return Tool(function_declarations=[func_decl])

# Create tools list
tools_for_gemini = [
    create_tool_schema(
        "Tool_Think_And_Plan",
        "Tool for thinking, planning, and analyzing before taking action. AI must call this first.",
        {
            "goal": {"type": "string", "description": "The goal"},
            "context": {"type": "string", "description": "The context"},
            "constraints": {"type": "array", "items": {"type": "string"}}
        },
        ["goal", "context", "constraints"]
    ),
    create_tool_schema(
        "Memory_Write",
        "Write data to session memory.",
        {
            "key": {"type": "string"},
            "value": {"type": "string"}
        },
        ["key", "value"]
    ),
    create_tool_schema(
        "Memory_Read",
        "Read data from session memory.",
        {
            "key": {"type": "string"}
        },
        ["key"]
    ),
    create_tool_schema(
        "File_Write",
        "Write content to a file using a template.",
        {
            "path": {"type": "string"},
            "content": {"type": "string"},
            "template_id": {"type": "string"}
        },
        ["path", "content", "template_id"]
    ),
    create_tool_schema(
        "File_Read",
        "Read file content.",
        {
            "path": {"type": "string"}
        },
        ["path"]
    ),
    create_tool_schema(
        "Knowledge_Base_Search",
        "Search knowledge base.",
        {
            "query": {"type": "string"},
            "knowledge_base_id": {"type": "string", "description": "Default: 'default'"}
        },
        ["query"]
    ),
    create_tool_schema(
        "Data_Table_Search",
        "Search JSON table data.",
        {
            "json_data": {"type": "string"},
            "query_logic": {"type": "string"}
        },
        ["json_data", "query_logic"]
    ),
    create_tool_schema(
        "Code_Runner_Python",
        "Run Python code in sandbox.",
        {
            "code": {"type": "string"},
            "allowed_libraries": {"type": "array", "items": {"type": "string"}}
        },
        ["code", "allowed_libraries"]
    ),
    create_tool_schema(
        "Template_Save_As_Playbook",
        "Save tool call sequence as playbook.",
        {
            "playbook_name": {"type": "string"},
            "tool_call_sequence": {"type": "array", "items": {"type": "object"}}
        },
        ["playbook_name", "tool_call_sequence"]
    )
]

# Model with tools
model_with_tools = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    tools=tools_for_gemini,
    generation_config={"temperature": 0.1}
)

def run_orchestrator(initial_prompt: str, role_definition: str) -> Optional[List[Dict[str, Any]]]:
    """
    Main function to run the role and manage tool calling loop.
    """
    print(f"\n=======================================================")
    print(f"🎬 STARTING ORCHESTRATOR")
    print(f"ROLE: {role_definition}")
    print(f"=======================================================")

    chat = model_with_tools.start_chat(enable_automatic_function_calling=False)
    
    full_prompt = f"SYSTEM_ROLE: {role_definition}\n\nUSER_REQUEST: {initial_prompt}"
    
    try:
        response = chat.send_message(full_prompt)
        tool_call_sequence: List[Dict[str, Any]] = []
        
        max_turns = 20
        turn_count = 0
        
        while turn_count < max_turns:
            turn_count += 1
            
            candidate = response.candidates[0]
            if not candidate.content.parts or not candidate.content.parts[0].function_call:
                print("\n✅ AI: (No tool call - thinking or summarizing)")
                if candidate.content.parts:
                    print(candidate.content.parts[0].text)
                if "เสร็จสิ้น" in (candidate.content.parts[0].text if candidate.content.parts else ""):
                    break
                response = chat.send_message("ดำเนินการต่อตามแผน")
                continue

            fc = candidate.content.parts[0].function_call
            function_name = fc.name
            function_args = dict(fc.args)
            
            print(f"\n🤖 AI -> [CALLING: {function_name}]")
            
            if function_name in available_tools:
                tool_function = available_tools[function_name]
                
                try:
                    function_result = tool_function(**function_args)
                    tool_call_sequence.append({
                        "tool": function_name,
                        "args": function_args,
                        "result_preview": str(function_result)[:50]
                    })

                    response = chat.send_message(
                        genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=function_name,
                                response={"result": function_result}
                            )
                        )
                    )
                except Exception as e:
                    print(f"🔥 ERROR executing {function_name}: {e}")
                    response = chat.send_message(
                        genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=function_name,
                                response={"error": str(e)}
                            )
                        )
                    )
            else:
                print(f"🔥 ERROR: Unknown tool: {function_name}")
                break
                
        print(f"\n=======================================================")
        print(f"🏁 ORCHESTRATOR FINISHED (Turns: {turn_count})")
        print(f"=======================================================")
        
        return tool_call_sequence

    except Exception as e:
        print(f"\n🔥🔥🔥 CRITICAL ERROR: {e}")
        return None

# Load Plans (abbreviated)
PLAN_1_TEXT = """
(นี่คือเนื้อหาจาก "โปรเจกต์ที่ 1: แพลตฟอร์มข่าวกรองข้อมูลฯ")
เป้าหมาย: สร้าง MVP แพลตฟอร์ม BI แบบเรียลไทม์
Tech Stack: Kafka, TimescaleDB, PySpark, Mistral 7B, SHAP, Plotly Dash
พรอมต์ AI ที่ต้องทำ:
1. Task Decomposition: "As a user, I want to create a real-time dashboard..."
2. Test-Driven Development: "Write unit tests for `create_timeseries_graph`..."
3. Daily Stand-up Summary: "Summarize Git commit logs..."
"""

PLAN_2_TEXT = """
(นี่คือเนื้อหาจาก "โปรเจกต์ที่ 2: แพลตฟอร์มการบำรุงรักษาเชิงคาดการณ์ฯ")
เป้าหมาย: สร้าง MVP แพลตฟอร์มคาดการณ์ความล้มเหลวของเครื่องจักร
Tech Stack: Kafka, TimescaleDB, Scikit-learn, TensorFlow, Plotly Dash
พรอมต์ AI ที่ต้องทำ:
1. Feature Engineering: "propose new engineered features for industrial pumps..."
2. API Design: "Design a RESTful API endpoint for real-time sensor data..."
3. Automated Documentation: "Generate OpenAPI documentation for RUL endpoint..."
"""

PLAN_3_TEXT = """
(นี่คือเนื้อหาจาก "โปรเจกต์ที่ 3: แพลตฟอร์มข่าวกรองด้านความปลอดภัยฯ")
เป้าหมาย: สร้าง MVP แพลตฟอร์ม SIEM สมัยใหม่
Tech Stack: Kafka, S3, OpenSearch, Python ML (UEBA)
พรอมต์ AI ที่ต้องทำ:
1. Detection Rule Generation: "create a detection rule for 'password spraying'..."
2. Incident Triage: "generate a checklist for 'malicious IP' alert..."
3. Executive Summary Generation: "Summarize a phishing incident..."
"""

print("Loaded 3 project plans (abbreviated).")

# Test functions
def run_test_1():
    print("\n\n<<<<< STARTING TEST 1: Real-time Data Intelligence >>>>>")
    role_1 = "คุณคือ IT Project Manager (Role: ROLE-ASA-001) หน้าที่ของคุณคือแปลงแผนงานให้เป็น Artifacts ที่จับต้องได้โดยใช้เครื่องมือที่มีให้เท่านั้น"
    prompt_1 = f"""
นี่คือแผนงาน: {PLAN_1_TEXT}
จงเริ่มต้นทำงานตามแผนทันที โดยต้องเรียก `Tool_Think_And_Plan` ก่อนเสมอ
จากนั้น ดำเนินการสร้าง Artifacts ทั้ง 3 อย่าง (Task Decomposition, Unit Tests, Stand-up Summary) โดยใช้ `Tool_File_Write` แยกกันในแต่ละไฟล์
เมื่อสร้างครบ 3 ไฟล์ ให้ตอบว่า 'เสร็จสิ้นแผนงานที่ 1'
"""
    return run_orchestrator(initial_prompt=prompt_1, role_definition=role_1)

def run_test_2():
    print("\n\n<<<<< STARTING TEST 2: Predictive Maintenance >>>>>")
    role_2 = "คุณคือ Data Scientist (Role: ROLE-DSC-008) หน้าที่ของคุณคือสร้างเอกสารทางเทคนิคและโค้ดต้นแบบตามแผนงาน โดยใช้เครื่องมือที่มีให้เท่านั้น"
    prompt_2 = f"""
นี่คือแผนงาน: {PLAN_2_TEXT}
จงเริ่มต้นทำงานตามแผนทันที โดยต้องเรียก `Tool_Think_And_Plan` ก่อน
จากนั้น ดำเนินการสร้าง Artifacts ทั้ง 3 อย่าง (Feature Engineering, API Design, Auto-Documentation) โดยใช้ `Tool_File_Write`
(API Design ควรใช้ Template 'Template_Bl1nk_Canvas_v1' เพื่อสร้าง JSON Diagram
และ Auto-Documentation ควรใช้ 'Template_Markdown_Report_v1')
เมื่อสร้างครบ 3 ไฟล์ ให้ตอบว่า 'เสร็จสิ้นแผนงานที่ 2'
"""
    return run_orchestrator(initial_prompt=prompt_2, role_definition=role_2)

def run_test_3():
    print("\n\n<<<<< STARTING TEST 3: Advanced Security >>>>>")
    role_3 = "คุณคือ Security Analyst (Role: ROLE-SEG-004) หน้าที่ของคุณคือสร้างกฎและรายงานด้านความปลอดภัยตามแผนงาน โดยใช้เครื่องมือที่มีให้เท่านั้น"
    prompt_3 = f"""
นี่คือแผนงาน: {PLAN_3_TEXT}
จงเริ่มต้นทำงานตามแผนทันที โดยต้องเรียก `Tool_Think_And_Plan` ก่อน
จากนั้น ดำเนินการสร้าง Artifacts ทั้ง 3 อย่าง (Detection Rule, Triage Checklist, Executive Summary) โดยใช้ `Tool_File_Write`
(Triage Checklist และ Executive Summary ควรใช้ 'Template_Markdown_Report_v1')
เมื่อสร้างครบ 3 ไฟล์ ให้ตอบว่า 'เสร็จสิ้นแผนงานที่ 3'
"""
    return run_orchestrator(initial_prompt=prompt_3, role_definition=role_3)

# Summary and Playbook creation
def final_review():
    print("\n\n<<<<< FINAL REVIEW & PLAYBOOK CREATION >>>>>")
    print("\n--- Summary of created files (mock) ---")
    print(json.dumps(file_system_mock, indent=2, ensure_ascii=False))

    # Assume Test 3 is the best
    sequence_3 = run_test_3()  # Run if not already
    if sequence_3:
        print("\n--- Saving TEST 3 as Playbook ---")
        playbook_result = Template_Save_As_Playbook(
            playbook_name="Security_Incident_Triage",
            tool_call_sequence=sequence_3
        )
        print(f"Save result: {playbook_result}")
        
        print("\n--- Saved Playbooks ---")
        # Convert protobuf objects to dict for JSON serialization
        serializable_playbooks = {}
        for name, sequence in playbook_storage.items():
            serializable_sequence = []
            for step in sequence:
                serializable_step = {}
                for k, v in step.items():
                    if hasattr(v, 'name'):  # protobuf object
                        serializable_step[k] = str(v)
                    elif isinstance(v, dict):
                        serializable_step[k] = v  # Already dict
                    else:
                        serializable_step[k] = str(v)  # Convert to string
                serializable_sequence.append(serializable_step)
            serializable_playbooks[name] = serializable_sequence
        print(json.dumps(serializable_playbooks, indent=2, ensure_ascii=False))
    else:
        print("\n--- Cannot save Playbook (TEST 3 failed) ---")

# Run all tests if script executed directly
if __name__ == "__main__":
    sequence_1 = run_test_1()
    sequence_2 = run_test_2()
    # sequence_3 already in final_review, but call tests
    final_review()