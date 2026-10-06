from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    app_name:str="AI Chart Analyzer"; environment:str="development"; secret_key:str="change-this-secret"
    database_url:str="sqlite:///./chart_analyzer.db"; cors_origins:str="http://127.0.0.1:8000,http://localhost:8000"
    binance_base_url:str="https://api.binance.com"
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")
    @property
    def cors_list(self): return [x.strip() for x in self.cors_origins.split(",") if x.strip()]
settings=Settings()
