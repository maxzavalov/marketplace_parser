import threading
import time
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from models import TrackedProduct
from database import Database
from parsers import WildberriesParser, OzonParser
from config import SCHEDULER_CONFIG
import telebot

class PriceTrackerScheduler:
    def __init__(self, bot: telebot.TeleBot):
        self.bot = bot
        self.db = Database()
        self.scheduler = BackgroundScheduler()
        self.wb_parser = WildberriesParser()
        self.ozon_parser = OzonParser()
        self.is_running = False