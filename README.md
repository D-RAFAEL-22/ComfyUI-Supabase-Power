# ComfyUI-Supabase-Power

A powerful node package for Supabase integration in ComfyUI. Provides 26 nodes covering Database, Storage, Realtime, Auth, and Edge Functions.

## Features

- **Modern API**: Uses the latest ComfyExtension API (2025+)
- **Full Supabase Coverage**: Database CRUD, Storage, Realtime subscriptions, Auth, Edge Functions
- **Chainable Builders**: FilterBuilder, OrderBy, JSONBuilder for composable queries
- **Type Safety**: Custom types (SUPABASE_CLIENT, FILTER_CHAIN, etc.)
- **Error Handling**: Built-in error handling with RLS-aware messages

## Installation

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/your-repo/comfyui-supabase-power
cd comfyui-supabase-power
pip install -r requirements.txt
```

## Nodes Overview

### Config (1 node)
| Node | Description |
|------|-------------|
| **SupabaseConnection** | Create a Supabase client connection |

### Database (6 nodes)
| Node | Description |
|------|-------------|
| **SupabaseSelect** | Query data with filters, ordering, pagination |
| **SupabaseInsert** | Insert new records |
| **SupabaseUpdate** | Update existing records (requires filters) |
| **SupabaseDelete** | Delete records (requires filters) |
| **SupabaseUpsert** | Insert or update on conflict |
| **SupabaseRPC** | Call PostgreSQL functions |

### Query Builder (3 nodes)
| Node | Description |
|------|-------------|
| **FilterBuilder** | Chainable WHERE conditions (eq, neq, like, in, etc.) |
| **OrderBy** | Chainable ORDER BY |
| **Pagination** | LIMIT/OFFSET or range-based pagination |

### Storage (5 nodes)
| Node | Description |
|------|-------------|
| **SupabaseUpload** | Upload IMAGE/AUDIO/BYTES with optional DB update |
| **SupabaseDownload** | Download files as IMAGE/AUDIO/BYTES/STRING |
| **SupabaseListFiles** | List files in a bucket |
| **SupabaseDeleteFile** | Delete files from storage |
| **SupabaseSignedURL** | Create temporary access URLs |

### Realtime (2 nodes)
| Node | Description |
|------|-------------|
| **SupabaseSubscribe** | Subscribe to database changes |
| **SupabaseBroadcast** | Send broadcast messages |

### Auth (2 nodes)
| Node | Description |
|------|-------------|
| **SupabaseSignIn** | Email/password authentication |
| **SupabaseUserInfo** | Get current user information |

### Edge Functions (1 node)
| Node | Description |
|------|-------------|
| **SupabaseEdgeFunction** | Invoke Edge Functions |

### Utils (3 nodes)
| Node | Description |
|------|-------------|
| **JSONBuilder** | Chainable JSON object construction |
| **ResponseParser** | Extract values from JSON with dot notation |
| **ErrorHandler** | Handle errors with fallbacks |

## Usage Examples

### Basic Select with Filters

```
[SupabaseConnection]
    → [FilterBuilder: column="status", op="eq", value="active"]
    → [FilterBuilder: column="price", op="gt", value="100"]
    → [SupabaseSelect: table="products", columns="id,name,price"]
    → [ResponseParser: path="0.name"]
```

### Upload Image and Update Database

```
[Image Generation]
    → [SupabaseUpload:
         bucket="images",
         update_table="generations",
         update_column="output_url",
         update_id_column="id",
         update_id_value="123"]
    → [SupabaseBroadcast:
         channel_name="notifications",
         event="image_ready"]
```

### Search by Name (ilike)

```
[SupabaseConnection]
    → [FilterBuilder: column="name", op="ilike", value="%chair%"]
    → [SupabaseSelect: table="assets", columns="id,name,usd_path"]
    → [ResponseParser: path="0.usd_path"]
