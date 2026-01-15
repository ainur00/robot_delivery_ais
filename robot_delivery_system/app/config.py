class Settings:
    DB_HOST = "192.168.56.104"
    DB_PORT = "3306"
    DB_USER = "robot_app"
    DB_PASSWORD = "strong_password_here" 
    DB_NAME = "robot_delivery_db"
    
    @property
    def DATABASE_URL(self):
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

# Создаем экземпляр настроек
settings = Settings()