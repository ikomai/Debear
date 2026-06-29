"""Aggregate all routers for easy inclusion in the dispatcher."""
from aiogram import Router

from app.handlers import admin, application, common, my_apps


def get_main_router() -> Router:
    router = Router()
    # order matters: command/menu handlers first, FSM flow last
    router.include_router(common.router)
    router.include_router(my_apps.router)
    router.include_router(admin.router)
    router.include_router(application.router)
    return router
