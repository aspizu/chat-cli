import asyncio

from dotenv import load_dotenv

from .app import App

load_dotenv()
app = App()

try:
    asyncio.run(app.run())
except KeyboardInterrupt:
    pass
