from fastapi import APIRouter
from pydantic import BaseModel
from model.quantum_model import QuantumModel
from model.video_model import VideoModel

router = APIRouter()
quantum_model = QuantumModel()
video_model = VideoModel()

class QuantumStateRequest(BaseModel):
    amplitudes: list
    basis_states: list

class LOCCOperationRequest(BaseModel):
    party_index: int
    qudit_index: int
    operation_type: str
    operator_choice: str
    condition: list | None = None

class ExecutionTypeRequest(BaseModel):
    execution_type: str

@router.post("/create_state")
def create_state(req: QuantumStateRequest):
    result = quantum_model.create_quantum_state(req.amplitudes, req.basis_states)
    return {"message": result}

@router.post("/add_locc_operation")
def add_locc_operation(req: LOCCOperationRequest):
    result = quantum_model.save_locc_operation(
        req.party_index, req.qudit_index,
        req.operation_type, req.operator_choice,
        req.condition
    )
    return {"message": result}

@router.post("/set_execution_type")
def set_execution_type(req: ExecutionTypeRequest):
    quantum_model.save_execution_type(req.execution_type)
    return {"message": f"Execution type set to {req.execution_type}"}

@router.post("/generate_video")
def generate_video():
    locc, kparty, exectype = quantum_model.get_input_for_video()
    path = video_model.generate_video(locc, kparty, exectype, output_path="backend/static/manim_output.mp4")
    return {"video_url": "/static/manim_output.mp4"}
