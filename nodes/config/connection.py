"""Supabase Connection node."""

from comfy_api.latest import io

from ...core.client import SupabaseClientManager

# Define custom types
SupabaseClientType = io.Custom("SUPABASE_CLIENT")


class SupabaseConnection(io.ComfyNode):
    """
    Creates a Supabase client connection.
    """

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="SupabaseConnection",
            display_name="Supabase Connection",
            description="Create a Supabase client connection",
            category="Supabase/Config",
            inputs=[
                io.String.Input(
                    id="url",
                    display_name="Project URL",
                    tooltip="Your Supabase project URL (e.g., https://xxx.supabase.co)",
                ),
                io.String.Input(
                    id="key",
                    display_name="API Key",
                    tooltip="Your anon or service_role key from Project Settings > API",
                ),
                io.Boolean.Input(
                    id="validate",
                    display_name="Validate Connection",
                    default=True,
                    tooltip="Test the connection on creation",
                ),
            ],
            outputs=[
                SupabaseClientType.Output(id="client"),
                io.Boolean.Output(id="is_service_role"),
                io.String.Output(id="error"),
            ],
        )

    @classmethod
    def execute(cls, url: str, key: str, validate: bool = True) -> io.NodeOutput:
        error = ""

        # Validate credentials format
        is_valid, validation_error = SupabaseClientManager.validate_credentials(url, key)
        if not is_valid:
            return io.NodeOutput(None, False, validation_error)

        try:
            # Create client
            wrapper = SupabaseClientManager.get_or_create(url.strip(), key.strip())

            # Optionally validate by making a simple request
            if validate:
                # Try to fetch from a non-existent table - will fail with 404 but proves auth works
                try:
                    wrapper.client.table("__connection_test__").select("*").limit(1).execute()
                except Exception as e:
                    error_str = str(e)
                    # 404 is expected (table doesn't exist), auth errors are not
                    if "JWT" in error_str or "Invalid API key" in error_str:
                        return io.NodeOutput(None, False, f"Authentication failed: {error_str}")
                    # Other errors (like 404) are fine - it means auth worked

            return io.NodeOutput(wrapper, wrapper.is_service_role, error)

        except Exception as e:
            return io.NodeOutput(None, False, str(e))
