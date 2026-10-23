from pydantic_settings import BaseSettings,SettingsConfigDict
class Settings(BaseSettings):
    app_name:str="SmartRetail Vision"
    secret_key:str="development-change-me"
    database_url:str="sqlite:///./smartretail.db"
    yolo_model:str="yolo11n.pt"; yolo_confidence:float=.35; yolo_iou:float=.70
    yolo_device:str="auto"; yolo_image_size:int=640; yolo_tracker:str="bytetrack.yaml"
    log_dir:str="logs"; log_level:str="INFO"   # bitácora (equivalente a LogBack)
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")
settings=Settings()
