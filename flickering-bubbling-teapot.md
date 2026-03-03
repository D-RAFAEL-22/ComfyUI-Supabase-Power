# Plan: ComfyUI-Supabase-Power - Мощный пакет узлов для Supabase

## Обзор
Создание полнофункционального пакета узлов ComfyUI для работы с Supabase, использующего современный ComfyExtension API (2025+).

## Выбранные параметры
- **API стиль**: Современный ComfyExtension API (`comfy_api.latest`)
- **Scope**: Полный пакет (Database, Storage, Realtime, Auth, Edge Functions)
- **Credentials**: Поля в узлах подключения
- **Vector/AI**: Не включено в первую версию

---

## Структура пакета

```
comfyui-supabase-power/
├── __init__.py                    # Async entrypoint
├── requirements.txt
├── pyproject.toml
│
├── core/
│   ├── __init__.py
│   ├── client.py                  # SupabaseClientManager
│   ├── types.py                   # Кастомные типы (SUPABASE_CLIENT, FILTER_CHAIN, etc.)
│   └── utils.py                   # Конвертация изображений, обработка ошибок
│
├── nodes/
│   ├── __init__.py
│   ├── config/
│   │   └── connection.py          # SupabaseConnection
│   │
│   ├── database/
│   │   ├── select.py              # SupabaseSelect
│   │   ├── insert.py              # SupabaseInsert
│   │   ├── update.py              # SupabaseUpdate
│   │   ├── delete.py              # SupabaseDelete
│   │   ├── upsert.py              # SupabaseUpsert
│   │   └── rpc.py                 # SupabaseRPC
│   │
│   ├── query/
│   │   ├── filter.py              # FilterBuilder (chainable)
│   │   ├── order.py               # OrderBy
│   │   └── pagination.py          # Pagination
│   │
│   ├── storage/
│   │   ├── upload.py              # SupabaseUpload (IMAGE, AUDIO, BYTES)
│   │   ├── download.py            # SupabaseDownload
│   │   ├── list_files.py          # SupabaseListFiles
│   │   ├── delete_file.py         # SupabaseDeleteFile
│   │   └── signed_url.py          # SupabaseSignedURL
│   │
│   ├── realtime/
│   │   ├── subscribe.py           # SupabaseSubscribe
│   │   └── broadcast.py           # SupabaseBroadcast
│   │
│   ├── auth/
│   │   ├── sign_in.py             # SupabaseSignIn
│   │   └── user_info.py           # SupabaseUserInfo
│   │
│   ├── edge/
│   │   └── invoke.py              # SupabaseEdgeFunction
│   │
│   └── utils/
│       ├── json_builder.py        # JSONBuilder (chainable)
│       ├── response_parser.py     # ResponseParser
│       └── error_handler.py       # ErrorHandler
│
└── web/
    └── js/
        └── supabase_nodes.js      # WebSocket handlers
```

---

## Список узлов (26 узлов)

### Config (1)
| Узел | Inputs | Outputs | Описание |
|------|--------|---------|----------|
| **SupabaseConnection** | url, key | SUPABASE_CLIENT | Создание клиента |

### Database (6)
| Узел | Inputs | Outputs | Описание |
|------|--------|---------|----------|
| **SupabaseSelect** | client, table, columns?, filters?, order?, pagination?, single? | data (JSON), rows (LIST), count, error | Выборка данных |
| **SupabaseInsert** | client, table, data (JSON) | result, error, success | Вставка записей |
| **SupabaseUpdate** | client, table, data, filters | result, error, affected_rows | Обновление записей |
| **SupabaseDelete** | client, table, filters | deleted, error, count | Удаление записей |
| **SupabaseUpsert** | client, table, data, on_conflict? | result, error, success | Insert or Update |
| **SupabaseRPC** | client, function_name, params? | result, error | Вызов PostgreSQL функций |

### Query Builder (3)
| Узел | Inputs | Outputs | Описание |
|------|--------|---------|----------|
| **FilterBuilder** | column, operator, value, FILTER_CHAIN? | FILTER_CHAIN | Chainable фильтры (eq, neq, gt, lt, like, ilike, in, is, contains) |
| **OrderBy** | column, direction, ORDER_CONFIG? | ORDER_CONFIG | Chainable сортировка |
| **Pagination** | limit, offset?, range_start?, range_end? | PAGINATION_CONFIG | Пагинация |

### Storage (5)
| Узел | Inputs | Outputs | Описание |
|------|--------|---------|----------|
| **SupabaseUpload** | client, bucket, path, image?/audio?/bytes?, upsert?, update_table?, update_column? | public_url, path, error, success | Универсальный upload с опциональным обновлением БД |
| **SupabaseDownload** | client, bucket, path, output_type | IMAGE/AUDIO/BYTES/STRING | Скачивание файлов |
| **SupabaseListFiles** | client, bucket, folder?, limit?, offset? | files (LIST), count | Список файлов в bucket |
| **SupabaseDeleteFile** | client, bucket, path | success, error | Удаление файла |
| **SupabaseSignedURL** | client, bucket, path, expires_in | signed_url | URL для приватных файлов |

### Realtime (2)
| Узел | Inputs | Outputs | Описание |
|------|--------|---------|----------|
| **SupabaseSubscribe** | client, channel_name, table?, event_type?, filter? | channel, status | Подписка на изменения |
| **SupabaseBroadcast** | client, channel, event, payload | status, success | Отправка broadcast сообщений |

