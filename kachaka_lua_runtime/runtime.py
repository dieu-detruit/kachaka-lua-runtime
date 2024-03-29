import logging
import time

from lupa.lua53 import LuaError, LuaRuntime, LuaSyntaxError  # type: ignore
from kachaka_api import KachakaApiClient

logger = logging.getLogger(__name__)

class KachakaLuaRuntime:
    def __init__(self, kachaka_api_client: KachakaApiClient) -> None:
        self._kachaka_api_client = kachaka_api_client
        self._lua = self._create_runtime()

    def run_script(self, lua_script: str) -> None:
        self._kachaka_api_client.update_resolver()
        try:
            self._lua.execute(lua_script)
        except LuaSyntaxError as e:
            logger.warning(f"failed to describe script for LuaSyntaxError: {e}")
        except LuaError as e:
            logger.warning(f"failed to describe script for LuaError: {e}")

    def _create_runtime(self) -> LuaRuntime:
        lua = LuaRuntime(unpack_returned_tuples=True)

        lua.globals().move_shelf = self._move_shelf
        lua.globals().return_shelf = self._return_shelf
        lua.globals().dock_shelf = self._dock_shelf
        lua.globals().undock_shelf = self._undock_shelf
        lua.globals().move_to_location = self._move_to_location
        lua.globals().return_home = self._return_home
        lua.globals().speak = self._speak
        
        lua.globals().get_location_list = self._get_location_list
        lua.globals().get_shelf_list = self._get_location_list
        
        lua.globals().sleep = self._sleep

        return lua

    # action apis
    def _move_shelf(self, shelf_name_or_id: str, location_name_or_id: str) -> bool:
        result = self._kachaka_api_client.move_shelf(shelf_name_or_id, location_name_or_id)
        return result.success

    def _return_shelf(self, shelf_name_or_id: str) -> bool:
        result = self._kachaka_api_client.return_shelf(shelf_name_or_id)
        return result.success

    def _dock_shelf(self) -> bool:
        result = self._kachaka_api_client.dock_shelf()
        return result.success

    def _undock_shelf(self) -> bool:
        result = self._kachaka_api_client.undock_shelf()
        return result.success

    def _move_to_location(self, location_name_or_id: str) -> bool:
        result = self._kachaka_api_client.move_to_location(location_name_or_id)
        return result.success

    def _return_home(self) -> bool:
        result = self._kachaka_api_client.return_home()
        return result.success

    def _speak(self, text: str) -> bool:
        result = self._kachaka_api_client.speak(text)
        return result.success

    # state acquisition api
    def _get_location_list(self) -> dict[str, str]:
        locations = self._kachaka_api_client.get_locations()
        return {location.id: location.name  for location in locations}
    
    def _get_shelf_list(self) -> dict[str, str]:
        shelves = self._kachaka_api_client.get_shelves()
        return {shelf.id: shelf.name  for shelf in shelves}

    # utility apis
    def _sleep(self, duration_sec: float) -> None:
        time.sleep(duration_sec)

