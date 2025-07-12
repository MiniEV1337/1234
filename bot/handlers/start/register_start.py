from .start import router as start_router

def register_start(dp):
    dp.include_router(start_router)