```

## Custom Types

- `SUPABASE_CLIENT` - Supabase client wrapper
- `FILTER_CHAIN` - List of filter conditions
- `ORDER_CONFIG` - Ordering configuration
- `PAGINATION_CONFIG` - Pagination settings
- `REALTIME_CHANNEL` - Realtime channel wrapper
- `JSON` - Generic JSON data
- `LIST` - Generic list

## Security Notes

1. **Use service_role key carefully** - It bypasses RLS
2. **Prefer anon key** for client-facing workflows
3. **UPDATE/DELETE require filters** - Safety mechanism to prevent accidental mass changes
4. **Credentials in nodes** - Consider using environment variables in production

## Requirements

- ComfyUI with modern API support (2025+)
- Python 3.10+
- supabase>=2.0.0
- httpx>=0.25.0
- websockets>=12.0
- Pillow>=10.0.0
- numpy>=1.24.0

Пакет comfyui-supabase-power полностью создан. Вот итоговая структура:

  Созданный пакет: ComfyUI-Supabase-Power

  Структура (40 файлов):

  comfyui-supabase-power/
  ├── __init__.py                    # Async entrypoint (ComfyExtension)
  ├── pyproject.toml                 # Package config
  ├── requirements.txt               # Dependencies
  ├── README.md                      # Documentation
  │
  ├── core/
  │   ├── __init__.py
  │   ├── client.py                  # SupabaseClientManager
  │   ├── types.py                   # Custom types (SUPABASE_CLIENT, etc.)
  │   └── utils.py                   # Image conversion, query builders
  │
  ├── nodes/
  │   ├── __init__.py                # ALL_NODES export
  │   ├── config/
  │   │   └── connection.py          # SupabaseConnection
  │   ├── database/
  │   │   ├── select.py, insert.py, update.py
  │   │   ├── delete.py, upsert.py, rpc.py
  │   ├── query/
  │   │   ├── filter.py              # FilterBuilder (chainable)
  │   │   ├── order.py               # OrderBy (chainable)
  │   │   └── pagination.py          # Pagination
  │   ├── storage/
  │   │   ├── upload.py              # Upload with DB update
  │   │   ├── download.py, list_files.py
  │   │   ├── delete_file.py, signed_url.py
  │   ├── realtime/
  │   │   ├── subscribe.py           # SupabaseSubscribe
  │   │   └── broadcast.py           # SupabaseBroadcast
  │   ├── auth/
  │   │   ├── sign_in.py, user_info.py
  │   ├── edge/
  │   │   └── invoke.py              # SupabaseEdgeFunction
  │   └── utils/
  │       ├── json_builder.py        # JSONBuilder (chainable)
  │       ├── response_parser.py     # Path-based JSON extraction
  │       └── error_handler.py       # Error handling with fallbacks
  │
  └── web/js/
      └── supabase_nodes.js          # Frontend enhancements

  26 узлов:

  - Config: SupabaseConnection
  - Database (6): Select, Insert, Update, Delete, Upsert, RPC
  - Query Builder (3): FilterBuilder, OrderBy, Pagination
  - Storage (5): Upload, Download, ListFiles, DeleteFile, SignedURL
  - Realtime (2): Subscribe, Broadcast
  - Auth (2): SignIn, UserInfo
  - Edge (1): EdgeFunction
  - Utils (3): JSONBuilder, ResponseParser, ErrorHandler

  Особенности:

  - Современный ComfyExtension API (comfy_api.latest)
  - Chainable паттерн для фильтров, сортировки, JSON
  - Upload с автоматическим обновлением БД
  - Защита от случайного DELETE/UPDATE без фильтров
  - RLS-aware сообщения об ошибках


& "E:\WORK\ComfyUI_windows_portable\python_embeded\python.exe" -m pip install -r "E:\WORK\ComfyUI_windows_portable\ComfyUI\custom_nodes\СomfyUI-Supabase-Power\requirements.txt"

## License

MIT License
