# backend/extensions.py
from data_sources.sqlite_source import Database
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# Apenas criamos as instâncias vazias
db = Database()
cors = CORS()
jwt = JWTManager()