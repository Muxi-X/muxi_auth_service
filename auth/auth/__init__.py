from flask import Blueprint

auth = Blueprint(
        'auth',
        __name__ ,
)

from . import  login,  signup, profile
