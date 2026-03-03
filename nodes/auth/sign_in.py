"""Supabase SignIn node for user authentication."""

from comfy_api.latest import io

from ...core.types import SupabaseClientWrapper
from ...core.utils import format_error

# Custom types
SupabaseClientType = io.Custom("SUPABASE_CLIENT")
JsonType = io.Custom("JSON")


class SupabaseSignIn(io.ComfyNode):
    """Authenticate a user with Supabase Auth."""

    @classmethod
    def define_schema(cls) -> io.Schema:
        return io.Schema(
            node_id="SupabaseSignIn",
            display_name="Supabase Sign In",
            description="Authenticate user with email/password",
            category="Supabase/Auth",
            inputs=[
                SupabaseClientType.Input(id="client", tooltip="Supabase client"),
                io.String.Input(id="email", display_name="Email", tooltip="User email"),
                io.String.Input(id="password", display_name="Password", tooltip="User password"),
            ],
            outputs=[
                JsonType.Output(id="session"),
                JsonType.Output(id="user"),
                io.String.Output(id="access_token"),
                io.String.Output(id="error"),
                io.Boolean.Output(id="success"),
            ],
        )

    @classmethod
    def execute(cls, client: SupabaseClientWrapper, email: str, password: str) -> io.NodeOutput:
        try:
            response = client.client.auth.sign_in_with_password({"email": email, "password": password})

            session = None
            user = None
            access_token = ""

            if response.session:
                session = {
                    "access_token": response.session.access_token,
                    "refresh_token": response.session.refresh_token,
                    "expires_at": response.session.expires_at,
                    "token_type": response.session.token_type,
                }
                access_token = response.session.access_token

            if response.user:
                user = {
                    "id": response.user.id,
                    "email": response.user.email,
                    "created_at": response.user.created_at,
                    "role": response.user.role,
                }

            return io.NodeOutput(session, user, access_token, "", True)
        except Exception as e:
            return io.NodeOutput(None, None, "", format_error(e), False)
