from .climate import router as climate_router
from .missions import router as missions_router
from .cooling_spots import router as cooling_spots_router
from .agent import router as agent_router
from .effects import router as effects_router

__all__ = ["climate_router", "missions_router", "cooling_spots_router", "agent_router", "effects_router"]
