"""Node modules for Supabase Power."""

from .config.connection import SupabaseConnection
from .query.filter import FilterBuilder
from .query.order import OrderBy
from .query.pagination import Pagination
from .database.select import SupabaseSelect
from .database.insert import SupabaseInsert
from .database.update import SupabaseUpdate
from .database.delete import SupabaseDelete
from .database.upsert import SupabaseUpsert
from .database.rpc import SupabaseRPC
from .storage.upload import SupabaseUpload
from .storage.download import SupabaseDownload
from .storage.list_files import SupabaseListFiles
from .storage.delete_file import SupabaseDeleteFile
from .storage.signed_url import SupabaseSignedURL
from .realtime.subscribe import SupabaseSubscribe
from .realtime.broadcast import SupabaseBroadcast
from .auth.sign_in import SupabaseSignIn
from .auth.user_info import SupabaseUserInfo
from .edge.invoke import SupabaseEdgeFunction
from .utils.json_builder import JSONBuilder
from .utils.response_parser import ResponseParser
from .utils.error_handler import ErrorHandler

ALL_NODES = [
    # Config
    SupabaseConnection,
    # Query Builder
    FilterBuilder,
    OrderBy,
    Pagination,
    # Database
    SupabaseSelect,
    SupabaseInsert,
    SupabaseUpdate,
    SupabaseDelete,
    SupabaseUpsert,
    SupabaseRPC,
    # Storage
    SupabaseUpload,
    SupabaseDownload,
    SupabaseListFiles,
    SupabaseDeleteFile,
    SupabaseSignedURL,
    # Realtime
    SupabaseSubscribe,
    SupabaseBroadcast,
    # Auth
    SupabaseSignIn,
    SupabaseUserInfo,
    # Edge Functions
    SupabaseEdgeFunction,
    # Utils
    JSONBuilder,
    ResponseParser,
    ErrorHandler,
]

__all__ = [node.__name__ for node in ALL_NODES] + ["ALL_NODES"]