### Auth (2)
| Узел | Inputs | Outputs | Описание |
|------|--------|---------|----------|
| **SupabaseSignIn** | client, email, password | session, user, error | Аутентификация |
| **SupabaseUserInfo** | client | user (JSON), is_authenticated | Информация о пользователе |

### Edge Functions (1)
| Узел | Inputs | Outputs | Описание |
|------|--------|---------|----------|
| **SupabaseEdgeFunction** | client, function_name, body?, headers?, method?, timeout? | response, error, status_code, success | Вызов Edge Function |

### Utils (6)
| Узел | Inputs | Outputs | Описание |
|------|--------|---------|----------|
| **JSONBuilder** | key, value, JSON? | JSON | Chainable построение JSON |
| **ResponseParser** | data (JSON), path?, default? | value, as_string, as_int, as_float, as_bool, as_list | Парсинг ответов |
| **ErrorHandler** | input, error, fallback?, raise_on_error? | output, has_error, error_message | Обработка ошибок |

---

## Кастомные типы данных

```python
CUSTOM_TYPES = [
    "SUPABASE_CLIENT",   # Клиент Supabase
    "FILTER_CHAIN",      # Chainable фильтры
    "ORDER_CONFIG",      # Конфигурация сортировки
    "PAGINATION_CONFIG", # Конфигурация пагинации
    "REALTIME_CHANNEL",  # Realtime канал
]
```

---

## Ключевые паттерны реализации

### 1. ComfyExtension API (из example_node.py)
```python
from comfy_api.latest import ComfyExtension, io

class SupabaseConnection(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="SupabaseConnection",
            display_name="Supabase Connection",
            category="Supabase/Config",
            inputs=[
                io.String.Input("url", placeholder="https://xxx.supabase.co"),
                io.String.Input("key", placeholder="anon/service_role key"),
            ],
            outputs=[
                io.Custom.Output("SUPABASE_CLIENT", "client"),
            ],
        )
```

### 2. Chainable паттерн (из KeyValueNode)
```python
class FilterBuilder(io.ComfyNode):
    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="FilterBuilder",
            inputs=[
                io.String.Input("column"),
                io.Combo.Input("operator", options=["eq", "neq", "gt", "lt", "like", "ilike", "in", "is"]),
                io.String.Input("value"),
                io.Custom.Input("FILTER_CHAIN", "filters", optional=True),  # Chainable!
            ],
            outputs=[
                io.Custom.Output("FILTER_CHAIN", "filters"),
            ],
        )

    @classmethod
    def execute(cls, column, operator, value, filters=None):
        output = filters.copy() if filters else []
        output.append({"column": column, "op": operator, "value": value})
        return io.NodeOutput(output)
```

### 3. Storage Upload с DB Update (из upload_image.py)
```python
class SupabaseUpload(io.ComfyNode):
    @classmethod
    def execute(cls, client, bucket, path, image=None, update_table="", update_column="", update_id_column="", update_id_value=""):
        # 1. Конвертация IMAGE → PNG bytes
        # 2. Upload в Supabase Storage
        # 3. Получение public_url
        # 4. Опционально: UPDATE таблицы с URL
        if update_table and update_column and update_id_value:
            client.table(update_table).update({update_column: public_url}).eq(update_id_column, update_id_value).execute()
        return io.NodeOutput(public_url, path, error, success)
```

---

## Зависимости (requirements.txt)

```
supabase>=2.0.0
httpx>=0.25.0
websockets>=12.0
Pillow>=10.0.0
numpy>=1.24.0
```

---

## Примеры Workflow

### 1. Базовый CRUD
```
[SupabaseConnection] → [FilterBuilder eq:"status"="active"] → [SupabaseSelect table:"items"]
                                                                        ↓
                                                              [ResponseParser path:"0.name"]
```

### 2. Upload с обновлением БД (ваш use case)
```
[Image Generation] → [SupabaseUpload bucket:"images" update_table:"generations" update_column:"output_url"]
                              ↓
                    [SupabaseBroadcast channel:"generations" event:"completed"]
```

### 3. Поиск по названию для Isaac
```
[SupabaseConnection] → [FilterBuilder column:"name" op:"ilike" value:"%chair%"]
                              ↓
                       [SupabaseSelect table:"assets" columns:"id,name,usd_path"]
                              ↓
                       [ResponseParser path:"0.usd_path"]
                              ↓
                       [IsaacRenderNode usd_path:(parsed)]
```

---

## Порядок реализации

1. **Core** - types.py, client.py, utils.py
2. **Config** - SupabaseConnection
3. **Query Builder** - FilterBuilder, OrderBy, Pagination (нужны для Database)
4. **Utils** - JSONBuilder, ResponseParser, ErrorHandler
5. **Database** - Select, Insert, Update, Delete, Upsert, RPC
6. **Storage** - Upload, Download, ListFiles, DeleteFile, SignedURL
7. **Realtime** - Subscribe, Broadcast
8. **Auth** - SignIn, UserInfo
9. **Edge** - EdgeFunction
10. **Web** - JS handlers для WebSocket notifications

---

## Верификация

1. **Unit тесты**: Тестирование каждого узла изолированно
2. **Integration тесты**: Тестирование цепочек узлов
3. **Manual тесты в ComfyUI**:
   - Создать подключение к тестовому Supabase проекту
   - Протестировать CRUD операции
   - Протестировать Upload + DB update
   - Протестировать Realtime подписки
